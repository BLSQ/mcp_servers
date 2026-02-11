---
name: jupyter-notebook
description: Create Jupyter notebooks with correct JSON format. CRITICAL: Never emit literal newlines in JSON. Emit \\n if needed. Prefer single quotes in Python code to reduce JSON escaping
---

# Jupyter Notebook Format

## CRITICAL: Source Field Format

The `source` field is a list of strings.

### ❌ BAD - Multi-line strings (INVALID JSON):
```json
"source": [
    "# Title\n",
    "Some text \n end of the sentence ",
    "More text\n"
]
```

### ✅ CORRECT - Single-line strings with \n:
```json
"source": [
    "# Title",
    "Some text \\n end of the sentence",
    "More text"
]
```

## Minimal Valid Notebook

```json
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Notebook Title",
    "**Purpose:** Description here"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd",
    "print('Hello')"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
  "language_info": {"name": "python", "version": "3.8.5"}
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
```

1) Source items must be valid JSON strings

Every cells[i].source[j] must be a JSON string with:

No literal newline characters inside it.

Any newline semantics must be represented as either:

- a dedicated line string ending with \\n, or

- an empty line string equal to "\\n" (not a literal blank line in the JSON file).

2) Always JSON-escape content inside source strings

Inside each source string:

- Any " in Python code must be escaped for JSON as \", or prefer single quotes in Python to avoid it.

- Backslashes must be preserved correctly (e.g., \\n if you want Python to see \n).

3) Represent blank lines explicitly

If you want a blank line between code lines, use:

"\\n" as its own array element, or end previous line with \\n and insert another "\\n" line.

## Save Location

Save notebooks in `notebooks/` folder with descriptive names like `data_exploration.ipynb`.
