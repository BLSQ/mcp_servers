---
name: dhis2-indicators
description: Extract indicators and indicator groups from DHIS2. Use for indicator definitions, formulas, or indicator groups. Routed via dhis2 skill for general DHIS2 requests.
---

# DHIS2 Indicators

**Prerequisites**: Client setup from `dhis2` skill (assumes `dhis` is initialized)

## Dataframe API

```python
from openhexa.toolbox.dhis2 import dataframe
```

### get_indicators

| Parameter | Type | Required |
|-----------|------|----------|
| dhis2 | DHIS2 | Yes |
| filters | list[str] \| None | No |

**Returns** `pl.DataFrame`:

| Column | Type |
|--------|------|
| id | str |
| name | str |
| numerator | str |
| denominator | str |

### get_indicator_groups

| Parameter | Type | Required |
|-----------|------|----------|
| dhis2 | DHIS2 | Yes |
| filters | list[str] \| None | No |

**Returns** `pl.DataFrame`:

| Column | Type |
|--------|------|
| id | str |
| name | str |
| indicators | list[str] |

## JSON API

```python
indicators = dhis.meta.indicators()        # Returns list[dict]
groups = dhis.meta.indicator_groups()      # Returns list[dict]
```

## Indicator Types

| Type | Factor |
|------|--------|
| Percentage | 100 |
| Per 1000 | 1000 |
| Per 100000 | 100000 |
| Number | 1 |
