#!/usr/bin/env python3
"""Build an isolated plugin fixture and validate the bundled skill component."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
COMPONENT_ITEMS = ("SKILL.md", "agents", "references", "scripts")


def validate_fixture(manifest_relative: Path) -> int:
    with tempfile.TemporaryDirectory(prefix="independent-audit-gate-plugin-") as temp_dir:
        plugin_root = Path(temp_dir) / "audit-orchestration"
        skill_root = plugin_root / "skills" / "independent-audit-gate"
        skill_root.mkdir(parents=True)

        manifest = {
            "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
            "name": "audit-orchestration",
            "version": "0.0.0",
            "description": "Isolated fixture for validating bundled audit skills.",
        }
        manifest_path = plugin_root / manifest_relative
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

        for item in COMPONENT_ITEMS:
            source = REPO_ROOT / item
            destination = skill_root / item
            if source.is_dir():
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)

        command = [
            sys.executable,
            str(skill_root / "scripts" / "validate_skill.py"),
            "--strict",
        ]
        result = subprocess.run(command, text=True, capture_output=True, check=False)
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        return result.returncode


def main() -> int:
    for manifest_relative in (Path("plugin.json"), Path(".codex-plugin/plugin.json")):
        print(f"Testing plugin component with {manifest_relative.as_posix()}")
        result = validate_fixture(manifest_relative)
        if result != 0:
            return result
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
