#!/usr/bin/env python3
"""Add a metadata tag to notebook code cells identified by a substring.

Usage:
    python3 tools/tag_cell.py NOTEBOOK SUBSTRING [TAG]

TAG defaults to "raises-exception" (intentional error demos).
Use "skip-execution" for cells that must not be auto-executed (e.g. turtle
GUI demos).
"""
import sys

import nbformat


def main():
    if len(sys.argv) not in (3, 4):
        sys.exit(__doc__)
    path, substring = sys.argv[1], sys.argv[2]
    tag = sys.argv[3] if len(sys.argv) == 4 else "raises-exception"
    nb = nbformat.read(path, as_version=4)
    tagged = 0
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        if substring not in cell.get("source", ""):
            continue
        tags = cell.setdefault("metadata", {}).setdefault("tags", [])
        if tag not in tags:
            tags.append(tag)
            tagged += 1
    nbformat.write(nb, path)
    print(f"tagged {tagged} cell(s) in {path} with {tag!r}")


if __name__ == "__main__":
    main()
