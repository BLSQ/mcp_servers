---
name: jupyter-notebook
description: Create Jupyter notebooks with correct JSON format.
---

# IPYNB Notebook Skill

You are an expert at creating, editing, and manipulating Jupyter notebooks programmatically.

## ⚠️ CRITICAL: NEVER Write Raw Notebook JSON

**DO NOT** write `.ipynb` files by directly outputting JSON. LLMs frequently produce invalid JSON by turning `\n` escape sequences into literal newlines, which breaks the file.

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
    """Create a markdown cell. source_lines is a list of strings (no \\n needed, added automatically)."""
    source = [line + "\n" for line in source_lines[:-1]] + [source_lines[-1]] if source_lines else []
    return {"cell_type": "markdown", "source": source, "metadata": {"id": cell_id}}

def code_cell(cell_id, source_lines):
    """Create a code cell. source_lines is a list of strings (no \\n needed, added automatically)."""
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

### Step 2: Run the script, then validate

After generating the notebook, **always** run this validation:

```python
import json, sys

path = "notebook.ipynb"
try:
    with open(path, "r") as f:
        nb = json.load(f)
    assert "cells" in nb, "Missing 'cells' key"
    assert nb.get("nbformat") == 4, "Bad nbformat"
    for i, cell in enumerate(nb["cells"]):
        assert "cell_type" in cell, f"Cell {i}: missing cell_type"
        assert "source" in cell, f"Cell {i}: missing source"
        assert isinstance(cell["source"], list), f"Cell {i}: source must be a list"
        for j, line in enumerate(cell["source"]):
            assert isinstance(line, str), f"Cell {i}, line {j}: not a string"
        if cell["cell_type"] == "code":
            assert "outputs" in cell, f"Cell {i}: code cell missing outputs"
    print(f"✓ Valid notebook: {len(nb['cells'])} cells")
except json.JSONDecodeError as e:
    print(f"✗ INVALID JSON: {e}", file=sys.stderr)
    sys.exit(1)
except AssertionError as e:
    print(f"✗ INVALID STRUCTURE: {e}", file=sys.stderr)
    sys.exit(1)
```

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
- [ ] Validation script ran successfully after generation
- [ ] All cells have unique IDs
- [ ] Markdown cells have proper headers and formatting
- [ ] Code cells are logically ordered
- [ ] Imports are at the top or in a setup cell
- [ ] Config values use Colab form fields where appropriate
- [ ] Error handling for common failures
- [ ] Clear output messages (✓ for success, ⚠️ for warnings)
- [ ] Section dividers between major parts



## Save Location

Save notebooks in `workspace/notebooks/` folder with descriptive names like `data_exploration.ipynb`.
