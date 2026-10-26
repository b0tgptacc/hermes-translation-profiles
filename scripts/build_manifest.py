from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "node_modules"}
EXCLUDED_FILES = {"MANIFEST.json"}


def payload_files() -> list[Path]:
    result = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if rel.name in EXCLUDED_FILES or any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        if path.suffix == ".pyc":
            continue
        result.append(path)
    return sorted(result, key=lambda p: p.relative_to(ROOT).as_posix())


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    entries = []
    for path in payload_files():
        rel = path.relative_to(ROOT).as_posix()
        entries.append({"path": rel, "size": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "schema_version": 1,
        "purpose": "Portable credential-free Hermes translation profiles",
        "files": entries,
    }
    target = ROOT / "MANIFEST.json"
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"files": len(entries), "bytes": sum(e["size"] for e in entries)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
