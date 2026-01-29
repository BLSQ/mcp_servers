---
name: dhis2
description: Work with DHIS2 health information systems - extract data, query metadata, run validations, manage users, or check system info. Use this skill for ANY DHIS2-related request. It routes to specialized sub-skills (analytics, tracker, validation, users, system-info, data-elements, indicators, organisation-units, datasets, data-values, visualizations).
---

# DHIS2 Skill Router

This skill routes DHIS2 requests to the appropriate specialized skill.

## Decision Tree

Use this table to determine which specialized skill to use:

| User Request | Route To | Examples |
|--------------|----------|----------|
| Aggregated values, indicator calculations, cross-dimensional analysis | `dhis2-analytics` | "Get monthly ANC coverage by district", "Query indicator trends" |
| Raw submitted data values (dataValueSets) | `dhis2-data-values` | "Extract raw data for dataset X", "Get submitted values for period" |
| Individual/case-based data (tracker programs) | `dhis2-tracker` | "Get tracked entities", "Extract enrollments", "Query events" |
| Data quality checks, validation violations | `dhis2-validation` | "Run validation rules", "Get validation violations", "Check data quality" |
| User permissions, access scope, user administration | `dhis2-users` | "What org units can I access?", "List users", "Check my permissions" |
| DHIS2 version, database info, server config | `dhis2-system-info` | "What DHIS2 version?", "Check server capabilities" |
| Data element metadata and groups | `dhis2-data-elements` | "List data elements", "Get data element groups" |
| Indicator definitions and formulas | `dhis2-indicators` | "Get indicator formula", "List indicator groups" |
| Organisation unit hierarchy and groups | `dhis2-organisation-units` | "Get org unit tree", "List facilities", "Get org unit levels" |
| Dataset definitions, reporting schedules | `dhis2-datasets` | "List datasets", "Get reporting frequency" |
| Saved visualizations (charts, tables, maps) | `dhis2-visualizations` | "Get dashboard charts", "Extract visualization config" |

## Quick Reference: Analytics vs Data Values vs Tracker

| Aspect | Analytics | Data Values | Tracker |
|--------|-----------|-------------|---------|
| Data type | Aggregated | Raw submitted | Individual-level |
| API endpoint | `/api/analytics` | `/api/dataValueSets` | `/api/tracker/*` |
| Indicators | Yes | No | No |
| Server-side aggregation | Yes | No | No |
| Use for | Reports, dashboards, trends | Data audits, raw exports | Case management, patient data |

## Common Setup (All Skills)

All DHIS2 skills use the same connection setup:

```python
from openhexa.sdk import workspace
from openhexa.toolbox.dhis2 import DHIS2

# Get DHIS2 connection from workspace
dhis2_connection = workspace.dhis2_connection("connection_identifier")

# Initialize DHIS2 client with caching
dhis = DHIS2(dhis2_connection, cache_dir=f"{workspace.files_path}/.cache")
```

### Using list_connections

To find available DHIS2 connections:

```python
from openhexa.sdk import workspace

# List all connections
connections = workspace.list_connections()
for conn in connections:
    print(f"{conn.identifier}: {conn.type}")
```

## Handling Ambiguous Requests

If the user request is ambiguous, ask for clarification:

### "Extract data from DHIS2"
Ask: "What type of data do you need?"
- Aggregated/calculated values (indicators, totals) → `dhis2-analytics`
- Raw submitted values (as entered) → `dhis2-data-values`
- Individual/patient-level data → `dhis2-tracker`

### "Get DHIS2 metadata"
Ask: "Which metadata do you need?"
- Data elements → `dhis2-data-elements`
- Indicators → `dhis2-indicators`
- Organisation units → `dhis2-organisation-units`
- Datasets → `dhis2-datasets`
- Users/permissions → `dhis2-users`

### "Query DHIS2"
Ask: "What are you trying to accomplish?"
- Generate a report/dashboard → `dhis2-analytics`
- Audit data entry → `dhis2-data-values`
- Track individuals/cases → `dhis2-tracker`
- Check data quality → `dhis2-validation`

## Multi-Skill Scenarios

Some tasks require multiple skills:

### Data Quality Report
1. `dhis2-validation` - Get validation violations
2. `dhis2-organisation-units` - Add org unit names/hierarchy
3. `dhis2-data-elements` - Add data element names

### Complete Data Export
1. `dhis2-organisation-units` - Get org unit hierarchy
2. `dhis2-data-elements` - Get data element metadata
3. `dhis2-analytics` or `dhis2-data-values` - Get actual data

### Tracker Program Analysis
1. `dhis2-tracker` - Extract tracked entities/events
2. `dhis2-organisation-units` - Add org unit context
3. `dhis2-data-elements` - Map data element IDs to names

## Toolbox vs API Methods

| Skill | Toolbox Support | Notes |
|-------|-----------------|-------|
| dhis2-analytics | ✅ `dhis.analytics.get()` | Full support |
| dhis2-data-values | ✅ `dhis.data_value_sets.get()` | Full support |
| dhis2-tracker | ⚠️ `dhis.tracker.extract_event_data_values()` | Events only, use `api.get()` for TEIs/enrollments |
| dhis2-data-elements | ✅ `dhis.meta.data_elements()` | Full support |
| dhis2-indicators | ✅ `dhis.meta.indicators()` | Full support |
| dhis2-organisation-units | ✅ `dhis.meta.organisation_units()` | Full support |
| dhis2-datasets | ✅ `dhis.meta.datasets()` | Full support |
| dhis2-validation | ❌ | Use `dhis.api.get()` |
| dhis2-users | ❌ | Use `dhis.api.get()` |
| dhis2-system-info | ❌ | Use `dhis.api.get()` |
| dhis2-visualizations | ❌ | Use `dhis.api.get()` |

## Version Compatibility

Some API features depend on DHIS2 version:

| Feature | Minimum Version |
|---------|-----------------|
| New Tracker API (`/api/tracker/*`) | 2.38 |
| Analytics with enrollment dimensions | 2.39 |
| Continuous analytics | 2.40 |

Check version using `dhis2-system-info` skill before using version-specific features.
