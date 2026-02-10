---
name: jupyter-notebook
description: Create and manage Jupyter notebooks in OpenHEXA. Use when creating notebooks for data analysis, exploration, or reporting. Covers notebook structure, cell organization, where to save, and best practices.
---

# Jupyter Notebook

Guidelines for creating and managing Jupyter notebooks in OpenHEXA.

## Where to Save Notebooks

### Default Location

Save notebooks in the `notebooks/` folder unless the user specifies an alternative location.

```
workspace/
├── notebooks/           <- Default location for notebooks
│   ├── analysis.ipynb
│   └── exploration.ipynb
├── pipelines/
└── dashboards/
```

### Naming Conventions

```
# Good names
data_exploration.ipynb
dhis2_indicator_analysis.ipynb
monthly_report_2024.ipynb
tracker_data_quality.ipynb

# Avoid
Untitled.ipynb
test.ipynb
final_final_v2.ipynb
```

## Notebook Structure

### Format
A notebook is saved in a JSON format. Here is a valid example:
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Download Organisation Units - Sierra Leone\n",
    "\n",
    "**Purpose:** Download Organisation Units from the Sierra Leone DHIS2 instance.\n",
    "**Connection:** `play-sierra-dhis2`"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "from openhexa.sdk import workspace\n",
    "from openhexa.toolbox.dhis2 import DHIS2\n",
    "\n",
    "# Setup DHIS2 connection\n",
    "connection = workspace.dhis2_connection(\"play-sierra-dhis2\")\n",
    "dhis = DHIS2(connection)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Download all organisation units\n",
    "# We will fetch basic fields + geometry to have a complete dataset\n",
    "print(\"Fetching organisation units...\")\n",
    "org_units = dhis.meta.organisation_units(\n",
    "    fields=\"id,name,level,parent[id,name],geometry,openingDate,closedDate\"\n",
    ")\n",
    "print(f\"Downloaded {len(org_units)} organisation units.\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Convert to DataFrame\n",
    "df = pd.DataFrame(org_units)\n",
    "\n",
    "# Let's inspect the data first\n",
    "df.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Simple data processing to make it flatter\n",
    "# If 'parent' is a dict, extract ID and Name\n",
    "if 'parent' in df.columns:\n",
    "    df['parent_id'] = df['parent'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)\n",
    "    df['parent_name'] = df['parent'].apply(lambda x: x.get('name') if isinstance(x, dict) else None)\n",
    "    df.drop(columns=['parent'], inplace=True)\n",
    "\n",
    "df.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Save to CSV for reference\n",
    "output_filename = \"sierra_leone_org_units.csv\"\n",
    "df.to_csv(output_filename, index=False)\n",
    "print(f\"Saved to {output_filename}\")"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}

Note that the source field uses list of strings such as "line_code"\n". Reproduce that format when generating notebooks.
###
### Recommended Cell Order

```
1. Title & Description (Markdown)
2. Imports & Setup (Code)
3. Configuration/Parameters (Code)
4. Data Loading (Code)
5. Analysis Sections (Markdown + Code alternating)
6. Results/Summary (Markdown)
```

### Cell 1: Title & Description

```markdown
# Notebook Title

**Purpose:** Brief description of what this notebook does

**Data Sources:**
- Table: `my_table` from workspace database
- DHIS2: Connection `dhis2_connection_name`

**Author:** Name
**Date:** YYYY-MM-DD
```

### Cell 2: Imports & Setup

```python
# Standard imports
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Database
from sqlalchemy import create_engine

# Visualization
import matplotlib.pyplot as plt

# OpenHEXA (if using toolbox)
from openhexa.sdk import workspace
from openhexa.toolbox.dhis2 import DHIS2

# Settings
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)

print("Setup complete")
```

### Cell 3: Configuration

```python
# Parameters - easy to modify
START_DATE = "2024-01-01"
END_DATE = "2024-12-31"
ORG_UNIT_LEVEL = 2

# Database connection
DB_URL = os.environ.get("WORKSPACE_DATABASE_URL")
engine = create_engine(DB_URL)

# DHIS2 connection (if needed)
dhis2_conn = workspace.dhis2_connection("connection_name")
dhis = DHIS2(dhis2_conn, cache_dir=f"{workspace.files_path}/.cache")

print(f"Analysis period: {START_DATE} to {END_DATE}")
```

