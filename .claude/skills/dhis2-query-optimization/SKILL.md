---
name: dhis2-query-optimization
description: Optimize DHIS2 queries to avoid URL length limits, server timeouts, and memory issues. Use when querying large datasets, using children=True, or when queries fail with timeouts. Provides chunking strategies and complexity estimation.
---

# DHIS2 Query Optimization

Strategies for handling large DHIS2 queries that might fail due to URL length, server timeout, or memory limits.

**Prerequisites**: Client setup from `dhis2` skill (assumes `dhis` is initialized)

## Problem Overview

DHIS2 queries can fail when:

| Problem | Symptom | Threshold |
|---------|---------|-----------|
| URL too long | HTTP 414 or truncated query | ~1900 characters |
| Server timeout | HTTP 504 or connection timeout | Query complexity too high |
| Memory overflow | HTTP 500 or incomplete response | Response too large |

## Query Complexity Estimation

### Formula

```python
complexity = org_units × periods × data_elements
```

**Safe thresholds** (approximate):
- `complexity < 10,000` - Usually safe
- `complexity 10,000-50,000` - May need chunking
- `complexity > 50,000` - Definitely chunk

### The `children=True` Problem

When using `children=True`, you don't know the org unit count upfront:

```python
# This might request data for 5,000+ org units!
df = dhis.analytics.get(
    data_elements=["fbfJHSPpUQD"],
    org_units=["country_uid"],  # Level 1
    periods=["LAST_12_MONTHS"],
    include_cocs=True,
    children=True  # ⚠️ Expands to ALL descendants
)
```

### Estimate Org Unit Count

```python
def estimate_org_unit_count(dhis, parent_uid: str) -> int:
    """Estimate number of org units under a parent."""
    # Get parent info
    parent = dhis.api.get(
        f"organisationUnits/{parent_uid}",
        params={"fields": "level,children::size"}
    )
    parent_level = parent.get("level", 1)

    # Get org unit counts by level
    levels = dhis.api.get(
        "filledOrganisationUnitLevels",
        params={"fields": "id,level,name"}
    )

    # Count all org units below parent level
    total = 0
    ou_by_level = dhis.meta.organisation_units()

    # Group by level and count under parent
    # Simplified: get descendants directly
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

### Quick Level-Based Estimation

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

# Typical structure:
# Level 1: 1 (country)
# Level 2: 10-50 (regions)
# Level 3: 50-200 (districts)
# Level 4: 200-2000 (sub-districts)
# Level 5: 1000-10000 (facilities)
```

## Chunking Strategies

### Strategy 1: Chunk by Org Units

Best when you have many org units but few periods/data elements:

```python
def chunk_by_org_units(org_units: list, chunk_size: int = 100) -> list:
    """Split org units into chunks."""
    return [org_units[i:i + chunk_size] for i in range(0, len(org_units), chunk_size)]

def get_analytics_chunked_by_ou(
    dhis,
    data_elements: list,
    org_units: list,
    periods: list,
    chunk_size: int = 100
) -> pd.DataFrame:
    """Get analytics data, chunking by org units."""
    all_data = []

    for i, ou_chunk in enumerate(chunk_by_org_units(org_units, chunk_size)):
        print(f"Fetching chunk {i+1}, org units {len(ou_chunk)}")

        df = dhis.analytics.get(
            data_elements=data_elements,
            org_units=ou_chunk,
            periods=periods
        )
        all_data.append(df)

    return pd.concat(all_data, ignore_index=True)
```

### Strategy 2: Chunk by Periods

Best when you have many periods but few org units:

```python
def chunk_by_periods(periods: list, chunk_size: int = 12) -> list:
    """Split periods into chunks."""
    return [periods[i:i + chunk_size] for i in range(0, len(periods), chunk_size)]

def get_analytics_chunked_by_period(
    dhis,
    data_elements: list,
    org_units: list,
    periods: list,
    chunk_size: int = 12
) -> pd.DataFrame:
    """Get analytics data, chunking by periods."""
    all_data = []

    for i, period_chunk in enumerate(chunk_by_periods(periods, chunk_size)):
        print(f"Fetching chunk {i+1}, periods {period_chunk[0]} to {period_chunk[-1]}")

        df = dhis.analytics.get(
            data_elements=data_elements,
            org_units=org_units,
            periods=period_chunk
        )
        all_data.append(df)

    return pd.concat(all_data, ignore_index=True)
```

### Strategy 3: Chunk by Data Elements

Best when you have many data elements:

```python
def chunk_by_data_elements(data_elements: list, chunk_size: int = 20) -> list:
    """Split data elements into chunks."""
    return [data_elements[i:i + chunk_size] for i in range(0, len(data_elements), chunk_size)]

def get_analytics_chunked_by_de(
    dhis,
    data_elements: list,
    org_units: list,
    periods: list,
    chunk_size: int = 20
) -> pd.DataFrame:
    """Get analytics data, chunking by data elements."""
    all_data = []

    for i, de_chunk in enumerate(chunk_by_data_elements(data_elements, chunk_size)):
        print(f"Fetching chunk {i+1}, data elements {len(de_chunk)}")

        df = dhis.analytics.get(
            data_elements=de_chunk,
            org_units=org_units,
            periods=periods
        )
        all_data.append(df)

    return pd.concat(all_data, ignore_index=True)
```

### Strategy 4: Replace `children=True` with Explicit List

**Recommended approach** - avoids unknown expansion:

