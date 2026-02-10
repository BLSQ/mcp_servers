---
name: dhis2-analytics
description: Query aggregated analytics data from DHIS2. Use for calculated/aggregated values, indicator values, or cross-dimensional analysis. ALWAYS use with dhis2-query-optimization skill. Routed via dhis2 skill for general DHIS2 requests.
---

# DHIS2 Analytics

Query aggregated analytics data from DHIS2.

**Prerequisites**:
- Client setup from `dhis2` skill (assumes `dhis` is initialized)
- **ALWAYS use `dhis2-query-optimization` skill** for complexity estimation and chunking

## MANDATORY: Query Optimization

Before ANY analytics query, you MUST:

1. **Estimate complexity** using `dhis2-query-optimization`
2. **Expand `children=True`** to explicit org unit list if used
3. **Apply chunking** if complexity > 10,000

```python
# WRONG - Never do this directly
df = dhis.analytics.get(
    data_elements=["de1"],
    org_units=["country_uid"],
    periods=["LAST_12_MONTHS"],
    children=True  # ⚠️ DANGEROUS - unknown expansion
)

# RIGHT - Use query optimization patterns
from dhis2_query_optimization import get_descendant_org_units, get_analytics_adaptive

# 1. Expand children to explicit list
org_units = get_descendant_org_units(dhis, "country_uid", levels=[4, 5])

# 2. Use adaptive chunking
df = get_analytics_adaptive(
    dhis,
    data_elements=["de1"],
    org_units=org_units,
    periods=periods
)
```

## Get Analytics Data

```python
# Basic query with data elements
data = dhis.analytics.get(
    data_elements=["fbfJHSPpUQD", "cYeuwXTCPkU"],
    org_units=["ImspTQPwCqd"],
    periods=["202401", "202402", "202403"]
)

# With indicators - ALWAYS set include_cocs=False
data = dhis.analytics.get(
    indicators=["ReUHfIn0pTQ"],
    org_units=["ImspTQPwCqd"],
    periods=["2024"],
    include_cocs=False  # ⚠️ MANDATORY for indicators
)

# By data element group
data = dhis.analytics.get(
    data_element_groups=["oDkJh5Ddh7d"],
    org_units=["ImspTQPwCqd"],
    periods=["2024"]
)

# By indicator group - ALWAYS set include_cocs=False
data = dhis.analytics.get(
    indicator_groups=["oehv9EO3vP7"],
    org_units=["ImspTQPwCqd"],
    periods=["2024"],
    include_cocs=False  # ⚠️ MANDATORY for indicators
)

# By org unit group
data = dhis.analytics.get(
    data_elements=["fbfJHSPpUQD"],
    org_unit_groups=["CXw2yu5fodb"],
    periods=["2024"]
)

# By org unit level
data = dhis.analytics.get(
    data_elements=["fbfJHSPpUQD"],
    org_unit_levels=[2, 3],  # Districts and facilities
    org_units=["ImspTQPwCqd"],  # Parent org unit
    periods=["2024"]
)

# Include category option combos
data = dhis.analytics.get(
    data_elements=["fbfJHSPpUQD"],
    org_units=["ImspTQPwCqd"],
    periods=["2024"],
    include_cocs=True
)
```

## Custom API Endpoint (Alternative)

For advanced queries not covered by toolbox:

```python
def get_analytics_raw(dhis, dimension: list, filter_dims: list = None) -> dict:
    """Query analytics with custom dimensions."""
    params = {
        "dimension": dimension,
        "skipMeta": False,
        "skipData": False
    }
    if filter_dims:
        params["filter"] = filter_dims

    return dhis.api.get("analytics", params=params)

# Example: custom dimension query
response = get_analytics_raw(
    dhis,
    dimension=[
        "dx:fbfJHSPpUQD;cYeuwXTCPkU",  # Data elements
        "pe:LAST_12_MONTHS",            # Relative period
        "ou:LEVEL-2;ImspTQPwCqd"        # Level 2 under parent
    ]
)
```

### Get Analytics Table Format

```python
def get_analytics_table(dhis, params: dict) -> pd.DataFrame:
    """Get analytics in table format."""
    response = dhis.api.get(
        "analytics",
        params={**params, "skipMeta": False}
    )

    headers = [h["name"] for h in response.get("headers", [])]
    rows = response.get("rows", [])

    df = pd.DataFrame(rows, columns=headers)

    # Add metadata for ID to name mapping
    metadata = response.get("metaData", {}).get("items", {})

    return df, metadata
```

