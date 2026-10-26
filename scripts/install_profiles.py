from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

REPO = Path(__file__).resolve().parents[1]
PROFILES = ("translator", "fasttranslator")


def run(args: list[str], *, input_text: str | None = None, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(args))
    return subprocess.run(
        args,
        input=input_text,
        text=True,
        encoding="utf-8",
        capture_output=capture,
        check=True,
    )


def profile_exists(name: str) -> bool:
    proc = subprocess.run(
        ["hermes", "profile", "show", name],
        text=True,
        encoding="utf-8",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return proc.returncode == 0


def profile_dir(name: str) -> Path:
    proc = run(["hermes", "-p", name, "config", "path"], capture=True)
    path = Path(proc.stdout.strip().splitlines()[-1])
    if not path.is_file():
        raise RuntimeError(f"profile config path is not a file: {path}")
    return path.parent


def config_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def install_dependencies() -> None:
    packages = [
        "pymupdf",
        "pypdf",
        "pdfplumber",
        "python-docx",
        "python-pptx",
        "openpyxl",
        "Pillow",
        "reportlab",
        "lxml",
    ]
    run([sys.executable, "-m", "pip", "install", *packages])


def write_launchers(workspace: Path) -> None:
    script = workspace / "fasttranslate.py"
    bat = workspace / "fasttranslate.bat"
    sh = workspace / "fasttranslate.sh"
    bat.write_text(f'@echo off\r\npython "{script}" %*\r\n', encoding="utf-8")
    sh.write_text(f'#!/usr/bin/env sh\nexec python3 "{script}" "$@"\n', encoding="utf-8")
    try:
        sh.chmod(0o755)
    except OSError:
        pass


def install_profile(source_name: str, target_name: str, workspace_root: Path, force: bool, workspace_prefix: str) -> None:
    spec_path = REPO / "profiles" / source_name / "profile-spec.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if profile_exists(target_name):
        if not force:
            raise RuntimeError(f"profile {target_name!r} already exists; rerun with --force to replace it")
        run(["hermes", "profile", "delete", target_name, "-y"])

    run([
        "hermes", "profile", "create", target_name, "--no-skills",
        "--description", spec["description"],
    ])
    # New profiles start at config version 0. Migrate non-interactively.
    run(["hermes", "-p", target_name, "config", "migrate"], input_text="n\n")
    run(["hermes", "-p", target_name, "config", "set", "model.provider", spec["provider"]])
    run(["hermes", "-p", target_name, "config", "set", "model.default", spec["model"]])

    workspace = workspace_root / f"{workspace_prefix}{spec['workspace_name']}"
    workspace.mkdir(parents=True, exist_ok=True)
    run(["hermes", "-p", target_name, "config", "set", "terminal.cwd", workspace.as_posix()])
    for key, value in spec["config"].items():
        cmd = ["hermes", "-p", target_name, "config", "set"]
        if key == "agent.reasoning_effort":
            cmd.append("--force")
        run([*cmd, key, config_value(value)])
    disabled = list(spec.get("disable_toolsets", []))
    if disabled:
        run(["hermes", "-p", target_name, "tools", "disable", *disabled])

    pdir = profile_dir(target_name)
    soul = REPO / "profiles" / source_name / "SOUL.md"
    if soul.is_file():
        shutil.copy2(soul, pdir / "SOUL.md")

    if source_name == "translator":
        src_skills = REPO / "profiles" / source_name / "skills"
        shutil.copytree(src_skills, pdir / "skills", dirs_exist_ok=True)
        shutil.copy2(REPO / "profiles" / source_name / "workspace.hermes.md", workspace / ".hermes.md")
        shutil.copytree(REPO / "profiles" / source_name / "glossary", workspace / "glossary", dirs_exist_ok=True)
        for child in ("inbox", "work", "output", "tests"):
            (workspace / child).mkdir(exist_ok=True)
    else:
        source_script = (REPO / "profiles" / source_name / "fasttranslate.py").read_text(encoding="utf-8")
        source_script = source_script.replace('"fasttranslator"', f'"{target_name}"')
        (workspace / "fasttranslate.py").write_text(source_script, encoding="utf-8")
        for child in ("input", "output", "tests"):
            (workspace / child).mkdir(exist_ok=True)
        write_launchers(workspace)

    run(["hermes", "-p", target_name, "config", "check"])
    run(["hermes", "profile", "show", target_name])


def main() -> int:
    parser = argparse.ArgumentParser(description="Install portable Hermes translation profiles")
    parser.add_argument("--profiles", choices=["translator", "fasttranslator", "both"], default="both")
    parser.add_argument("--workspace-root", type=Path, default=Path.home() / "Documents")
    parser.add_argument("--force", action="store_true", help="Replace profiles with the same names")
    parser.add_argument("--install-deps", action="store_true", help="Install local document Python packages")
    parser.add_argument("--name-prefix", default="", help="Prefix installed profile/workspace names (acceptance testing)")
    args = parser.parse_args()

    if shutil.which("hermes") is None:
        raise SystemExit("Hermes CLI is not on PATH. Install Hermes Agent first.")
    if args.install_deps:
        install_dependencies()
    selected = PROFILES if args.profiles == "both" else (args.profiles,)
    for source_name in selected:
        target_name = f"{args.name_prefix}{source_name}"
        install_profile(source_name, target_name, args.workspace_root.expanduser().resolve(), args.force, args.name_prefix)
    print("\nInstallation complete.")
    print("Authenticate the selected provider on the target device if needed:")
    print("  hermes auth add openai-codex")
    print("Then run:")
    print(f"  hermes -p {args.name_prefix}translator")
    print(f"  hermes -p {args.name_prefix}fasttranslator --reasoning none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