```python
def get_descendant_org_units(dhis, parent_uid: str, levels: list = None) -> list:
    """Get all descendant org unit UIDs under a parent."""
    params = {
        "filter": f"path:like:{parent_uid}",
        "fields": "id,level",
        "paging": "false"
    }

    response = dhis.api.get("organisationUnits", params=params)
    org_units = response.get("organisationUnits", [])

    # Filter by level if specified
    if levels:
        org_units = [ou for ou in org_units if ou.get("level") in levels]

    return [ou["id"] for ou in org_units]

# Usage: Instead of children=True
# BAD (unknown expansion):
# df = dhis.analytics.get(..., org_units=["country"], children=True)

# GOOD (explicit, can chunk):
descendants = get_descendant_org_units(dhis, "country_uid", levels=[4, 5])
print(f"Found {len(descendants)} org units")

# Now chunk the explicit list
df = get_analytics_chunked_by_ou(
    dhis,
    data_elements=["de1", "de2"],
    org_units=descendants,
    periods=["202401", "202402"]
)
```

## Adaptive Chunking

Automatically determine best chunking strategy:

```python
def get_analytics_adaptive(
    dhis,
    data_elements: list,
    org_units: list,
    periods: list,
    max_complexity: int = 10000
) -> pd.DataFrame:
    """Get analytics with adaptive chunking based on query complexity."""

    n_ou = len(org_units)
    n_pe = len(periods)
    n_de = len(data_elements)
    complexity = n_ou * n_pe * n_de

    print(f"Query complexity: {n_ou} OUs × {n_pe} periods × {n_de} DEs = {complexity:,}")

    if complexity <= max_complexity:
        print("Complexity OK, executing single query")
        return dhis.analytics.get(
            data_elements=data_elements,
            org_units=org_units,
            periods=periods
        )

    # Determine what to chunk
    # Chunk the dimension with the most items
    if n_ou >= n_pe and n_ou >= n_de:
        chunk_size = max(1, max_complexity // (n_pe * n_de))
        print(f"Chunking by org units, size={chunk_size}")
        return get_analytics_chunked_by_ou(dhis, data_elements, org_units, periods, chunk_size)

    elif n_pe >= n_ou and n_pe >= n_de:
        chunk_size = max(1, max_complexity // (n_ou * n_de))
        print(f"Chunking by periods, size={chunk_size}")
        return get_analytics_chunked_by_period(dhis, data_elements, org_units, periods, chunk_size)

    else:
        chunk_size = max(1, max_complexity // (n_ou * n_pe))
        print(f"Chunking by data elements, size={chunk_size}")
        return get_analytics_chunked_by_de(dhis, data_elements, org_units, periods, chunk_size)
```

## URL Length Handling

For raw API queries, check URL length:

```python
def build_url_params(params: dict) -> str:
    """Build URL query string to check length."""
    from urllib.parse import urlencode
    return urlencode(params, doseq=True)

def check_url_length(base_url: str, params: dict, max_length: int = 1900) -> bool:
    """Check if URL would exceed max length."""
    query_string = build_url_params(params)
    full_length = len(base_url) + 1 + len(query_string)  # +1 for '?'
    return full_length <= max_length

# If URL too long, use POST instead of GET (where supported)
# Or chunk the parameters
```

## Timeout and Retry Handling

```python
import time

def query_with_retry(
    query_func,
    max_retries: int = 3,
    initial_delay: float = 5.0,
    backoff_factor: float = 2.0
):
    """Execute query with exponential backoff retry."""
    delay = initial_delay

    for attempt in range(max_retries):
        try:
            return query_func()
        except Exception as e:
            if "timeout" in str(e).lower() or "504" in str(e):
                if attempt < max_retries - 1:
                    print(f"Timeout, retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    delay *= backoff_factor
                else:
                    print("Max retries reached. Consider reducing query size.")
                    raise
            else:
                raise

# Usage
df = query_with_retry(lambda: dhis.analytics.get(...))
```

## Complete Example

Fetching 5 years of monthly data for all facilities:

```python
import pandas as pd

# 1. Get all org units at facility level (level 5)
facilities = get_descendant_org_units(dhis, "country_uid", levels=[5])
print(f"Total facilities: {len(facilities)}")

# 2. Generate period list
periods = [f"{year}{month:02d}" for year in range(2019, 2024) for month in range(1, 13)]
print(f"Total periods: {len(periods)}")

# 3. Data elements
data_elements = ["de1", "de2", "de3"]
print(f"Total data elements: {len(data_elements)}")

# 4. Calculate complexity
complexity = len(facilities) * len(periods) * len(data_elements)
print(f"Query complexity: {complexity:,}")

# 5. Use adaptive chunking
df = get_analytics_adaptive(
    dhis,
    data_elements=data_elements,
    org_units=facilities,
    periods=periods,
    max_complexity=10000
)

print(f"Retrieved {len(df):,} rows")
```

## Quick Reference

| Dimension | Safe Chunk Size | Notes |
|-----------|-----------------|-------|
| Org units | 50-100 | Depends on periods/DEs |
| Periods | 12-24 | Monthly periods |
| Data elements | 10-20 | With disaggregations |
| Indicators | 10-20 | Complex formulas cost more |

| Scenario | Recommended Strategy |
|----------|---------------------|
| National data, all facilities | Chunk by org units |
| 10-year trend, one facility | Chunk by periods |
| 100+ indicators, few OUs | Chunk by data elements |
| Unknown size (children=True) | Expand to explicit list first |
