---
name: jupyter-notebook
description: Create Jupyter notebooks with correct JSON format.
---

# IPYNB Notebook Skill

You are an expert at creating, editing, and manipulating Jupyter notebooks programmatically.

## ⚠️ CRITICAL: NEVER Write Raw Notebook JSON

**DO NOT** write `.ipynb` files by directly outputting JSON. LLMs frequently produce invalid JSON by turning `\n` escape sequences into literal backslash-n text, which breaks the file (all code appears on one line).

**ALWAYS** generate notebooks using a **Python script** that builds the notebook as a Python data structure and serializes it with `json.dump()`. This guarantees valid JSON output.

## Creating Notebooks — The Only Correct Way

### Step 1: Write a Python generator script

```python
import json

notebook = {
    "nbformat": 4,
    "nbformat_minor": 0,
    "metadata": {
        "colab": {"provenance": []},
        "kernelspec": {"name": "python3", "display_name": "Python 3"},
        "language_info": {"name": "python"}
    },
    "cells": []
}

def md_cell(cell_id, source_lines):
    """Create a markdown cell. source_lines is a list of plain strings (no \\n needed)."""
    source = [line + "\n" for line in source_lines[:-1]] + [source_lines[-1]] if source_lines else []
    return {"cell_type": "markdown", "source": source, "metadata": {"id": cell_id}}

def code_cell(cell_id, source_lines):
    """Create a code cell. source_lines is a list of plain strings (no \\n needed)."""
    source = [line + "\n" for line in source_lines[:-1]] + [source_lines[-1]] if source_lines else []
    return {
        "cell_type": "code",
        "source": source,
        "metadata": {"id": cell_id},
        "execution_count": None,
        "outputs": []
    }

# --- Build cells ---

notebook["cells"].append(md_cell("intro", [
    "# My Notebook",
    "",
    "Description here."
]))

notebook["cells"].append(code_cell("imports", [
    "import torch",
    "import numpy as np",
    "",
    "print('Ready!')"
]))

# --- Write notebook ---

with open("notebook.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2, ensure_ascii=False)

print("✓ Notebook created successfully")
```

### Step 2: ALWAYS validate and auto-fix after generation

After generating **any** notebook, **always** run this validation and auto-fix script. This catches the most common LLM failure: writing literal `\n` text instead of actual newline characters.

```python
import json, sys

path = "notebook.ipynb"

# --- Load ---
try:
    with open(path, "r") as f:
        nb = json.load(f)
except json.JSONDecodeError as e:
    print(f"✗ INVALID JSON: {e}", file=sys.stderr)
    sys.exit(1)

# --- Structural validation ---
assert "cells" in nb, "Missing 'cells' key"
assert nb.get("nbformat") == 4, "Bad nbformat"

fixed = False
for i, cell in enumerate(nb["cells"]):
    assert "cell_type" in cell, f"Cell {i}: missing cell_type"
    assert "source" in cell, f"Cell {i}: missing source"
    assert isinstance(cell["source"], list), f"Cell {i}: source must be a list"

    if cell["cell_type"] == "code":
        if "outputs" not in cell:
            cell["outputs"] = []
            fixed = True
        if "execution_count" not in cell:
            cell["execution_count"] = None
            fixed = True

    # --- AUTO-FIX: literal \\n → actual \n ---
    # This is the #1 failure mode for LLMs generating notebooks.
    # They write the two characters \ and n instead of a real newline.
    new_source = []
    for line in cell["source"]:
        assert isinstance(line, str), f"Cell {i}: source line is not a string"
        if "\\n" in line:
            fixed = True
            line = line.replace("\\n", "\n")
        new_source.append(line)
    cell["source"] = new_source

# --- Write back if fixes were applied ---
if fixed:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)
    print(f"⚠️ Auto-fixed notebook ({len(nb['cells'])} cells) — literal \\\\n replaced with real newlines")
else:
    print(f"✓ Valid notebook: {len(nb['cells'])} cells, no fixes needed")
```

**This validation + auto-fix step is MANDATORY. Never skip it.**

## Helper Functions Reference

Use these helper functions in every notebook generation script:

```python
def md_cell(cell_id, lines):
    """Markdown cell from a list of plain strings (one per line)."""
    src = [l + "\n" for l in lines[:-1]] + [lines[-1]] if lines else []
    return {"cell_type": "markdown", "source": src, "metadata": {"id": cell_id}}

def code_cell(cell_id, lines):
    """Code cell from a list of plain strings (one per line)."""
    src = [l + "\n" for l in lines[:-1]] + [lines[-1]] if lines else []
    return {
        "cell_type": "code", "source": src,
        "metadata": {"id": cell_id}, "execution_count": None, "outputs": []
    }
```

**Why plain strings?** You pass `["import torch", "import numpy"]` — the helper adds `\n` between lines programmatically. This eliminates the most common source of invalid JSON.

## Editing Existing Notebooks

```python
import json

with open('notebook.ipynb', 'r') as f:
    nb = json.load(f)

# Find and modify cell by ID
for cell in nb['cells']:
    if cell.get('metadata', {}).get('id') == 'target_id':
        cell['source'] = ["new line 1\n", "new line 2"]
        break

# Insert a cell at position
nb['cells'].insert(2, code_cell("new_cell", ["print('inserted')"]))

# Delete a cell by ID
nb['cells'] = [c for c in nb['cells'] if c.get('metadata', {}).get('id') != 'delete_me']

with open('notebook.ipynb', 'w') as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)
```

## Colab Form Fields

```python
code_cell("config", [
    '#@title Configuration { display-mode: "form" }',
    '',
    'MODEL_NAME = "gpt2"  #@param {type:"string"}',
    'BATCH_SIZE = 32  #@param {type:"integer"}',
    'USE_GPU = True  #@param {type:"boolean"}',
    'MODE = "A"  #@param ["A", "B", "C"]',
])
```

## Notebook Patterns

### Setup Cell
```python
code_cell("setup", [
    "#@title Setup",
    "!pip install -q package1 package2",
    "",
    "import package1",
    "import package2",
    "",
    "print('✓ Setup complete')",
])
```

### Progress Display
```python
code_cell("train_loop", [
    "from tqdm.notebook import tqdm",
    "",
    "for i in tqdm(range(100)):",
    "    # work",
    "    pass",
])
```

## Quality Checklist

Before finalizing a notebook:
- [ ] Generated via Python script with `json.dump()` — **never raw JSON**
- [ ] Validation + auto-fix script ran successfully after generation
- [ ] All cells have unique IDs
- [ ] Markdown cells have proper headers and formatting
- [ ] Code cells are logically ordered
- [ ] Imports are at the top or in a setup cell
- [ ] Config values use Colab form fields where appropriate
- [ ] Error handling for common failures
- [ ] Clear output messages (✓ for success, ⚠️ for warnings)
- [ ] Section dividers between major parts