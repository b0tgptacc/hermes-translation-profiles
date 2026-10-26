from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Iterable

import pymupdf

def resolve_translation_font() -> Path:
    candidates = [
        os.environ.get("HERMES_TRANSLATION_FONT", ""),
        r"C:/Windows/Fonts/msyh.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for value in candidates:
        if value and Path(value).is_file():
            return Path(value)
    raise FileNotFoundError(
        "No Cyrillic-capable translation font found. Set HERMES_TRANSLATION_FONT "
        "to a TTF/OTF/TTC path (Noto Sans CJK recommended)."
    )


def parse_pages(spec: str, page_count: int) -> list[int]:
    pages: list[int] = []
    for token in spec.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            start_s, end_s = token.split("-", 1)
            start, end = int(start_s), int(end_s)
            pages.extend(range(start, end + 1))
        else:
            pages.append(int(token))
    unique = []
    for p in pages:
        if p < 1 or p > page_count:
            raise ValueError(f"page {p} outside 1..{page_count}")
        if p not in unique:
            unique.append(p)
    if not unique:
        raise ValueError("no pages selected")
    return unique


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def cjk_count(text: str) -> int:
    return sum(1 for c in text if "\u3400" <= c <= "\u9fff")


def cyrillic_count(text: str) -> int:
    return sum(1 for c in text if "\u0400" <= c <= "\u04ff")


def save_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def inspect_pdf(source: Path) -> dict:
    doc = pymupdf.open(source)
    page_rows = []
    for i, page in enumerate(doc):
        text = page.get_text("text") or ""
        images = page.get_images(full=True)
        page_rows.append({
            "page": i + 1,
            "width": round(page.rect.width, 2),
            "height": round(page.rect.height, 2),
            "rotation": page.rotation,
            "chars": len(text.strip()),
            "cjk": cjk_count(text),
            "cyrillic": cyrillic_count(text),
            "blocks": len(page.get_text("blocks") or []),
            "images": len(images),
            "full_page_image_likely": bool(images),
        })
    all_have_images = all(row["images"] > 0 for row in page_rows)
    return {
        "source": str(source.resolve()),
        "sha256": sha256(source),
        "format": doc.metadata.get("format"),
        "encrypted": bool(doc.is_encrypted),
        "page_count": len(doc),
        "nonempty_text_pages": sum(row["chars"] > 0 for row in page_rows),
        "pages_with_images": sum(row["images"] > 0 for row in page_rows),
        "all_pages_have_images": all_have_images,
        "total_text_chars": sum(row["chars"] for row in page_rows),
        "total_cjk": sum(row["cjk"] for row in page_rows),
        "recommended_fidelity_class": "FACSIMILE" if all_have_images else "PDF_NATIVE_LAYOUT",
        "pages": page_rows,
    }


def render_page(page: pymupdf.Page, dpi: int = 150) -> pymupdf.Pixmap:
    scale = dpi / 72.0
    return page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), colorspace=pymupdf.csRGB, alpha=False)


def sample_pdf(source: Path, pages: Iterable[int], output: Path, render_dir: Path | None) -> dict:
    src = pymupdf.open(source)
    out = pymupdf.open()
    rows = []
    if render_dir:
        render_dir.mkdir(parents=True, exist_ok=True)
    for p in pages:
        out.insert_pdf(src, from_page=p - 1, to_page=p - 1)
        text = src[p - 1].get_text("text") or ""
        row = {"page": p, "chars": len(text.strip()), "cjk": cjk_count(text)}
        if render_dir:
            png = render_dir / f"source_page_{p:04d}.png"
            render_page(src[p - 1]).save(png)
            row["render"] = str(png.resolve())
        rows.append(row)
    output.parent.mkdir(parents=True, exist_ok=True)
    out.save(output, garbage=4, deflate=True)
    return {"output": str(output.resolve()), "sha256": sha256(output), "pages": rows}


def extract_units(source: Path, pages: Iterable[int]) -> dict:
    src = pymupdf.open(source)
    units = []
    for p in pages:
        page = src[p - 1]
        text = page.get_text("text") or ""
        blocks = []
        for idx, block in enumerate(page.get_text("blocks") or []):
            x0, y0, x1, y1, content, *_ = block
            content = " ".join((content or "").split())
            if content:
                blocks.append({
                    "unit_id": f"pdf:p{p}:b{idx}",
                    "bbox": [round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)],
                    "source": content,
                })
        units.append({
            "page": p,
            "source_text": text,
            "source_chars": len(text.strip()),
            "source_cjk": cjk_count(text),
            "blocks": blocks,
            "ocr_warning": "Text layer originates from OCR; verify against rendered source page.",
        })
    return {
        "source": str(source.resolve()),
        "source_sha256": sha256(source),
        "fidelity_class": "FACSIMILE",
        "target_language": "ru",
        "entries": units,
    }


