---
name: dhis2-organisation-units
description: Extract organisation units and groups from DHIS2. Use for org unit hierarchy, metadata, levels, or groups. Routed via dhis2 skill for general DHIS2 requests.
---

# DHIS2 Organisation Units

**Prerequisites**: Client setup from `dhis2` skill (assumes `dhis` is initialized)

## Dataframe API

```python
from openhexa.toolbox.dhis2 import dataframe
```

### get_organisation_units

| Parameter | Type | Required |
|-----------|------|----------|
| dhis2 | DHIS2 | Yes |
| max_level | int \| None | No |
| filters | list[str] \| None | No |

**Returns** `pl.DataFrame`:

| Column | Type |
|--------|------|
| id | str |
| name | str |
| level | int |
| opening_date | datetime |
| closed_date | datetime |
| level_{n}_id | str |
| level_{n}_name | str |
| geometry | str |

### get_organisation_unit_levels

| Parameter | Type | Required |
|-----------|------|----------|
| dhis2 | DHIS2 | Yes |

**Returns** `pl.DataFrame`:

| Column | Type |
|--------|------|
| id | str |
| name | str |
| level | int |

### get_organisation_unit_groups

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

### extract_organisation_unit_attributes

| Parameter | Type | Required |
|-----------|------|----------|
| dhis2 | DHIS2 | Yes |

**Returns** `pl.DataFrame`:

| Column | Type |
|--------|------|
| organisation_unit_id | str |
| organisation_unit_name | str |
| attribute_id | str |
| attribute_name | str |
| value | str |

### get_attributes

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
| organisation_units | pl.DataFrame \| None | No |

**Returns** `pl.DataFrame` with added level_{n}_id and level_{n}_name columns.

## JSON API

```python
org_units = dhis.meta.organisation_units()       # Returns list[dict]
groups = dhis.meta.organisation_unit_groups()    # Returns list[dict]
levels = dhis.meta.organisation_unit_levels()    # Returns list[dict]
```
