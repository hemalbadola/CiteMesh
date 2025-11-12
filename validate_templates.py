#!/usr/bin/env python3
"""validate_templates.py
Purpose: Scan template files across contributor folders to ensure required sections are present.
Usage: ./validate_templates.py [-r ROOT]
Dependencies: Python 3.8+
Flags:
  -r, --root  Root directory to scan (default: current working directory)

Validation Rules:
- File must contain at least one level-1 heading (# )
- File must include an instruction section (case-insensitive match: "instruction")
- File must include an example or sample block (match keywords: "example" or "sample")
"""
from __future__ import annotations

import argparse
import pathlib
import sys

REQUIRED_KEYWORDS = {
    "heading": "# ",
    "instructions": "instruction",
    "sample": "sample",
}

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate template files for required sections.")
    parser.add_argument("-r", "--root", default=pathlib.Path.cwd(), type=pathlib.Path,
                        help="Root directory containing contributor folders")
    return parser.parse_args()


def is_template_file(path: pathlib.Path) -> bool:
    template_markers = ("template", "_template", "guideline", "plan")
    return path.is_file() and path.suffix in {".md", ".sql", ".py", ".sh"} and any(marker in path.name.lower() for marker in template_markers)


def validate_file(path: pathlib.Path) -> list[str]:
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [f"{path}: unable to read file (encoding error)"]

    errors: list[str] = []
    lowered = content.lower()

    if REQUIRED_KEYWORDS["heading"] not in content:
        errors.append("missing level-1 heading (# )")
    if REQUIRED_KEYWORDS["instructions"] not in lowered:
        errors.append("missing instructions section")
    if "example" not in lowered and REQUIRED_KEYWORDS["sample"] not in lowered:
        errors.append("missing example/sample section")

    return [f"{path}: {err}" for err in errors]


def main() -> int:
    args = parse_args()
    root = args.root

    if not root.exists():
        print(f"Error: root path {root} does not exist", file=sys.stderr)
        return 1

    template_files = [path for path in root.rglob("*") if is_template_file(path)]

    failures: list[str] = []
    for template_file in template_files:
        failures.extend(validate_file(template_file))

    if failures:
        print("Template validation failures detected:")
        for failure in failures:
            print(f" - {failure}")
        return 2

    print("All templates passed validation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
