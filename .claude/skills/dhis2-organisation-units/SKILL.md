---
name: dhis2-organisation-units
description: Extract organisation units and groups from DHIS2. Use for org unit hierarchy, metadata, levels, or groups. Routed via dhis2 skill for general DHIS2 requests.
---

# DHIS2 Organisation Units

Extract organisation unit metadata from DHIS2 instances.

## Toolbox Methods (Recommended)

The OpenHEXA toolbox provides built-in methods for organisation units.

### Setup

```python
from openhexa.sdk import workspace, DHIS2Connection
from openhexa.toolbox.dhis2 import DHIS2

# Initialize client
dhis = DHIS2(dhis2_connection, cache_dir=f"{workspace.files_path}/.cache")
```

### Get Organisation Units

```python
# Get all organisation units
org_units = dhis.meta.organisation_units()

# With pagination
org_units = dhis.meta.organisation_units(
    page=1,
    pageSize=1000
)

# With filters
org_units = dhis.meta.organisation_units(
    filters=["level:eq:2"]  # Only level 2 (districts)
)

# Custom fields
org_units = dhis.meta.organisation_units(
    fields="id,name,level,parent[id,name],geometry"
)
```

### Get Organisation Unit Levels

```python
# Get all levels
levels = dhis.meta.organisation_unit_levels()

# Custom fields
levels = dhis.meta.organisation_unit_levels(
    fields="id,name,level"
)
```

### Get Organisation Unit Groups

```python
# Get all groups
groups = dhis.meta.organisation_unit_groups()

# With filters
groups = dhis.meta.organisation_unit_groups(
    filters=["name:ilike:hospital"]
)
```

## DataFrame Helper Methods

### Add Org Unit Names to Data

```python
# If you have a DataFrame with org unit IDs
df = dhis.meta.add_org_unit_name_column(
    dataframe=df,
    org_unit_id_column="orgUnit"
)
# Adds 'orgUnit_name' column
```

### Add Parent Hierarchy

```python
# Add parent columns (level_1_name, level_2_name, etc.)
df = dhis.meta.add_org_unit_parent_columns(
    dataframe=df,
    org_unit_id_column="orgUnit"
)
```

## Custom API Endpoint (Alternative)

For endpoints not covered by toolbox methods:

```python
# Get org units with geometry
response = dhis.api.get(
    "organisationUnits",
    params={
        "fields": "id,name,level,geometry,parent[id,name]",
        "paging": False,
        "filter": "level:le:3"
    }
)
org_units = response.get("organisationUnits", [])
```

### Get Org Unit by ID

```python
def get_org_unit(dhis, org_unit_id: str) -> dict:
    """Get single organisation unit with full details."""
    return dhis.api.get(
        f"organisationUnits/{org_unit_id}",
        params={
            "fields": "*,parent[id,name],children[id,name],ancestors[id,name,level]"
        }
    )
```

### Get Org Units with Coordinates

```python
def get_org_units_with_coordinates(dhis) -> list:
    """Get org units that have coordinates/geometry."""
    response = dhis.api.get(
        "organisationUnits",
        params={
            "fields": "id,name,level,coordinates,geometry",
            "filter": "coordinates:!null",
            "paging": False
        }
    )
    return response.get("organisationUnits", [])
```

## Common Filters

| Filter | Description |
|--------|-------------|
| `level:eq:2` | Exact level |
| `level:le:3` | Level 3 or above |
| `name:ilike:hospital` | Name contains (case-insensitive) |
| `id:in:[id1,id2]` | Specific IDs |
| `parent.id:eq:abc123` | Children of parent |
| `coordinates:!null` | Has coordinates |

## Output Fields

Common fields to request:

```
id,name,shortName,code,level,path,
parent[id,name],
children[id,name],
ancestors[id,name,level],
geometry,coordinates,
openingDate,closedDate
```
