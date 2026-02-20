---
name: dhis2-schema-explorer
description: Discover DHIS2 API endpoints and schemas dynamically. Use when other DHIS2 skills don't cover the needed endpoint or you need to explore available fields for custom queries. Helps build correct field selections for any DHIS2 resource.
---

# DHIS2 Schema Explorer

**Prerequisites**: Client setup from `dhis2` skill (assumes `dhis` is initialized)

Use this skill to explore DHIS2 API structure when other skills don't fit your needs.

## Step 1: List Available Resources

```python
# Get all available API resources
resources = dhis.api.get("resources")["resources"]

# Each resource has: displayName, singular, plural, href
# Example entry:
# {
#   "displayName": "Data Sets",
#   "singular": "dataSet",
#   "plural": "dataSets",
#   "href": "https://play.dhis2.org/api/dataSets"
# }
```

## Step 2: Get Schema for a Resource

Use the **singular** name to query the schema:

```python
# Get schema properties for a resource
schema = dhis.api.get(
    "schemas/dataSet",
    params={"fields": "properties[name,collection,collectionName]"}
)

# Returns properties like:
# {
#   "properties": [
#     {"name": "dataEntryForm", "collection": false},
#     {"name": "dataSetElement", "collection": true, "collectionName": "dataSetElements"},
#     {"name": "organisationUnits", "collection": true, "collectionName": "organisationUnits"}
#   ]
# }
```

## Step 3: Build Your Query

Use the **plural** name for the endpoint, property names for fields:

```python
# Simple fields query
response = dhis.api.get(
    "dataSets",
    params={"fields": "id,name,periodType,dataSetElements"}
)
```

## Step 4: Nested Queries

For collections, explore the nested schema using the property **name** (singular):

```python
# Get schema for nested resource
nested_schema = dhis.api.get(
    "schemas/dataSetElement",
    params={"fields": "properties[name,collection,collectionName]"}
)

# Returns:
# {"properties": [
#   {"name": "dataElement", "collection": false},
#   {"name": "categoryCombo", "collection": false}
# ]}

# Now build nested query
response = dhis.api.get(
    "dataSets",
    params={"fields": "id,name,dataSetElements[dataElement[id,name],categoryCombo[id,name]]"}
)
```

## Naming Convention Summary

| Context | Use |
|---------|-----|
| Schema endpoint | **singular** (`schemas/dataSet`) |
| Data endpoint | **plural** (`dataSets`) |
| Fields parameter | **collection name** from schema  (`?field=dataSetElements`)|
| Nested schema lookup | **property name** (singular form) (`schemas/dataSetElement`) |

## Quick Discovery Pattern

```python
def explore_resource(dhis, resource_singular: str) -> dict:
    """Get all field names available for a resource."""
    schema = dhis.api.get(
        f"schemas/{resource_singular}",
        params={"fields": "properties[name,collection,collectionName]"}
    )
    return {
        p["name"]: {
            "collection": p.get("collection", False),
            "collectionName": p.get("collectionName")
        }
        for p in schema.get("properties", [])
    }

# Usage
fields = explore_resource(dhis, "dataSet")
# Returns dict of field_name -> {collection: bool, collectionName: str|None}
```

## Find a Resource by Name

```python
def find_resource(dhis, search_term: str) -> list:
    """Search for resources matching a term."""
    resources = dhis.api.get("resources")["resources"]
    return [
        r for r in resources
        if search_term.lower() in r["displayName"].lower()
        or search_term.lower() in r["singular"].lower()
    ]

# Usage
find_resource(dhis, "indicator")
# Returns matching resources with their singular/plural names
```