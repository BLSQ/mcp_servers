---
name: dhis2-data-elements
description: Extract data elements and data element groups from DHIS2. Use for data element metadata, groups, or category option combos. Routed via dhis2 skill for general DHIS2 requests.
---

# DHIS2 Data Elements

**Prerequisites**: Client setup from `dhis2` skill (assumes `dhis` is initialized)

## Dataframe API

```python
from openhexa.toolbox.dhis2 import dataframe
```

### get_data_elements

| Parameter | Type | Required |
|-----------|------|----------|
| dhis2 | DHIS2 | Yes |
| filters | list[str] \| None | No |

**Returns** `pl.DataFrame`:

| Column | Type |
|--------|------|
| id | str |
| name | str |
| value_type | str |

### get_data_element_groups

| Parameter | Type | Required |
|-----------|------|----------|
| dhis2 | DHIS2 | Yes |
| filters | list[str] \| None | No |

**Returns** `pl.DataFrame`:

| Column | Type |
|--------|------|
| id | str |
| name | str |
| data_elements | list[str] |

### get_category_option_combos

| Parameter | Type | Required |
|-----------|------|----------|
| dhis2 | DHIS2 | Yes |
| filters | list[str] \| None | No |

**Returns** `pl.DataFrame`:

| Column | Type |
|--------|------|
| id | str |
| name | str |

### join_object_names

| Parameter | Type | Required |
|-----------|------|----------|
| df | pl.DataFrame | Yes |
| data_elements | pl.DataFrame \| None | No |
| category_option_combos | pl.DataFrame \| None | No |

**Returns** `pl.DataFrame` with added columns: data_element_name, category_option_combo_name.

## JSON API

```python
data_elements = dhis.meta.data_elements()  # list[dict]
groups = dhis.meta.data_element_groups()   # list[dict]
cocs = dhis.meta.category_option_combos()  # list[dict]
```
