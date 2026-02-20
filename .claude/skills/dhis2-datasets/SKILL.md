---
name: dhis2-datasets
description: Extract datasets metadata from DHIS2. Use for dataset definitions, data entry forms, or reporting frequencies. Routed via dhis2 skill for general DHIS2 requests.
---

# DHIS2 Datasets

**Prerequisites**: Client setup from `dhis2` skill (assumes `dhis` is initialized)

## Dataframe API

```python
from openhexa.toolbox.dhis2 import dataframe
```

### get_datasets

| Parameter | Type | Required |
|-----------|------|----------|
| dhis2 | DHIS2 | Yes |
| filters | list[str] \| None | No |

**Returns** `pl.DataFrame`:

| Column | Type |
|--------|------|
| id | str |
| name | str |
| organisation_units | list[str] |
| data_elements | list[str] |
| indicators | list[str] |
| period_type | str |

## JSON API

```python
datasets = dhis.meta.datasets()  # Returns list[dict]
```

## Period Types

| period_type | Format | Example |
|-------------|--------|---------|
| Daily | YYYYMMDD | 20240115 |
| Weekly | YYYYWn | 2024W03 |
| Monthly | YYYYMM | 202401 |
| Quarterly | YYYYQn | 2024Q1 |
| SixMonthly | YYYYS1/S2 | 2024S1 |
| Yearly | YYYY | 2024 |
