# Basics of Python course

A beginner, notebook-based course in programming with Python — no prior
programming experience assumed. Each class is a Jupyter notebook lesson
(`ClassNN/ClassN.ipynb`) with a matching exercise worksheet
(`ClassNN/LabN.ipynb`).

## How to use this course

Work through the classes in order; each lab assumes only what has been
taught so far. Inside a class, follow the **GOTO Lab exercises X-Y**
callouts — they tell you when you are ready for which exercises.

- **Course introduction and outcomes:** `CourseIntroduction.ipynb`
- **Sample exam:** `SampleExam.ipynb`

You can run the notebooks without installing anything by uploading them to
[Google Colab](https://colab.research.google.com/), or run them locally:

```bash
pip install jupyter
pip install -r requirements.txt   # libraries used in Classes 9-11
jupyter notebook
```

## Course outline

| Class | Topic |
| --- | --- |
| 1 | Introduction to Python: print, data types, variables, operators |
| 2 | Collection data types: lists, tuples, sets, dictionaries |
| 3 | Control statements: `if`, loops, and the turtle |
| 4 | Functions |
| 5 | Scripts, modules and file operations |
| 6 | Algorithms: complexity, search, sort, recursion |
| 7 | Object-oriented programming 1 |
| 8 | Object-oriented programming 2 |
| 9 | API programming with `requests` and JSON |
| 10 | Web scraping with `BeautifulSoup` |
| 11 | Cryptography: hashing, symmetric and asymmetric encryption |

## For maintainers

Every notebook is executable top-to-bottom on Python 3.10+. To check (and to
regenerate recorded cell outputs), use the tooling in `tools/`:

```bash
pip install nbformat nbclient ipykernel -r requirements.txt
python3 tools/execute_notebooks.py --all            # verify all notebooks run
python3 tools/execute_notebooks.py --all --write    # ... and save fresh outputs
```

The runner executes each notebook in a fresh kernel (in the notebook's own
folder, answering `'5'` to any `input()` call). Two cell metadata tags
control execution:

- `raises-exception` — the cell is an *intentional* error demonstration
- `skip-execution` — the cell is not auto-executed (e.g. turtle GUI demos)

Add a tag to a cell with:

```bash
python3 tools/tag_cell.py NOTEBOOK.ipynb "substring of the cell" raises-exception
```

## Requirements

Python 3.10+. Most classes need only the standard library. Classes 9-11 also
use the packages in `requirements.txt` (`requests`, `beautifulsoup4`,
`cryptography`, `rsa`, `numpy`).
