#!/usr/bin/env python3
"""update_readmes.py
Purpose: Update README.md files in contributor directories with the current date.
Usage: ./update_readmes.py [-r ROOT] [-f DATE_FORMAT]
Dependencies: Python 3.8+
Flags:
  -r, --root        Root directory to scan (default: current working directory)
  -f, --format      datetime format string (default: %Y-%m-%d)

The script looks for a line starting with "Last updated:" (case-insensitive).
If not found, it appends the line at the end of the README.
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update README last updated timestamps.")
    parser.add_argument("-r", "--root", default=pathlib.Path.cwd(), type=pathlib.Path,
                        help="Project root containing README files")
    parser.add_argument("-f", "--format", default="%Y-%m-%d",
                        help="Datetime format string, e.g., %Y-%m-%d")
    return parser.parse_args()


def update_readme(path: pathlib.Path, timestamp: str) -> bool:
    content = path.read_text(encoding="utf-8").splitlines()
    updated = False

    for idx, line in enumerate(content):
        if line.lower().startswith("last updated:"):
            if content[idx] != f"Last updated: {timestamp}":
                content[idx] = f"Last updated: {timestamp}"
                updated = True
            break
    else:
        content.append(f"\nLast updated: {timestamp}")
        updated = True

    if updated:
        path.write_text("\n".join(content) + "\n", encoding="utf-8")
    return updated


def main() -> int:
    args = parse_args()
    root: pathlib.Path = args.root
    timestamp = dt.datetime.now().strftime(args.format)

    if not root.exists():
        print(f"Root directory {root} does not exist")
        return 1

    readme_files = list(root.rglob("README.md"))
    if not readme_files:
        print("No README.md files found.")
        return 0

    for readme in readme_files:
        if update_readme(readme, timestamp):
            print(f"Updated {readme}")
        else:
            print(f"No change for {readme}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