## Dimension Syntax

| Dimension | Syntax | Example |
|-----------|--------|---------|
| Data (dx) | `dx:id1;id2` | `dx:fbfJHSPpUQD;ReUHfIn0pTQ` |
| Period (pe) | `pe:period1;period2` | `pe:202401;202402` |
| Org Unit (ou) | `ou:id1;id2` | `ou:ImspTQPwCqd` |
| Org Unit Level | `ou:LEVEL-n` | `ou:LEVEL-2` |
| Org Unit Group | `ou:OU_GROUP-id` | `ou:OU_GROUP-CXw2yu5fodb` |

## Relative Periods

| Period | Description |
|--------|-------------|
| `THIS_MONTH` | Current month |
| `LAST_MONTH` | Previous month |
| `LAST_3_MONTHS` | Last 3 months |
| `LAST_6_MONTHS` | Last 6 months |
| `LAST_12_MONTHS` | Last 12 months |
| `THIS_QUARTER` | Current quarter |
| `LAST_QUARTER` | Previous quarter |
| `LAST_4_QUARTERS` | Last 4 quarters |
| `THIS_YEAR` | Current year |
| `LAST_YEAR` | Previous year |
| `LAST_5_YEARS` | Last 5 years |

## Analytics vs Data Values

| Aspect | Analytics | Data Values |
|--------|-----------|-------------|
| Aggregation | Yes (server-side) | No (raw) |
| Indicators | Yes | No |
| Performance | Better for aggregated | Better for raw |
| Disaggregation | Optional | Always included |
| Calculated values | Yes | No |

## Enriching Results

```python
# Add names to analytics results
df = data  # DataFrame from analytics.get()

# Add data element/indicator names
df = dhis.meta.add_dx_name_column(df, "dx")

# Add org unit names
df = dhis.meta.add_org_unit_name_column(df, "ou")

# Add org unit hierarchy
df = dhis.meta.add_org_unit_parent_columns(df, "ou")
```

## Advanced Query Examples

### Aggregate by Org Unit Level

```python
def get_aggregated_by_level(dhis, data_elements: list, level: int, periods: list) -> pd.DataFrame:
    """Get data aggregated at specific org unit level."""
    response = dhis.api.get(
        "analytics",
        params={
            "dimension": [
                f"dx:{';'.join(data_elements)}",
                f"ou:LEVEL-{level}",
                f"pe:{';'.join(periods)}"
            ],
            "aggregationType": "SUM"
        }
    )

    headers = [h["name"] for h in response.get("headers", [])]
    return pd.DataFrame(response.get("rows", []), columns=headers)
```

### Time Series for Single Indicator

```python
def get_time_series(dhis, indicator_id: str, org_unit_id: str, periods: int = 12) -> pd.DataFrame:
    """Get time series for an indicator."""
    return dhis.analytics.get(
        indicators=[indicator_id],
        org_units=[org_unit_id],
        periods=[f"LAST_{periods}_MONTHS"],
        include_cocs=False  # ⚠️ MANDATORY for indicators
    )
```

## Important: Indicators and Category Option Combos

**⚠️ ALWAYS use `include_cocs=False` when querying indicators.**

The toolbox defaults to `include_cocs=True`, which adds category option combo disaggregation. This causes queries to FAIL for indicators because indicators don't have category option combos.

```python
# WRONG - will fail for indicators
data = dhis.analytics.get(
    indicators=["ReUHfIn0pTQ"],
    org_units=["ImspTQPwCqd"],
    periods=["2024"]
    # include_cocs defaults to True → FAILS
)

# RIGHT - always set include_cocs=False for indicators
data = dhis.analytics.get(
    indicators=["ReUHfIn0pTQ"],
    org_units=["ImspTQPwCqd"],
    periods=["2024"],
    include_cocs=False  # ⚠️ MANDATORY
)
```

## Performance Tips

1. **Use relative periods** - More efficient than listing individual periods
2. **Aggregate at higher levels** - Query LEVEL-2 instead of all facilities
3. **Limit data dimensions** - Don't query all data elements
4. **Enable caching** - Results are cached based on query
5. **Use skipMeta=True** - If you don't need metadata
6. **ALWAYS estimate complexity first** - See `dhis2-query-optimization`
7. **ALWAYS use `include_cocs=False` for indicators** - Toolbox bug workaround
