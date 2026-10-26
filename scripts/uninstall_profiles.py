from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess

PROFILE_WORKSPACES = {
    "translator": "HermesTranslator",
    "fasttranslator": "HermesFastTranslator",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Remove portable Hermes translation profiles")
    parser.add_argument("--profiles", choices=["translator", "fasttranslator", "both"], default="both")
    parser.add_argument("--workspace-root", type=Path, default=Path.home() / "Documents")
    parser.add_argument("--remove-workspaces", action="store_true", help="Also delete translation workspaces and their files")
    args = parser.parse_args()
    selected = tuple(PROFILE_WORKSPACES) if args.profiles == "both" else (args.profiles,)
    for name in selected:
        proc = subprocess.run(["hermes", "profile", "show", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if proc.returncode == 0:
            subprocess.run(["hermes", "profile", "delete", name, "-y"], check=True)
        if args.remove_workspaces:
            workspace = args.workspace_root.expanduser().resolve() / PROFILE_WORKSPACES[name]
            if workspace.exists():
                shutil.rmtree(workspace)
                print(f"Removed {workspace}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
