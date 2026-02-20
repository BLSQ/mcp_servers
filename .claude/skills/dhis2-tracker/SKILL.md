---
name: dhis2-tracker
description: Extract individual-level/case-based data from DHIS2 Tracker. Use for tracked entities, enrollments, events, or relationships. Routed via dhis2 skill for general DHIS2 requests.
---

# DHIS2 Tracker

**Prerequisites**: Client setup from `dhis2` skill (assumes `dhis` is initialized)

## Dataframe API

```python
from openhexa.toolbox.dhis2 import dataframe
```

### extract_events

| Parameter | Type | Required |
|-----------|------|----------|
| dhis2 | DHIS2 | Yes |
| program_id | str | Yes |
| org_unit_parents | list[str] | Yes |
| occurred_after | str \| None | No |
| occurred_before | str \| None | No |

**Returns** `pl.DataFrame` (one row per event data value):

| Column | Type |
|--------|------|
| event_id | str |
| status | str |
| program_id | str |
| program_stage_id | str |
| organisation_unit_id | str |
| occurred_at | datetime[ms, UTC] |
| deleted | bool |
| attribute_option_combo_id | str |
| data_element_id | str |
| value | str |

### get_programs

| Parameter | Type | Required |
|-----------|------|----------|
| dhis2 | DHIS2 | Yes |
| filters | list[str] \| None | No |

**Returns** `pl.DataFrame`:

| Column | Type |
|--------|------|
| id | str |
| name | str |
| program_type | str |

### get_program_stages

| Parameter | Type | Required |
|-----------|------|----------|
| dhis2 | DHIS2 | Yes |
| filters | list[str] \| None | No |

**Returns** `pl.DataFrame`:

| Column | Type |
|--------|------|
| program_stage_id | str |
| program_stage_name | str |
| program_id | str |
| program_name | str |

### get_program_data_elements

| Parameter | Type | Required |
|-----------|------|----------|
| dhis2 | DHIS2 | Yes |
| filters | list[str] \| None | No |

**Returns** `pl.DataFrame`:

| Column | Type |
|--------|------|
| program_stage_id | str |
| program_stage_name | str |
| program_id | str |
| program_name | str |
| valid_data_elements | list[str] |
| compulsory_data_elements | list[str] |

### get_tracked_entity_types

| Parameter | Type | Required |
|-----------|------|----------|
| dhis2 | DHIS2 | Yes |
| filters | list[str] \| None | No |

**Returns** `pl.DataFrame`:

| Column | Type |
|--------|------|
| id | str |
| name | str |

## Tracked Entities, Enrollments, Relationships

No specific toolbox functions yet developed. Use your own knowledge of the DHIS2 Tracker API.
