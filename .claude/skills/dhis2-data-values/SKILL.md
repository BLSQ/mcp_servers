---
name: dhis2-data-values
description: Extract raw data values from DHIS2 using the dataValueSets API. Use for actual submitted data values, not aggregated analytics. ALWAYS use with dhis2-query-optimization skill. Routed via dhis2 skill for general DHIS2 requests.
---

# DHIS2 Data Values

Extract and post raw data values using the dataValueSets API.

**Prerequisites**:
- Client setup from `dhis2` skill (assumes `dhis` is initialized)
- **ALWAYS use `dhis2-query-optimization` skill** for complexity estimation and chunking

## MANDATORY: Query Optimization

Before ANY data values query, you MUST:

1. **Estimate complexity** using `dhis2-query-optimization`
2. **Expand `children=True`** to explicit org unit list if used
3. **Apply chunking** if complexity > 10,000

```python
# WRONG - Never do this directly for large queries
df = dhis.data_value_sets.get(
    data_sets=["ds1"],
    org_units=["country_uid"],
    periods=periods,
    children=True  # ⚠️ DANGEROUS - unknown expansion
)

# RIGHT - Use query optimization patterns
from dhis2_query_optimization import get_descendant_org_units, chunk_by_org_units

# 1. Expand children to explicit list
org_units = get_descendant_org_units(dhis, "country_uid", levels=[4, 5])

# 2. Chunk and fetch
all_data = []
for ou_chunk in chunk_by_org_units(org_units, chunk_size=100):
    df = dhis.data_value_sets.get(
        data_sets=["ds1"],
        org_units=ou_chunk,
        periods=periods
    )
    all_data.append(df)

df = pd.concat(all_data, ignore_index=True)
```

## Get Data Values

```python
# Basic query
data = dhis.data_value_sets.get(
    data_elements=["fbfJHSPpUQD", "cYeuwXTCPkU"],
    org_units=["ImspTQPwCqd"],
    periods=["202401", "202402", "202403"]
)

# By dataset
data = dhis.data_value_sets.get(
    datasets=["BfMAe6Itzgt"],
    org_units=["ImspTQPwCqd"],
    periods=["202401"]
)

# By data element group
data = dhis.data_value_sets.get(
    data_element_groups=["oDkJh5Ddh7d"],
    org_units=["ImspTQPwCqd"],
    periods=["2024"]
)

# With date range instead of periods
data = dhis.data_value_sets.get(
    data_elements=["fbfJHSPpUQD"],
    org_units=["ImspTQPwCqd"],
    start_date="2024-01-01",
    end_date="2024-03-31"
)

# Include children org units
data = dhis.data_value_sets.get(
    data_elements=["fbfJHSPpUQD"],
    org_units=["ImspTQPwCqd"],
    periods=["202401"],
    children=True
)

# By org unit group
data = dhis.data_value_sets.get(
    data_elements=["fbfJHSPpUQD"],
    org_unit_groups=["CXw2yu5fodb"],
    periods=["202401"]
)

# Filter by last updated
data = dhis.data_value_sets.get(
    data_elements=["fbfJHSPpUQD"],
    org_units=["ImspTQPwCqd"],
    periods=["202401"],
    last_updated="2024-01-15"
)
```

### Post Data Values

```python
# Prepare data values
data_values = [
    {
        "dataElement": "fbfJHSPpUQD",
        "period": "202401",
        "orgUnit": "ImspTQPwCqd",
        "categoryOptionCombo": "HllvX50cXC0",
        "value": "42"
    },
    {
        "dataElement": "cYeuwXTCPkU",
        "period": "202401",
        "orgUnit": "ImspTQPwCqd",
        "categoryOptionCombo": "HllvX50cXC0",
        "value": "100"
    }
]

# Post with dry run first
result = dhis.data_value_sets.post(
    data_values=data_values,
    dry_run=True
)
print(f"Dry run: {result}")

# Actual import
result = dhis.data_value_sets.post(
    data_values=data_values,
    import_strategy="CREATE_AND_UPDATE"
)
print(f"Imported: {result}")
```

## Data Value Structure

Each data value has these fields:

| Field | Description |
|-------|-------------|
| `dataElement` | Data element ID |
| `period` | Period (e.g., 202401) |
| `orgUnit` | Organisation unit ID |
| `categoryOptionCombo` | Disaggregation ID |
| `attributeOptionCombo` | Attribute combo ID |
| `value` | The actual value |
| `storedBy` | Username who stored |
| `created` | Creation timestamp |
| `lastUpdated` | Last update timestamp |
| `comment` | Optional comment |
| `followup` | Flagged for followup |

## Enriching Data Values

### Add Names to DataFrame

```python
# After getting data values
df = data  # DataFrame from data_value_sets.get()

# Add data element names
df = dhis.meta.add_dx_name_column(df, "dataElement")

# Add org unit names
df = dhis.meta.add_org_unit_name_column(df, "orgUnit")

# Add category option combo names
df = dhis.meta.add_coc_name_column(df, "categoryOptionCombo")

# Add org unit hierarchy
df = dhis.meta.add_org_unit_parent_columns(df, "orgUnit")
```

## Custom API Endpoint (Alternative)

For specific use cases:

```python
def get_data_values_raw(dhis, params: dict) -> dict:
    """Get raw dataValueSets response."""
    return dhis.api.get(
        "dataValueSets",
        params=params
    )

# Example: get with specific attribute option combo
response = get_data_values_raw(dhis, {
    "dataSet": "BfMAe6Itzgt",
    "period": "202401",
    "orgUnit": "ImspTQPwCqd",
    "attributeOptionCombo": "HllvX50cXC0"
})
```

## Import Strategies

| Strategy | Description |
|----------|-------------|
| `CREATE` | Only create new values |
| `UPDATE` | Only update existing values |
| `CREATE_AND_UPDATE` | Create or update (default) |
| `DELETE` | Delete values |

## Period Formats

| Period Type | Format | Example |
|-------------|--------|---------|
| Daily | YYYYMMDD | 20240115 |
| Weekly | YYYYWn | 2024W03 |
| Monthly | YYYYMM | 202401 |
| Quarterly | YYYYQn | 2024Q1 |
| Yearly | YYYY | 2024 |

## Error Handling

```python
try:
    data = dhis.data_value_sets.get(
        data_elements=["invalid_id"],
        org_units=["ImspTQPwCqd"],
        periods=["202401"]
    )
except Exception as e:
    current_run.log_error(f"Failed to get data values: {e}")
```

## Performance Tips

1. **Use specific filters** - Don't query all data
2. **Limit periods** - Query one year at a time
3. **Use pagination** - For large datasets
4. **Enable caching** - `cache_dir` parameter
5. **Use children=True** - Instead of listing all child org units
