---
name: jupyter-notebook
description: Create Jupyter notebooks with correct JSON format. CRITICAL: source arrays must use single-line strings with \n, never multi-line strings.
---

# Jupyter Notebook Format

## CRITICAL: Source Field Format

The `source` field is a list of strings. Each string MUST be on a single line with `\n` for newlines.

### ❌ BAD - Multi-line strings (INVALID JSON):
```json
"source": [
    "# Title
",
    "Some text
",
    "More text"
]
```

### ✅ CORRECT - Single-line strings with \n:
```json
"source": [
    "# Title\n",
    "\n",
    "Some text\n",
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
    "# Notebook Title\n",
    "\n",
    "**Purpose:** Description here"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "\n",
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

## Save Location

Save notebooks in `notebooks/` folder with descriptive names like `data_exploration.ipynb`.
