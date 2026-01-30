---
name: dhis2
description: Work with DHIS2 health information systems - extract data, query metadata, run validations, manage users, or check system info. Use this skill for ANY DHIS2-related request. It routes to specialized sub-skills and provides centralized client setup and API patterns.
---

# DHIS2

Main entry point for all DHIS2 interactions. This skill provides:
1. **Client setup** - How to initialize the DHIS2 client
2. **API basics** - How to use `dhis.api.get()` and other methods
3. **Routing** - Which sub-skill to use for specific tasks
4. **Query optimization** - Reference to `dhis2-query-optimization` for large queries

## Client Setup (Centralized)

All DHIS2 code uses this setup. Sub-skills assume `dhis` is already initialized.

```python
from openhexa.sdk import workspace
from openhexa.toolbox.dhis2 import DHIS2

# Get connection identifier from workspace
dhis2_connection = workspace.dhis2_connection("connection_identifier")

# Initialize client with caching (recommended)
dhis = DHIS2(dhis2_connection, cache_dir=f"{workspace.files_path}/.cache")
```

### Find Available Connections

```python
from openhexa.sdk import workspace

# List all connections to find DHIS2 connection identifiers
for conn in workspace.list_connections():
    print(f"{conn.identifier}: {conn.type}")
```

## API Basics

The `dhis` client provides several interfaces:

### Toolbox Methods (Preferred)

High-level methods that handle pagination and return DataFrames:

```python
# Analytics - aggregated data (data elements)
df = dhis.analytics.get(
    data_elements=["fbfJHSPpUQD"],
    org_units=["ImspTQPwCqd"],
    periods=["202401", "202402"]
)

# Analytics - indicators (⚠️ ALWAYS use include_cocs=False)
df = dhis.analytics.get(
    indicators=["ReUHfIn0pTQ"],
    org_units=["ImspTQPwCqd"],
    periods=["202401", "202402"],
    include_cocs=False  # MANDATORY for indicators - toolbox bug
)

# Data values - raw submitted data
df = dhis.data_value_sets.get(
    data_sets=["BfMAe6Itzgt"],
    org_units=["ImspTQPwCqd"],
    periods=["202401"]
)

# Metadata
df_de = dhis.meta.data_elements()
df_ind = dhis.meta.indicators()
df_ou = dhis.meta.organisation_units()
df_ds = dhis.meta.datasets()

# Tracker events
df = dhis.tracker.extract_event_data_values(
    programs=["IpHINAT79UW"],
    org_units=["ImspTQPwCqd"],
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

### Raw API Access

For endpoints without toolbox methods, use `dhis.api.get()`:

```python
# GET request
response = dhis.api.get("endpoint", params={"key": "value"})

# Examples
system_info = dhis.api.get("system/info")
users = dhis.api.get("users", params={"fields": "id,name,email", "paging": "false"})
validation = dhis.api.get("validationRules", params={"fields": "*"})

# With path parameters
user = dhis.api.get(f"users/{user_id}", params={"fields": "id,name,organisationUnits"})

# POST request
response = dhis.api.post("endpoint", data=payload)
```

### Response Handling

```python
# API responses are dictionaries
response = dhis.api.get("dataElements", params={"paging": "false"})
data_elements = response.get("dataElements", [])

# Pagination (when paging=true or default)
response = dhis.api.get("dataElements", params={"pageSize": 50, "page": 1})
pager = response.get("pager", {})
total = pager.get("total")
page_count = pager.get("pageCount")
```

## Routing Decision Tree

**IMPORTANT**: For analytics and data-values queries, ALWAYS use `dhis2-query-optimization` skill first to:
1. Estimate query complexity
2. Handle `children=True` by expanding to explicit org unit list
3. Apply chunking if needed

| User Request | Route To | Toolbox Method |
|--------------|----------|----------------|
| Aggregated/indicator values | `dhis2-analytics` + `dhis2-query-optimization` | `dhis.analytics.get()` |
| Raw submitted values | `dhis2-data-values` + `dhis2-query-optimization` | `dhis.data_value_sets.get()` |
| Tracker/individual data | `dhis2-tracker` | `dhis.tracker.*` / `dhis.api.get()` |
| Validation rules/violations | `dhis2-validation` | `dhis.api.get()` |
| User info/permissions | `dhis2-users` | `dhis.api.get()` |
| System version/config | `dhis2-system-info` | `dhis.api.get()` |
| Data element metadata | `dhis2-data-elements` | `dhis.meta.data_elements()` |
| Indicator metadata | `dhis2-indicators` | `dhis.meta.indicators()` |
| Org unit hierarchy | `dhis2-organisation-units` | `dhis.meta.organisation_units()` |
| Dataset metadata | `dhis2-datasets` | `dhis.meta.datasets()` |
| Saved visualizations | `dhis2-visualizations` | `dhis.api.get()` |

## Query Optimization

**IMPORTANT**: For large queries, see `dhis2-query-optimization` skill.

Large queries can fail due to:
1. **URL too long** - Max ~1900 characters
2. **Server timeout** - Too much data requested
3. **Memory issues** - Response too large

Common triggers:
- `children=True` with high-level org unit (country)
- Many periods (e.g., 5 years monthly = 60 periods)
- Many data elements/indicators (>20)

The toolbox handles chunking for explicit lists, but NOT for:
- `children=True` / `includeDescendants=True`
- Very large explicit lists

**Always estimate query complexity before executing large queries.**

## Quick Reference: Data Types

| Aspect | Analytics | Data Values | Tracker |
|--------|-----------|-------------|---------|
| Data type | Aggregated | Raw submitted | Individual-level |
| API endpoint | `/api/analytics` | `/api/dataValueSets` | `/api/tracker/*` |
| Indicators | Yes | No | No |
| Aggregation | Server-side | None | None |
| Use for | Reports, trends | Audits, raw exports | Case management |

## Ambiguous Request Handling

### "Extract data from DHIS2"
Ask: "What type of data?"
- Aggregated/calculated → `dhis2-analytics`
- Raw as submitted → `dhis2-data-values`
- Individual/patient → `dhis2-tracker`

### "Get DHIS2 metadata"
Ask: "Which metadata?"
- Data elements → `dhis2-data-elements`
- Indicators → `dhis2-indicators`
- Org units → `dhis2-organisation-units`
- Datasets → `dhis2-datasets`

## Multi-Skill Scenarios

### Complete Data Export
1. `dhis2-organisation-units` - Get hierarchy
2. `dhis2-data-elements` - Get metadata
3. `dhis2-analytics` or `dhis2-data-values` - Get data
4. `dhis2-query-optimization` - If large query

### Data Quality Analysis
1. `dhis2-validation` - Get violations
2. `dhis2-organisation-units` - Add org unit names
3. `dhis2-data-elements` - Add data element names

## Version Compatibility

| Feature | Min Version |
|---------|-------------|
| New Tracker API | 2.38 |
| Enrollment analytics | 2.39 |
| Continuous analytics | 2.40 |

Check with `dhis2-system-info` before using version-specific features.