def translation_entries(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("translations JSON needs non-empty entries[]")
    seen: set[int] = set()
    for entry in entries:
        page = int(entry["page"])
        text = str(entry.get("translation", "")).strip()
        if page in seen:
            raise ValueError(f"duplicate page {page}")
        if not text:
            raise ValueError(f"empty translation for page {page}")
        seen.add(page)
    return entries


def split_translation(text: str, max_chars: int = 2100) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for paragraph in paragraphs:
        parts = [paragraph]
        if len(paragraph) > max_chars:
            lines = [line.strip() for line in paragraph.splitlines() if line.strip()]
            parts = lines if len(lines) > 1 else [paragraph[i:i + max_chars] for i in range(0, len(paragraph), max_chars)]
        for part in parts:
            extra = len(part) + (2 if current else 0)
            if current and current_len + extra > max_chars:
                chunks.append("\n\n".join(current))
                current = []
                current_len = 0
            current.append(part)
            current_len += len(part) + (2 if current_len else 0)
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def add_translation_page(
    out: pymupdf.Document,
    size: pymupdf.Rect,
    source_page: int,
    text: str,
    part: int,
    parts_total: int,
) -> dict:
    page = out.new_page(width=size.width, height=size.height)
    fontfile = resolve_translation_font()
    fontname = "TranslationUnicode"
    page.insert_font(fontname=fontname, fontfile=str(fontfile))
    margin = 34
    header = pymupdf.Rect(margin, 24, size.width - margin, 70)
    body = pymupdf.Rect(margin, 72, size.width - margin, size.height - 40)
    page.insert_textbox(
        header,
        f"Русский перевод исходной страницы {source_page} — часть {part}/{parts_total}",
        fontname=fontname,
        fontsize=12,
        color=(0.12, 0.12, 0.12),
        align=pymupdf.TEXT_ALIGN_CENTER,
    )
    used_size = None
    result = None
    for fontsize in (10.0, 9.5, 9.0, 8.5, 8.0, 7.5, 7.0):
        shape = page.new_shape()
        result = shape.insert_textbox(
            body,
            text,
            fontname=fontname,
            fontsize=fontsize,
            lineheight=1.28,
            color=(0, 0, 0),
            align=pymupdf.TEXT_ALIGN_LEFT,
        )
        if result >= 0:
            shape.commit()
            used_size = fontsize
            break
    if used_size is None:
        raise ValueError(f"translation for source page {source_page}, part {part}, does not fit at 7 pt")
    page.insert_text(
        (margin, size.height - 18),
        "FACSIMILE: исходная страница сохранена перед этой страницей; OCR проверяется визуально.",
        fontname=fontname,
        fontsize=6.5,
        color=(0.35, 0.35, 0.35),
    )
    return {
        "source_page": source_page,
        "part": part,
        "parts_total": parts_total,
        "font_size": used_size,
        "remaining_space": round(float(result), 2),
    }


def build_facsimile(source: Path, translations: Path, output: Path) -> dict:
    src = pymupdf.open(source)
    entries = translation_entries(translations)
    out = pymupdf.open()
    build_rows = []
    for entry in entries:
        p = int(entry["page"])
        if p < 1 or p > len(src):
            raise ValueError(f"page {p} outside source")
        out.insert_pdf(src, from_page=p - 1, to_page=p - 1)
        chunks = split_translation(str(entry["translation"]).strip())
        for part, chunk in enumerate(chunks, start=1):
            row = add_translation_page(out, src[p - 1].rect, p, chunk, part, len(chunks))
            build_rows.append(row)
    output.parent.mkdir(parents=True, exist_ok=True)
    out.set_metadata({
        "title": "Факсимильный перевод на русский язык",
        "subject": "Original source pages followed by Russian translation pages",
        "keywords": "FACSIMILE, translation, Russian",
    })
    out.save(output, garbage=4, deflate=True)
    return {
        "output": str(output.resolve()),
        "sha256": sha256(output),
        "fidelity_class": "FACSIMILE",
        "source_pages_preserved": len(entries),
        "translation_pages": len(build_rows),
        "output_pages": len(out),
        "build": build_rows,
    }


def pix_hash(page: pymupdf.Page, dpi: int = 150) -> str:
    pix = render_page(page, dpi=dpi)
    h = hashlib.sha256()
    h.update(str((pix.width, pix.height, pix.n)).encode())
    h.update(pix.samples)
    return h.hexdigest()


def verify_facsimile(source: Path, translations: Path, output: Path) -> dict:
    src = pymupdf.open(source)
    out = pymupdf.open(output)
    entries = translation_entries(translations)
    rows = []
    failures = []
    expected_pages = sum(1 + len(split_translation(str(entry["translation"]).strip())) for entry in entries)
    if len(out) != expected_pages:
        failures.append(f"output page count {len(out)} != {expected_pages}")
    output_index = 0
    for entry in entries:
        source_page = int(entry["page"])
        original_hash = pix_hash(src[source_page - 1])
        copied_hash = pix_hash(out[output_index])
        visual_equal = original_hash == copied_hash
        chunks = split_translation(str(entry["translation"]).strip())
        translation_pages = []
        cyr = 0
        for part in range(len(chunks)):
            translation_index = output_index + 1 + part
            translated_text = out[translation_index].get_text("text") if translation_index < len(out) else ""
            page_cyr = cyrillic_count(translated_text)
            cyr += page_cyr
            translation_pages.append({"output_page": translation_index + 1, "cyrillic_chars": page_cyr})
        if not visual_equal:
            failures.append(f"source page {source_page} visual hash mismatch")
        if cyr < 20:
            failures.append(f"translation page for source {source_page} has insufficient Cyrillic text")
        rows.append({
            "source_page": source_page,
            "source_visual_sha256": original_hash,
            "facsimile_visual_sha256": copied_hash,
            "pixel_exact_render_match": visual_equal,
            "translation_cyrillic_chars": cyr,
            "translation_pages": translation_pages,
        })
        output_index += 1 + len(chunks)
    return {
        "status": "PASS" if not failures else "FAIL",
        "fidelity_class": "FACSIMILE",
        "source": str(source.resolve()),
        "source_sha256": sha256(source),
        "output": str(output.resolve()),
        "output_sha256": sha256(output),
        "expected_output_pages": expected_pages,
        "actual_output_pages": len(out),
        "rows": rows,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Scanned-PDF facsimile translation helper")
    sub = parser.add_subparsers(dest="command", required=True)

    p_inspect = sub.add_parser("inspect")
    p_inspect.add_argument("source", type=Path)
    p_inspect.add_argument("--output", type=Path, required=True)

    p_sample = sub.add_parser("sample")
    p_sample.add_argument("source", type=Path)
    p_sample.add_argument("--pages", required=True)
    p_sample.add_argument("--output", type=Path, required=True)
    p_sample.add_argument("--render-dir", type=Path)

    p_extract = sub.add_parser("extract")
    p_extract.add_argument("source", type=Path)
    p_extract.add_argument("--pages", required=True)
    p_extract.add_argument("--output", type=Path, required=True)

    p_build = sub.add_parser("build")
    p_build.add_argument("source", type=Path)
    p_build.add_argument("translations", type=Path)
    p_build.add_argument("--output", type=Path, required=True)

    p_verify = sub.add_parser("verify")
    p_verify.add_argument("source", type=Path)
    p_verify.add_argument("translations", type=Path)
    p_verify.add_argument("translated", type=Path)
    p_verify.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    if not args.source.exists():
        parser.error(f"source not found: {args.source}")

    if args.command == "inspect":
        result = inspect_pdf(args.source)
    elif args.command == "sample":
        src = pymupdf.open(args.source)
        result = sample_pdf(args.source, parse_pages(args.pages, len(src)), args.output, args.render_dir)
    elif args.command == "extract":
        src = pymupdf.open(args.source)
        result = extract_units(args.source, parse_pages(args.pages, len(src)))
    elif args.command == "build":
        result = build_facsimile(args.source, args.translations, args.output)
    elif args.command == "verify":
        result = verify_facsimile(args.source, args.translations, args.translated)
    else:
        raise AssertionError(args.command)

    save_json(args.output if args.command in {"inspect", "extract", "verify"} else args.output.with_suffix(args.output.suffix + ".manifest.json"), result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status", "PASS") != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
