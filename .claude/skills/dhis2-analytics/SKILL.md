---
name: dhis2-analytics
description: Query aggregated analytics data from DHIS2. Use for calculated/aggregated values, indicator values, or cross-dimensional analysis. Routed via dhis2 skill for general DHIS2 requests.
---

# DHIS2 Analytics

Query aggregated analytics data from DHIS2.

## Toolbox Methods (Recommended)

The OpenHEXA toolbox provides built-in methods for analytics.

### Setup

```python
from openhexa.sdk import workspace, DHIS2Connection
from openhexa.toolbox.dhis2 import DHIS2

dhis = DHIS2(dhis2_connection, cache_dir=f"{workspace.files_path}/.cache")
```

### Get Analytics Data

```python
# Basic query with data elements
data = dhis.analytics.get(
    data_elements=["fbfJHSPpUQD", "cYeuwXTCPkU"],
    org_units=["ImspTQPwCqd"],
    periods=["202401", "202402", "202403"]
)

# With indicators
data = dhis.analytics.get(
    indicators=["ReUHfIn0pTQ"],
    org_units=["ImspTQPwCqd"],
    periods=["2024"]
)

# By data element group
data = dhis.analytics.get(
    data_element_groups=["oDkJh5Ddh7d"],
    org_units=["ImspTQPwCqd"],
    periods=["2024"]
)

# By indicator group
data = dhis.analytics.get(
    indicator_groups=["oehv9EO3vP7"],
    org_units=["ImspTQPwCqd"],
    periods=["2024"]
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
        periods=[f"LAST_{periods}_MONTHS"]
    )
```

## Performance Tips

1. **Use relative periods** - More efficient than listing individual periods
2. **Aggregate at higher levels** - Query LEVEL-2 instead of all facilities
3. **Limit data dimensions** - Don't query all data elements
4. **Enable caching** - Results are cached based on query
5. **Use skipMeta=True** - If you don't need metadata
