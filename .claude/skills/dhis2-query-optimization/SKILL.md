---
name: dhis2-query-optimization
description: ALWAYS use this skill when querying DHIS2 analytics or data values. Provides MAX_* tuning for batch sizes, children=True expansion, and server error handling. Prevents URL length limits, server timeouts, and memory issues.
---

# DHIS2 Query Optimization

The OpenHEXA toolbox **already handles batching automatically** via internal MAX_* attributes. This skill explains how to tune those attributes and handle edge cases.

**Prerequisites**: Client setup from `dhis2` skill (assumes `dhis` is initialized)

## How Toolbox Batching Works

The toolbox splits large queries into batches based on these instance attributes:

**DataValueSets** (`dhis.data_value_sets`):
```python
MAX_DATA_ELEMENTS = 50  # Data elements per batch
MAX_ORG_UNITS = 50      # Org units per batch
MAX_PERIODS = 5         # Periods per batch
DATE_RANGE_DELTA = relativedelta(years=1)  # Date range chunk size
```

**Analytics** (`dhis.analytics`):
```python
MAX_DX = 50             # Data elements/indicators per batch
MAX_ORG_UNITS = 50      # Org units per batch
MAX_PERIODS = 1         # Periods per batch (conservative default)
```

## Tuning MAX_* Attributes

You can modify these attributes before querying:

```python
# Increase batch sizes for faster servers
dhis.analytics.MAX_ORG_UNITS = 100
dhis.analytics.MAX_PERIODS = 4
dhis.data_value_sets.MAX_ORG_UNITS = 100
dhis.data_value_sets.MAX_PERIODS = 12
```

**When to increase MAX_* values:**
- Fast, well-resourced DHIS2 server
- Fewer total API calls needed
- Reduce extraction time

**When to decrease MAX_* values:**
- Slow or overloaded server
- Getting timeout errors (502, 504)
- Getting server errors (500)

## Handling Server Errors (50X)

If you encounter **HTTP 502, 504, or timeout errors**, the batch size is too large for the server:

```python
# Server struggling with default values
# Reduce batch sizes:
dhis.analytics.MAX_ORG_UNITS = 25      # Was 50
dhis.analytics.MAX_PERIODS = 1         # Was 1 (already minimal)
dhis.analytics.MAX_DX = 25             # Was 50

dhis.data_value_sets.MAX_ORG_UNITS = 25
dhis.data_value_sets.MAX_PERIODS = 3   # Was 5
dhis.data_value_sets.MAX_DATA_ELEMENTS = 25
```

**Error → Action mapping:**

| Error | Meaning | Action |
|-------|---------|--------|
| HTTP 502 Bad Gateway | Server overwhelmed | Reduce all MAX_* by 50% |
| HTTP 504 Gateway Timeout | Query took too long | Reduce MAX_ORG_UNITS and MAX_PERIODS |
| HTTP 500 Internal Error | Server crashed | Reduce MAX_* significantly, try MAX_*=10 |
| Connection timeout | Network/server issue | Add retry logic + reduce batch size |

## The `children=True` Problem

**This is the one case where MAX_* tuning alone is NOT sufficient.**

When you pass `children=True`, the DHIS2 **server** expands org units, but the **toolbox** doesn't know how many children exist:

```python
# Toolbox sees: 1 org unit → creates 1 batch
# Server sees: 1 org unit + children=True → expands to 5,000+ org units!
df = dataframe.extract_analytics(
    dhis,
    data_elements=["de1"],
    org_units=["national_uid"],  # Just 1
    periods=["202401"],
    children=True  # ⚠️ Server-side expansion, toolbox can't batch
)
```

**Solution: Expand org units explicitly BEFORE querying:**

```python
from openhexa.toolbox.dhis2 import dataframe

# 1. Get org unit counts to understand the pyramid
counts = get_org_unit_counts_by_level(dhis)
max_level = max(counts.keys())
total_org_units = sum(counts.values())

print(f"Org unit pyramid: {counts}")
print(f"Total org units: {total_org_units}")

# 2. If total exceeds MAX_ORG_UNITS, expand explicitly
if total_org_units > dhis.analytics.MAX_ORG_UNITS:
    # Get explicit list - toolbox can batch this correctly
    org_units_df = dataframe.get_organisation_units(dhis, max_level=max_level)
    all_org_unit_ids = org_units_df["id"].to_list()

    df = dataframe.extract_analytics(
        dhis,
        data_elements=["de1"],
        org_units=all_org_unit_ids,  # Explicit list
        periods=["202401"]
        # NO children=True needed
    )
else:
    # Small pyramid - children=True is safe
    df = dataframe.extract_analytics(
        dhis,
        data_elements=["de1"],
        org_units=["national_uid"],
        periods=["202401"],
        children=True  # Safe when total < MAX_ORG_UNITS
    )
```

## Decision Tree

```
Do you need descendants of a parent org unit?
│
├─► NO: Just tune MAX_* if needed, toolbox batches automatically
│
└─► YES: How many org units will be included?
        │
        ├─► > MAX_ORG_UNITS: Use explicit org unit list (toolbox batches correctly)
        │
        └─► ≤ MAX_ORG_UNITS: children=True is safe to use
```

