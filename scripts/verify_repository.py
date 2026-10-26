from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST.json"
EXCLUDED_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "node_modules"}
FORBIDDEN_NAMES = {".env", "auth.json", "auth.lock", "state.db", ".git-credentials"}
SECRET_PATTERNS = {
    "private_key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_token": re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "openai_key": re.compile(rb"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "bearer_token": re.compile(rb"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{20,}"),
    "oauth_assignment": re.compile(rb"(?i)oauth_token\s*[:=]\s*[^\s<'\"]{12,}"),
}
USER_PATH = re.compile(rb"(?i)C:[/\\]Users[/\\](?:admin|[^/\\\s]+)[/\\](?:AppData|Desktop)")


def files_on_disk() -> dict[str, Path]:
    result = {}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path == MANIFEST:
            continue
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDED_DIRS for part in rel.parts) or path.suffix == ".pyc":
            continue
        result[rel.as_posix()] = path
    return result


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify() -> dict:
    failures = []
    if not MANIFEST.is_file():
        return {"status": "FAIL", "failures": ["MANIFEST.json missing"]}
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected = {entry["path"]: entry for entry in manifest["files"]}
    actual = files_on_disk()
    if set(expected) != set(actual):
        failures.append({
            "file_set_mismatch": {
                "missing": sorted(set(expected) - set(actual)),
                "extra": sorted(set(actual) - set(expected)),
            }
        })
    secret_hits = []
    user_path_hits = []
    oversized = []
    for rel, path in actual.items():
        if any(part.lower() in {name.lower() for name in FORBIDDEN_NAMES} for part in Path(rel).parts):
            failures.append({"forbidden_path": rel})
        data = path.read_bytes()
        entry = expected.get(rel)
        if entry:
            if len(data) != entry["size"]:
                failures.append({"size_mismatch": rel})
            if sha256(path) != entry["sha256"]:
                failures.append({"sha256_mismatch": rel})
        if len(data) >= 95 * 1024 * 1024:
            oversized.append(rel)
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(data):
                secret_hits.append({"path": rel, "pattern": name})
        if USER_PATH.search(data):
            user_path_hits.append(rel)
    if secret_hits:
        failures.append({"secret_patterns": secret_hits})
    if user_path_hits:
        failures.append({"machine_specific_user_paths": sorted(user_path_hits)})
    if oversized:
        failures.append({"oversized_files": oversized})

    # Structural checks.
    specs = []
    for rel in ("profiles/translator/profile-spec.json", "profiles/fasttranslator/profile-spec.json"):
        data = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        specs.append({"name": data["name"], "provider": data["provider"], "model": data["model"]})
    skill_files = list((ROOT / "profiles/translator/skills").rglob("SKILL.md"))
    if len(skill_files) != 8:
        failures.append({"skill_count": len(skill_files), "expected": 8})
    for path in skill_files:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n") or "\n---\n" not in text[4:]:
            failures.append({"invalid_skill_frontmatter": path.relative_to(ROOT).as_posix()})

    return {
        "status": "PASS" if not failures else "FAIL",
        "file_count": len(actual),
        "total_bytes": sum(path.stat().st_size for path in actual.values()),
        "profiles": specs,
        "skills": len(skill_files),
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify portable profile repository integrity and secret safety")
    parser.parse_args()
    result = verify()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
