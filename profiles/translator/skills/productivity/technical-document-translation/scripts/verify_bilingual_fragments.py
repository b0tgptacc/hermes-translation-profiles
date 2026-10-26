#!/usr/bin/env python
"""Verify page-linked bilingual fragment translations.

Example:
  python verify_bilingual_fragments.py source.txt translated.md

The source must contain <!-- SOURCE_PAGE n --> markers. Only source lines
containing CJK ideographs are expected as `Оригинал:` lines in the target.
Target accepts plain or bold labels:
  Оригинал: ... / Перевод: ...
  **Оригинал:**\n... / **Перевод:**\n...
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
MARKER = re.compile(r"<!--\s*SOURCE_PAGE\s+(\d+)\s*-->")


def parse_target(text: str):
    originals = [x.strip() for x in re.findall(
        r"^(?:Оригинал:\s?|\*\*Оригинал:\*\*\n)(.*)$", text, re.M)]
    translations = re.findall(
        r"(?:^Перевод:\s?|^\*\*Перевод:\*\*\n)(.*?)"
        r"(?=\n(?:Оригинал:|\*\*Оригинал:\*\*|<!-- SOURCE_PAGE|## Страница)|\Z)",
        text, re.M | re.S)
    translations = [x.strip() for x in translations]
    markers = [int(x) for x in MARKER.findall(text)]
    return originals, translations, markers


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("translation")
    args = ap.parse_args()
    src = Path(args.source).read_text(encoding="utf-8")
    dst = Path(args.translation).read_text(encoding="utf-8")
    source_lines = [x.strip() for x in src.splitlines() if CJK.search(x)]
    source_markers = [int(x) for x in MARKER.findall(src)]
    originals, translations, target_markers = parse_target(dst)
    report = {
        "source_lines": len(source_lines),
        "original_lines": len(originals),
        "translation_lines": len(translations),
        "source_order_exact": source_lines == originals,
        "pair_counts_match": len(originals) == len(translations),
        "source_markers": len(source_markers),
        "target_markers": len(target_markers),
        "markers_exact": source_markers == target_markers,
        "markers_unique_sorted": target_markers == sorted(set(target_markers)),
        "cjk_in_translation_fields": sum(len(CJK.findall(x)) for x in translations),
    }
    report["ok"] = all([
        report["source_order_exact"], report["pair_counts_match"],
        report["markers_exact"], report["markers_unique_sorted"],
        report["cjk_in_translation_fields"] == 0,
    ])
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