### Cell 4: Data Loading

```python
# Load data with clear variable names
df_raw = pd.read_sql("""
    SELECT * FROM source_table
    WHERE date >= %(start)s AND date <= %(end)s
""", engine, params={"start": START_DATE, "end": END_DATE})

print(f"Loaded {len(df_raw):,} rows")
df_raw.head()
```

## Best Practices

### 1. One Concept Per Cell

```python
# GOOD: One operation per cell
# Cell 1: Filter data
df_filtered = df_raw[df_raw["status"] == "active"]

# Cell 2: Aggregate
df_summary = df_filtered.groupby("category").agg({"value": "sum"})
```

```python
# BAD: Too much in one cell
df_filtered = df_raw[df_raw["status"] == "active"]
df_summary = df_filtered.groupby("category").agg({"value": "sum"})
df_summary.plot(kind="bar")
plt.savefig("chart.png")
```

### 2. Use Markdown Headers

```markdown
## 1. Data Exploration

### 1.1 Missing Values

### 1.2 Distribution Analysis

## 2. Data Transformation

## 3. Results
```

### 3. Show Progress & Shapes

```python
# After each transformation, show the result
df_clean = df_raw.dropna()
print(f"After cleaning: {len(df_clean):,} rows (dropped {len(df_raw) - len(df_clean):,})")
df_clean.shape
```

### 4. Document Decisions

```python
# Remove outliers using IQR method
# Rationale: Values > 3x IQR are likely data entry errors
Q1 = df["value"].quantile(0.25)
Q3 = df["value"].quantile(0.75)
IQR = Q3 - Q1

df_no_outliers = df[
    (df["value"] >= Q1 - 1.5 * IQR) &
    (df["value"] <= Q3 + 1.5 * IQR)
]
print(f"Removed {len(df) - len(df_no_outliers)} outliers")
```

### 5. Avoid Hardcoded Values

```python
# BAD
df = df[df["org_unit"] == "ImspTQPwCqd"]

# GOOD
TARGET_ORG_UNIT = "ImspTQPwCqd"  # Define in config cell
df = df[df["org_unit"] == TARGET_ORG_UNIT]
```

## Writing to Database

When writing results to the database, follow the `sql-tables` skill guidelines:

```python
from sqlalchemy import String, Float, Integer, DateTime

# 1. Check if table exists
from sqlalchemy import inspect
inspector = inspect(engine)
if "my_results" in inspector.get_table_names():
    print("WARNING: Table 'my_results' exists. Will use 'my_results_new'")
    table_name = "my_results_new"
else:
    table_name = "my_results"

# 2. Define explicit types
dtype_mapping = {
    "org_unit": String(11),
    "period": String(10),
    "value": Float,
    "created_at": DateTime,
}

# 3. Show proposed types for confirmation
print(f"Will write to table: {table_name}")
print("Column types:")
for col, dtype in dtype_mapping.items():
    print(f"  - {col}: {dtype}")
```

```python
# 4. Write after user confirmation
df_results.to_sql(
    name=table_name,
    con=engine,
    if_exists="replace",
    index=False,
    dtype=dtype_mapping
)
print(f"Written {len(df_results):,} rows to {table_name}")
```

## Visualizations


### Save Figures

```python
# Save to workspace files
output_path = f"{workspace.files_path}/figures/chart.png"
plt.savefig(output_path, dpi=150, bbox_inches="tight")
print(f"Saved to: {output_path}")
```

## Cleanup Cell (Optional)

```python
# Close connections at the end
engine.dispose()
print("Connections closed")
```



## Checklist

- [ ] Title and description in first cell
- [ ] Imports organized at top
- [ ] Configuration in dedicated cell
- [ ] Markdown headers for sections
- [ ] Progress/shape shown after transformations
- [ ] No hardcoded values in analysis cells
- [ ] Database writes follow sql-tables guidelines
- [ ] Saved in `notebooks/` folder (or user-specified)
