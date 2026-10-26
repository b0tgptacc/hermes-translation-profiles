from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import pymupdf

FONT_CANDIDATES = {
    "ru": [
        ("HERMES_RU_FONT", ""),
        ("", r"C:/Windows/Fonts/arial.ttf"),
        ("", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ("", "/System/Library/Fonts/Supplemental/Arial.ttf"),
    ],
    "ru_bold": [
        ("HERMES_RU_BOLD_FONT", ""),
        ("", r"C:/Windows/Fonts/arialbd.ttf"),
        ("", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ("", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    ],
    "cjk": [
        ("HERMES_CJK_FONT", ""),
        ("", r"C:/Windows/Fonts/msyh.ttc"),
        ("", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        ("", "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf"),
        ("", "/System/Library/Fonts/PingFang.ttc"),
    ],
}


def resolve_font(kind: str) -> Path:
    for env_name, fallback in FONT_CANDIDATES[kind]:
        value = os.environ.get(env_name, "") if env_name else fallback
        if value and Path(value).is_file():
            return Path(value)
    if kind == "ru_bold":
        return resolve_font("ru")
    raise FileNotFoundError(
        f"No font found for {kind}. Set HERMES_RU_FONT / HERMES_RU_BOLD_FONT / "
        "HERMES_CJK_FONT as appropriate."
    )


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def cyrillic_count(text: str) -> int:
    return sum(1 for c in text if "\u0400" <= c <= "\u04ff")


def register_fonts(page: pymupdf.Page) -> dict[str, str]:
    names = {"ru": "F_RU", "ru_bold": "F_RU_B", "cjk": "F_CJK"}
    for key in names:
        file = resolve_font(key)
        page.insert_font(fontname=names[key], fontfile=str(file))
    return names


def rect(values: list[float]) -> pymupdf.Rect:
    if len(values) != 4:
        raise ValueError(f"bbox requires four numbers: {values}")
    return pymupdf.Rect(*map(float, values))


def fit_text(
    page: pymupdf.Page,
    box: pymupdf.Rect,
    text: str,
    fontname: str,
    max_size: float,
    min_size: float,
    align: int,
    lineheight: float,
    color: tuple[float, float, float] = (0, 0, 0),
) -> dict:
    size = max_size
    while size + 1e-9 >= min_size:
        shape = page.new_shape()
        spare = shape.insert_textbox(
            box,
            text,
            fontname=fontname,
            fontsize=size,
            lineheight=lineheight,
            color=color,
            align=align,
        )
        if spare >= 0:
            shape.commit()
            return {"font_size": round(size, 2), "spare_height": round(float(spare), 2)}
        size -= 0.25
    raise ValueError(f"text does not fit bbox={list(box)} above min font {min_size}: {text[:80]!r}")


def draw_text(page: pymupdf.Page, item: dict, fonts: dict[str, str]) -> dict:
    style = item.get("style", "ru")
    align_name = item.get("align", "left")
    aligns = {"left": pymupdf.TEXT_ALIGN_LEFT, "center": pymupdf.TEXT_ALIGN_CENTER, "right": pymupdf.TEXT_ALIGN_RIGHT, "justify": pymupdf.TEXT_ALIGN_JUSTIFY}
    result = fit_text(
        page,
        rect(item["bbox"]),
        str(item["text"]),
        fonts[style],
        float(item.get("max_font", 9)),
        float(item.get("min_font", 5)),
        aligns[align_name],
        float(item.get("lineheight", 1.15)),
    )
    return {"type": "text", "id": item.get("id"), **result}


def draw_table(page: pymupdf.Page, item: dict, fonts: dict[str, str]) -> dict:
    box = rect(item["bbox"])
    rows = item["rows"]
    if not rows or not all(len(row) == len(rows[0]) for row in rows):
        raise ValueError("table rows must be non-empty and rectangular")
    cols = len(rows[0])
    col_weights = item.get("col_weights") or [1] * cols
    if len(col_weights) != cols:
        raise ValueError("col_weights length mismatch")
    row_weights = item.get("row_weights") or [1] * len(rows)
    if len(row_weights) != len(rows):
        raise ValueError("row_weights length mismatch")
    total_c = sum(col_weights)
    total_r = sum(row_weights)
    xs = [box.x0]
    for weight in col_weights:
        xs.append(xs[-1] + box.width * weight / total_c)
    ys = [box.y0]
    for weight in row_weights:
        ys.append(ys[-1] + box.height * weight / total_r)
    width = float(item.get("line_width", 0.7))
    page.draw_rect(box, color=(0, 0, 0), width=width)
    for x in xs[1:-1]:
        page.draw_line((x, box.y0), (x, box.y1), color=(0, 0, 0), width=width)
    for y in ys[1:-1]:
        page.draw_line((box.x0, y), (box.x1, y), color=(0, 0, 0), width=width)
    cell_results = []
    padding = float(item.get("padding", 2.0))
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            cell = pymupdf.Rect(xs[c] + padding, ys[r] + padding, xs[c + 1] - padding, ys[r + 1] - padding)
            style = "ru_bold" if r == 0 else "ru"
            result = fit_text(
                page,
                cell,
                str(value),
                fonts[style],
                float(item.get("header_font" if r == 0 else "body_font", 6.5)),
                float(item.get("min_font", 4.5)),
                pymupdf.TEXT_ALIGN_CENTER,
                float(item.get("lineheight", 1.05)),
            )
            cell_results.append({"row": r, "col": c, **result})
    return {"type": "table", "id": item.get("id"), "rows": len(rows), "cols": cols, "cells": cell_results}


def draw_source_crop(page: pymupdf.Page, item: dict, source_doc: pymupdf.Document) -> dict:
    source_page = int(item["source_page"])
    if source_page < 1 or source_page > len(source_doc):
        raise ValueError(f"source crop page {source_page} outside source document")
    clip = rect(item["clip"])
    target = rect(item.get("bbox", item["clip"]))
    dpi = int(item.get("dpi", 300))
    scale = dpi / 72.0
    pix = source_doc[source_page - 1].get_pixmap(
        matrix=pymupdf.Matrix(scale, scale),
        clip=clip,
        colorspace=pymupdf.csRGB,
        alpha=False,
    )
    page.insert_image(target, stream=pix.tobytes("png"), keep_proportion=False)
    return {
        "type": "source_crop",
        "id": item.get("id"),
        "source_page": source_page,
        "clip": list(clip),
        "bbox": list(target),
        "dpi": dpi,
    }


def build(spec_path: Path, output: Path) -> dict:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    pages = spec.get("pages")
    if not isinstance(pages, list) or not pages:
        raise ValueError("spec needs non-empty pages[]")
    out = pymupdf.open()
    source_doc = None
    if any(item.get("type") == "source_crop" for p in pages for item in p.get("elements", [])):
        source_path = Path(spec["source_file"])
        source_doc = pymupdf.open(source_path)
    page_results = []
    for page_spec in pages:
        width = float(page_spec["width"])
        height = float(page_spec["height"])
        page = out.new_page(width=width, height=height)
        fonts = register_fonts(page)
        results = []
        for item in page_spec.get("elements", []):
            kind = item["type"]
            if kind == "text":
                results.append(draw_text(page, item, fonts))
            elif kind == "table":
                results.append(draw_table(page, item, fonts))
            elif kind == "line":
                page.draw_line(tuple(item["from"]), tuple(item["to"]), color=(0, 0, 0), width=float(item.get("width", 0.7)))
                results.append({"type": "line", "id": item.get("id")})
            elif kind == "source_crop":
                if source_doc is None:
                    raise ValueError("source_crop requires top-level source_file")
                results.append(draw_source_crop(page, item, source_doc))
            else:
                raise ValueError(f"unsupported element type: {kind}")
        page_results.append({"source_page": int(page_spec["source_page"]), "width": width, "height": height, "elements": results})
    output.parent.mkdir(parents=True, exist_ok=True)
    out.set_metadata({"title": spec.get("title", "Russian layout-locked translation"), "subject": "SCANNED_LAYOUT_LOCKED"})
    out.save(output, garbage=4, deflate=True)
    manifest = {
        "status": "PASS",
        "fidelity_class": "SCANNED_LAYOUT_LOCKED",
        "spec": str(spec_path.resolve()),
        "spec_sha256": sha256(spec_path),
        "output": str(output.resolve()),
        "output_sha256": sha256(output),
        "page_count": len(out),
        "pages": page_results,
    }
    manifest_path = output.with_suffix(output.suffix + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def verify(spec_path: Path, output: Path, report: Path) -> dict:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    doc = pymupdf.open(output)
    failures = []
    expected = spec["pages"]
    if len(doc) != len(expected):
        failures.append(f"page count {len(doc)} != {len(expected)}")
    rows = []
    for idx, page_spec in enumerate(expected):
        if idx >= len(doc):
            break
        page = doc[idx]
        width_ok = abs(page.rect.width - float(page_spec["width"])) < 0.01
        height_ok = abs(page.rect.height - float(page_spec["height"])) < 0.01
        text = page.get_text("text") or ""
        cyr = cyrillic_count(text)
        if not width_ok or not height_ok:
            failures.append(f"page {idx + 1} dimensions mismatch")
        if cyr < int(page_spec.get("min_cyrillic", 50)):
            failures.append(f"page {idx + 1} insufficient Cyrillic text: {cyr}")
        rows.append({
            "output_page": idx + 1,
            "source_page": int(page_spec["source_page"]),
            "width": page.rect.width,
            "height": page.rect.height,
            "dimensions_match": width_ok and height_ok,
            "cyrillic_chars": cyr,
            "drawings": len(page.get_drawings()),
        })
    result = {
        "status": "PASS" if not failures else "FAIL",
        "fidelity_class": "SCANNED_LAYOUT_LOCKED",
        "spec_sha256": sha256(spec_path),
        "output_sha256": sha256(output),
        "expected_page_count": len(expected),
        "actual_page_count": len(doc),
        "pages": rows,
        "failures": failures,
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Russian scanned-PDF pages from a locked layout specification")
    sub = parser.add_subparsers(dest="command", required=True)
    p_build = sub.add_parser("build")
    p_build.add_argument("spec", type=Path)
    p_build.add_argument("--output", type=Path, required=True)
    p_verify = sub.add_parser("verify")
    p_verify.add_argument("spec", type=Path)
    p_verify.add_argument("translated", type=Path)
    p_verify.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "build":
        result = build(args.spec, args.output)
    else:
        result = verify(args.spec, args.translated, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
