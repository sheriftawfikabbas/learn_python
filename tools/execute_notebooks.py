#!/usr/bin/env python3
"""Execute course notebooks to verify they run, optionally writing outputs back.

Usage:
    python3 tools/execute_notebooks.py [--all] [paths ...] [--write] [--timeout SECS]

Verification mode (default) exits non-zero if any code cell raises an
unexpected error. Cells tagged with "raises-exception" are expected to raise
and their errors are reported but do not fail the run.

With --write, the executed notebook (with fresh outputs and sequential
execution counts) is saved back over the original file.

input() calls are auto-answered so notebooks execute non-interactively.
"""
import argparse
import glob
import os
import sys

import nbformat
from nbclient import NotebookClient

AUTO_INPUT_PREAMBLE = (
    "def _auto_input(prompt=''):\n"
    "    if prompt:\n"
    "        print(prompt, end='')\n"
    "    print('5')\n"
    "    return '5'\n"
    "input = _auto_input\n"
)
AUTO_INPUT_TAG = "auto-input-preamble"


def iter_code_cells(nb):
    for i, cell in enumerate(nb.cells):
        if cell.cell_type == "code":
            yield i, cell


def has_raises_exception_tag(cell):
    return "raises-exception" in cell.get("metadata", {}).get("tags", [])


def cell_errors(cell):
    return [o for o in cell.get("outputs", []) if o.get("output_type") == "error"]


def has_skip_tag(cell):
    return "skip-execution" in cell.get("metadata", {}).get("tags", [])


def execute_notebook(path, write=False, timeout=120):
    """Execute one notebook. Returns (ok, messages)."""
    nb = nbformat.read(path, as_version=4)

    # Cells tagged skip-execution (GUI demos, turtle) are not executed.
    # Blank their source in the executed copy; restore before saving.
    skipped_sources = {}
    for idx, cell in iter_code_cells(nb):
        if has_skip_tag(cell):
            skipped_sources[idx] = cell["source"]
            cell["source"] = "pass  # skipped by execute_notebooks.py"

    preamble_tags = [AUTO_INPUT_TAG]
    preamble_cell = nbformat.v4.new_code_cell(AUTO_INPUT_PREAMBLE)
    preamble_cell.metadata["tags"] = preamble_tags
    nb.cells.insert(0, preamble_cell)

    client = NotebookClient(
        nb,
        timeout=timeout,
        kernel_name="python3",
        allow_errors=True,
        resources={"metadata": {"path": os.path.dirname(os.path.abspath(path))}},
    )
    try:
        client.execute()
    except Exception as exc:  # kernel-level failure
        return False, [f"KERNEL FAILURE: {exc}"]

    messages = []
    ok = True
    # Skip the preamble (index 0) when reporting; adjust for popped cell.
    for i, cell in iter_code_cells(nb):
        if i == 0:
            continue
        errors = cell_errors(cell)
        if not errors:
            continue
        if has_raises_exception_tag(cell):
            messages.append(
                f"cell {i - 1}: expected error (raises-exception): "
                f"{errors[0].get('ename', '')}"
            )
        else:
            src = cell.get("source", "").strip().splitlines()
            snippet = src[0][:60] if src else ""
            ok = False
            for err in errors:
                ename = err.get("ename", "")
                evalue = err.get("evalue", "").splitlines()
                evalue = evalue[0][:120] if evalue else ""
                messages.append(
                    f"cell {i - 1}: UNEXPECTED {ename}: {evalue}  << {snippet}"
                )

    if write:
        nb.cells.pop(0)
        # Restore skipped cells verbatim (unexecuted, no outputs).
        for idx, source in skipped_sources.items():
            cell = nb.cells[idx]
            cell["source"] = source
            cell["outputs"] = []
            cell["execution_count"] = None
        # Renumber execution counts sequentially.
        count = 1
        for _, cell in iter_code_cells(nb):
            if cell.get("execution_count") is not None:
                cell["execution_count"] = count
                count += 1
        nbformat.write(nb, path)

    return ok, messages


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--all", action="store_true",
                        help="Execute every .ipynb in the repo")
    parser.add_argument("--write", action="store_true",
                        help="Save fresh outputs back to the notebooks")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    paths = list(args.paths)
    if args.all:
        paths.extend(sorted(glob.glob("Class*/**/*.ipynb", recursive=True)))
        paths.extend(sorted(glob.glob("*.ipynb")))
    if not paths:
        parser.error("no notebooks specified")

    failures = []
    for path in paths:
        ok, messages = execute_notebook(path, write=args.write,
                                        timeout=args.timeout)
        status = "PASS" if ok else "FAIL"
        print(f"{status}: {path}")
        for msg in messages:
            print(f"      {msg}")
        if not ok:
            failures.append(path)

    if failures:
        print(f"\n{len(failures)} notebook(s) failed:")
        for path in failures:
            print(f"  - {path}")
        sys.exit(1)
    print(f"\nAll {len(paths)} notebook(s) executed successfully.")


if __name__ == "__main__":
    main()
