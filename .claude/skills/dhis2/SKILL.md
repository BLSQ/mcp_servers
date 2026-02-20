---
name: dhis2
description: Work with DHIS2 health information systems - extract data, query metadata, run validations, manage users, or check system info. Use this skill for ANY DHIS2-related request. It routes to specialized sub-skills and provides centralized client setup and API patterns.
---

# DHIS2

Main entry point for all DHIS2 interactions.

## Client Setup

All DHIS2 code uses this setup. Sub-skills assume `dhis` is already initialized.

```python
from openhexa.sdk import workspace
from openhexa.toolbox.dhis2 import DHIS2

# Get connection and initialize client with caching
dhis2_connection = workspace.dhis2_connection("connection_identifier")
dhis = DHIS2(dhis2_connection, cache_dir=f"{workspace.files_path}/.cache") #cache_dir is optionnal! 
```

## Routing Decision Tree

| User Request | Route To |
|--------------|----------|
| Aggregated/indicator values | `dhis2-analytics` + `dhis2-query-optimization` |
| Raw submitted values | `dhis2-data-values` + `dhis2-query-optimization` |
| Tracker/individual data | `dhis2-tracker` |
| Data element metadata | `dhis2-data-elements` |
| Indicator metadata | `dhis2-indicators` |
| Org unit hierarchy | `dhis2-organisation-units` |
| Dataset metadata | `dhis2-datasets` |
| Validation rules/violations | `dhis2-validation` |
| User info/permissions | `dhis2-users` |
| System version/config | `dhis2-system-info` |
| Saved visualizations | `dhis2-visualizations` |
| Explore API endpoints/schemas | `dhis2-schema-explorer` |

## Query Optimization (MANDATORY for large queries)

For analytics and data-values queries, ALWAYS use `dhis2-query-optimization` skill to:
1. Estimate query complexity
2. Expand `children=True` to explicit org unit list

## Raw API Access

For endpoints without toolbox methods:

```python
response = dhis.api.get("endpoint", params={"key": "value"})
response = dhis.api.post("endpoint", data=payload)
```
