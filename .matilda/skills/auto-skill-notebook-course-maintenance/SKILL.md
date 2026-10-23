---
name: notebook-course-maintenance
description: How to safely edit, restructure and verify the Jupyter lesson notebooks in this repo (executor tooling, tags, and the traps that silently break notebook surgery)
source: auto-skill
extracted_at: '2026-10-23T01:22:21.936Z'
---

# Notebook course maintenance

This repo is a Jupyter-notebook Python course (11 `Class` lessons + `Lab` worksheets).
The durable workflow for editing lessons safely and proving they run:

## Verify/execute notebooks

```bash
python3 tools/execute_notebooks.py --all            # execute every notebook, report errors
python3 tools/execute_notebooks.py --all --write    # ... and save fresh outputs/execution counts
python3 tools/tag_cell.py NOTEBOOK "substring" [TAG]  # tag cells (default tag: raises-exception)
```

Conventions the executor honours (also respected by Jupyter tooling):

- `raises-exception` — *intentional* error demo (e.g. `TypeError: 'tuple' object does not
  support item assignment`). Its error is reported but doesn't fail the run, and its error
  output is preserved as course content.
- `skip-execution` — never auto-executed (GUI/turtle, blocking cells); source kept verbatim.

Executor facts worth knowing (learned by breaking them):

- It launches the kernel with `cwd = the notebook's own folder`
  (`resources={"metadata":{"path":...}}`), so local imports like `import abc_module` work.
  Files written by notebooks land next to the notebook, not at the repo root.
- `input()` is auto-answered `'5'` by **shadowing `input` in the notebook's global
  namespace** — do NOT try patching `builtins.input`; ipykernel re-overrides it per
  execution and the patch silently no-ops.
- nbclient does **not** regenerate outputs for empty code cells. If you blank a lab
  solution cell, also clear its `outputs`/`execution_count` or the stale (possibly error)
  output lingers and will be misread as a live failure.

## Editing notebooks

- Use the `notebook_edit` tool only for isolated single replaces. After **any insert** the
  tool invalidates its read cache and subsequent edits in the same batch fail with
  "notebook has not been fully read". For inserts/deletes/reorders/multi-cell surgery,
  script it with `nbformat` instead:

  ```python
  import nbformat
  nb = nbformat.read(p, as_version=4)
  nb.cells.insert(i, nbformat.v4.new_code_cell(src))  # or del / reassign / nb.cells[i:i+1] = [...]
  nbformat.write(nb, p)
  ```

- Locate cells by **source snippet assertions**, not fixed indices; indices shift as you
  work and a stale index means you edit the wrong cell or crash.
- These lessons have giant "blob" markdown cells holding several `##` sections. A
  phrase-replacement that targets text *inside* a blob either silently fails to match
  (e.g. `source.startswith("## X")` when the section is mid-cell) or — worse — wholesale
  replaces the blob's source and deletes neighbouring sections. **After every scripted
  edit, audit:** dump headings (`line.startswith('## ')`), grep for the old text, and
  re-run the executor. Twice in this overhaul a "successful" edit silently dropped a
  section (lost `# Class 11` title, lost `## 8.3 Polymorphism`) and was only caught by a
  heading audit; section text was recovered from `git show HEAD:file`.

## Course-structure invariants to keep

- Every `ClassN.ipynb`: `# Class N:` title, `## Learning outcomes` (must match actual
  content), `## N.M` numbered sections, `**GOTO Lab exercises X-Y**` callouts that map
  **exactly** to existing exercises in the sibling `LabN.ipynb`, trailing `## Summary`.
- Labs are worksheets: `## Exercise k:` sequentially numbered, a precise task with an
  example run/expected output, one **empty** code cell each. No solutions in labs.
- Exercises in LabN may only use concepts from Classes 1..N.
- Error-demo cells must be tagged `raises-exception` before the executor can pass.
- Class notebooks must run offline-decisively: either deterministic code, or clearly
  noted network-dependent cells (Classes 9/10 hit live APIs/sites).

`requirements.txt` covers the notebook deps (requests, beautifulsoup4, cryptography,
rsa, numpy); the executor tooling needs `nbformat nbclient ipykernel` (pip).
