---
name: dhis2-analytics
description: Query aggregated analytics data from DHIS2. Use for calculated/aggregated values, indicator values, or cross-dimensional analysis. ALWAYS use with dhis2-query-optimization skill. Routed via dhis2 skill for general DHIS2 requests.
---

# DHIS2 Analytics

**Prerequisites**: Client setup from `dhis2` skill + `dhis2-query-optimization` for large queries

## Dataframe API

```python
from openhexa.toolbox.dhis2 import dataframe
```

### extract_analytics

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| dhis2 | DHIS2 | Yes | |
| periods | list[str] | Yes | e.g., ["2021", "202401"] |
| data_elements | list[str] \| None | No | Cannot mix with indicators |
| data_element_groups | list[str] \| None | No | Cannot mix with indicators |
| indicators | list[str] \| None | No | Cannot mix with data_elements |
| indicator_groups | list[str] \| None | No | Cannot mix with data_elements |
| org_units | list[str] \| None | No | At least one spatial dim required |
| org_unit_groups | list[str] \| None | No | At least one spatial dim required |
| org_unit_levels | list[int] \| None | No | At least one spatial dim required |

**Returns** `pl.DataFrame`:

For data elements:

| Column | Type |
|--------|------|
| data_element_id | str |
| category_option_combo_id | str |
| organisation_unit_id | str |
| period | str |
| value | str |

For indicators (no category_option_combo_id):

| Column | Type |
|--------|------|
| indicator_id | str |
| organisation_unit_id | str |
| period | str |
| value | str |

## JSON API

```python
# Data elements
data = dhis.analytics.get(
    data_elements=["uid"],
    org_units=["uid"],
    periods=["202401"]
)  # Returns list[dict]

# Indicators - ALWAYS use include_cocs=False
data = dhis.analytics.get(
    indicators=["uid"],
    org_units=["uid"],
    periods=["2024"],
    include_cocs=False  # MANDATORY for indicators
)
```
