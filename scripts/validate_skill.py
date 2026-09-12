#!/usr/bin/env python3
"""Validate the standalone or plugin-bundled independent-audit-gate skill."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


EXPECTED_NAME = "independent-audit-gate"
EXPECTED_VERSION = "1.0.0"
CORE_REQUIRED_FILES = (
    "SKILL.md",
    "agents/openai.yaml",
    "references/audit-protocol.md",
    "references/orchestrator-integration.md",
)
STANDALONE_REQUIRED_FILES = (
    "README.md",
    "LICENSE",
    ".gitattributes",
    ".gitignore",
    ".github/workflows/validate.yml",
)
PLACEHOLDERS = (
    "TO" "DO",
    "T" "BD",
    "YOUR" "-SKILL-NAME",
    "YOUR" "_GITHUB_USERNAME",
)
SECRET_PATTERNS = {
    "GitHub token": re.compile(r"\b(?:gh[opusr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    "OpenAI-style key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "personal Windows path": re.compile(r"[A-Za-z]:\\Users\\(?!<USER>)[^\\\s]+", re.IGNORECASE),
    "workspace path": re.compile(r"[A-Za-z]:\\codex\\", re.IGNORECASE),
}
LOCAL_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def read_utf8(path: Path, errors: list[str]) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        errors.append(f"{path}: not valid UTF-8 ({exc})")
        return ""
    if "\ufffd" in text:
        errors.append(f"{path}: contains a Unicode replacement character")
    return text


def parse_frontmatter(text: str, errors: list[str]) -> dict[str, str]:
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.DOTALL)
    if not match:
        errors.append("SKILL.md: missing YAML frontmatter")
        return {}

    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if line.startswith((" ", "\t")) or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"\'')
    return values


def validate_links(root: Path, relative: Path, text: str, errors: list[str]) -> None:
    for raw_target in LOCAL_LINK.findall(text):
        target = raw_target.strip().split("#", 1)[0]
        if not target or re.match(r"^(?:https?://|mailto:)", target, re.IGNORECASE):
            continue
        resolved = (root / relative.parent / target).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{relative}: local link escapes package root: {raw_target}")
            continue
        if not resolved.exists():
            errors.append(f"{relative}: missing local link target: {raw_target}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--profile",
        choices=("auto", "standalone", "plugin-component"),
        default="auto",
        help="validation profile; auto detects a skill nested under a supported plugin manifest",
    )
    parser.add_argument("--strict", action="store_true", help="enable public-release hygiene checks")
    args = parser.parse_args()

    root = args.root.resolve()
    errors: list[str] = []

    plugin_root = root.parent.parent if root.parent.name == "skills" else None
    plugin_manifests = (
        (plugin_root / "plugin.json", plugin_root / ".codex-plugin/plugin.json")
        if plugin_root is not None
        else ()
    )
    detected_plugin_component = (
        root.name == EXPECTED_NAME
        and plugin_root is not None
        and any(path.is_file() for path in plugin_manifests)
    )
    profile = args.profile
    if profile == "auto":
        profile = "plugin-component" if detected_plugin_component else "standalone"

    if profile == "plugin-component" and not detected_plugin_component:
        errors.append(
            "plugin-component profile requires skills/independent-audit-gate under a plugin root "
            "containing plugin.json or .codex-plugin/plugin.json"
        )

    required_files = CORE_REQUIRED_FILES
    if profile == "standalone":
        required_files += STANDALONE_REQUIRED_FILES

    for relative in required_files:
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")

    skill_path = root / "SKILL.md"
    skill_text = read_utf8(skill_path, errors) if skill_path.is_file() else ""
    frontmatter = parse_frontmatter(skill_text, errors) if skill_text else {}

    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")
    if name != EXPECTED_NAME:
        errors.append(f"SKILL.md: name must be {EXPECTED_NAME!r}, got {name!r}")
    if not NAME_PATTERN.fullmatch(name) or len(name) > 64:
        errors.append("SKILL.md: name must use lowercase letters, digits, and hyphens and be at most 64 characters")
    if not description:
        errors.append("SKILL.md: description is required")
    if len(description) > 1024:
        errors.append("SKILL.md: description must be at most 1024 characters")
    version_line = next((line for line in skill_text.splitlines() if line.startswith("  version:")), "")
    version = version_line.split(":", 1)[1].strip().strip('"\'') if version_line else ""
    if version != EXPECTED_VERSION:
        errors.append(f"SKILL.md: metadata.version must be {EXPECTED_VERSION!r}, got {version!r}")

    openai_path = root / "agents/openai.yaml"
    openai_text = read_utf8(openai_path, errors) if openai_path.is_file() else ""
    if openai_text:
        if "$independent-audit-gate" not in openai_text:
            errors.append("agents/openai.yaml: default_prompt must mention $independent-audit-gate")
        if not re.search(r"^\s*allow_implicit_invocation:\s*true\s*$", openai_text, re.MULTILINE):
            errors.append("agents/openai.yaml: allow_implicit_invocation must be true")
        if re.search(r"^dependencies:\s*$", openai_text, re.MULTILINE):
            errors.append("agents/openai.yaml: runtime dependencies are not allowed")

    tracked_candidates = [
        path
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(root).parts and "__pycache__" not in path.parts
    ]
    for path in tracked_candidates:
        relative = path.relative_to(root)
        if path.suffix.lower() not in {".md", ".yaml", ".yml", ".py", ".txt", ""}:
            continue
        text = read_utf8(path, errors)
        validate_links(root, relative, text, errors)
        if args.strict:
            upper = text.upper()
            for placeholder in PLACEHOLDERS:
                if placeholder in upper:
                    errors.append(f"{relative}: unresolved placeholder {placeholder}")
            for label, pattern in SECRET_PATTERNS.items():
                if pattern.search(text):
                    errors.append(f"{relative}: possible {label}")

    if errors:
        print("Skill validation failed:", file=sys.stderr)
        for error in sorted(set(errors)):
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Skill validation passed ({profile}): {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
