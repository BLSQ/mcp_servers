---
name: dhis2-data-values
description: Extract raw data values from DHIS2 using the dataValueSets API. Use for actual submitted data values, not aggregated analytics. ALWAYS use with dhis2-query-optimization skill. Routed via dhis2 skill for general DHIS2 requests.
---

# DHIS2 Data Values

**Prerequisites**: Client setup from `dhis2` skill + `dhis2-query-optimization` for large queries

## Dataframe API

```python
from datetime import datetime
from openhexa.toolbox.dhis2 import dataframe
```

### extract_dataset

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| dhis2 | DHIS2 | Yes | |
| dataset | str | Yes | Dataset UID |
| start_date | datetime \| None | No | Use with end_date OR use periods |
| end_date | datetime \| None | No | Use with start_date OR use periods |
| periods | list[str] \| None | No | e.g., ["202101", "202102"] |
| org_units | list[str] \| None | No | Use org_units OR org_unit_groups |
| org_unit_groups | list[str] \| None | No | Use org_units OR org_unit_groups |
| include_children | bool | No | Default: False |
| last_updated | datetime \| None | No | Filter by last updated |

### extract_data_element_groups

| Parameter | Type | Required |
|-----------|------|----------|
| dhis2 | DHIS2 | Yes |
| data_element_groups | list[str] | Yes |
| *(other params same as extract_dataset)* | | |

### extract_data_elements

| Parameter | Type | Required |
|-----------|------|----------|
| dhis2 | DHIS2 | Yes |
| data_elements | list[str] | Yes |
| *(other params same as extract_dataset)* | | |

**All extract functions return** `pl.DataFrame`:

| Column | Type |
|--------|------|
| data_element_id | str |
| period | str |
| organisation_unit_id | str |
| category_option_combo_id | str |
| attribute_option_combo_id | str |
| value | str |
| created | datetime[ms, UTC] |
| last_updated | datetime[ms, UTC] |

### import_data_values

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| dhis2 | DHIS2 | Yes | |
| data | pl.DataFrame | Yes | See required columns below |
| org_units_mapping | dict \| None | No | {old_uid: new_uid} |
| data_elements_mapping | dict \| None | No | {old_uid: new_uid} |
| category_option_combos_mapping | dict \| None | No | {old_uid: new_uid} |
| attribute_option_combos_mapping | dict \| None | No | {old_uid: new_uid} |
| import_strategy | Literal["CREATE", "UPDATE", "CREATE_AND_UPDATE", "DELETE"] | No | Default: "CREATE" |
| dry_run | bool | No | Default: True |

**Required input DataFrame columns** (all str):
- data_element_id
- period
- organisation_unit_id
- category_option_combo_id
- attribute_option_combo_id
- value

**Returns** `dict`: `{"imported": N, "updated": N, "ignored": N, "deleted": N}`

## JSON API

```python
data = dhis.data_value_sets.get(
    datasets=["uid"],
    org_units=["uid"],
    start_date="2024-01-01",
    end_date="2024-03-31"
)  # Returns list[dict]
```
