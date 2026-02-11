---
name: jupyter-notebook
description: Create Jupyter notebooks with correct JSON format. CRITICAL: source arrays must use single-line strings without \n , never multi-line strings.
---

# Jupyter Notebook Format

## CRITICAL: Source Field Format

The `source` field is a list of strings.

### ❌ BAD - Multi-line strings (INVALID JSON):
```json
"source": [
    "# Title
",
    "Some text \n end of the sentence ",
    "More text
"
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

The reason behind this is that when rendering a JSON file from the LLM text, all "\n" will be used as new line, breaking the JSON synthax of just instead writing the character "\n".
So never use \n or \t. The only case is to use \\n or \\t in strings inside code lines.

## Save Location

Save notebooks in `notebooks/` folder with descriptive names like `data_exploration.ipynb`.