## Estimating Org Unit Counts

### Quick Level-Based Estimation

Efficient way to understand the org unit pyramid:

```python
def get_org_unit_counts_by_level(dhis) -> dict:
    """Get org unit count at each level."""
    response = dhis.api.get(
        "organisationUnits",
        params={
            "fields": "level",
            "paging": "false"
        }
    )

    counts = {}
    for ou in response.get("organisationUnits", []):
        level = ou.get("level")
        counts[level] = counts.get(level, 0) + 1

    return counts

# Usage
counts = get_org_unit_counts_by_level(dhis)
max_level = max(counts.keys())
print(f"Org unit pyramid: {counts}")
print(f"Max level: {max_level}")

# Typical structure:
# Level 1: 1 (country)
# Level 2: 10-50 (regions)
# Level 3: 50-200 (districts)
# Level 4: 200-2000 (sub-districts)
# Level 5: 1000-10000 (facilities)
```

### Estimate Descendant Count for a Parent

```python
def estimate_org_unit_count(dhis, parent_uid: str) -> int:
    """Estimate number of org units under a parent."""
    descendants = dhis.api.get(
        "organisationUnits",
        params={
            "filter": f"path:like:{parent_uid}",
            "fields": "id",
            "paging": "false"
        }
    )
    return len(descendants.get("organisationUnits", []))

# Usage
count = estimate_org_unit_count(dhis, "ImspTQPwCqd")
print(f"Org units under parent: {count}")
```

## Expanding Org Units (Replacing children=True)

Instead of `children=True`, expand org units explicitly so the toolbox can batch correctly:

```python
from openhexa.toolbox.dhis2 import dataframe

def get_org_units_for_query(dhis, level: int = None) -> list:
    """Get org unit IDs for querying.

    If level is provided, get org units at that level.
    Otherwise, get all org units up to the max level in the pyramid.
    """
    # Get org unit counts to find max level
    counts = get_org_unit_counts_by_level(dhis)
    max_level = max(counts.keys())

    # Use provided level or default to max level
    target_level = level if level is not None else max_level

    # Fetch org units
    org_units_df = dataframe.get_organisation_units(dhis, max_level=target_level)

    # Filter to target level
    org_unit_ids = org_units_df.filter(
        pl.col("level") == target_level
    )["id"].to_list()

    print(f"Found {len(org_unit_ids)} org units at level {target_level}")
    return org_unit_ids

# Usage
# Option 1: Get lowest level (facilities) automatically
facility_ids = get_org_units_for_query(dhis)

# Option 2: Get specific level (e.g., districts at level 3)
district_ids = get_org_units_for_query(dhis, level=3)

# Now query - toolbox batches automatically
df = dataframe.extract_analytics(
    dhis,
    data_elements=["de1"],
    org_units=facility_ids,
    periods=["202401"]
)
```

## Complete Example

```python
from openhexa.sdk import workspace
from openhexa.toolbox.dhis2 import DHIS2, dataframe
import polars as pl

# Setup
connection = workspace.dhis2_connection("my-dhis2")
dhis = DHIS2(connection)

# Check org unit pyramid
counts = get_org_unit_counts_by_level(dhis)
print(f"Org unit pyramid: {counts}")

# Tune batch sizes if needed (optional)
dhis.analytics.MAX_ORG_UNITS = 100
dhis.analytics.MAX_PERIODS = 4

# Get org units explicitly (NOT using children=True)
district_ids = get_org_units_for_query(dhis, level=3)

# Extract data - toolbox handles batching
df = dataframe.extract_analytics(
    dhis,
    data_elements=["de1"],
    org_units=district_ids,
    periods=["202401"]
)

print(f"Retrieved {len(df)} rows")
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| HTTP 502/504 errors | Batch size too large | Reduce MAX_ORG_UNITS and MAX_PERIODS |
| Query takes forever | Too many batches | Increase MAX_* values (if server can handle) |
| URL too long (414) | Using children=True | Expand org units explicitly |
| Memory error | Response too large | Reduce MAX_* values |

## Quick Reference

| Attribute | Default | Location |
|-----------|---------|----------|
| MAX_DATA_ELEMENTS | 50 | `dhis.data_value_sets.MAX_DATA_ELEMENTS` |
| MAX_ORG_UNITS | 50 | `dhis.data_value_sets.MAX_ORG_UNITS` / `dhis.analytics.MAX_ORG_UNITS` |
| MAX_PERIODS | 5/1 | `dhis.data_value_sets.MAX_PERIODS` / `dhis.analytics.MAX_PERIODS` |
| MAX_DX | 50 | `dhis.analytics.MAX_DX` |

| Scenario | Action |
|----------|--------|
| Fast server, want fewer API calls | Increase MAX_* values |
| Slow server, getting 50X errors | Decrease MAX_* values |
| Need data for children of an org unit | Use explicit org unit list, NOT children=True |
