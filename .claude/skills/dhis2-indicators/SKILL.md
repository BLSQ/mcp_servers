---
name: dhis2-indicators
description: Extract indicators and indicator groups from DHIS2. Use for indicator definitions, formulas, or indicator groups. Routed via dhis2 skill for general DHIS2 requests.
---

# DHIS2 Indicators

Extract indicator metadata from DHIS2 instances.

**Prerequisites**: Client setup from `dhis2` skill (assumes `dhis` is initialized)

## Get Indicators

```python
# Get all indicators
indicators = dhis.meta.indicators()

# With pagination
indicators = dhis.meta.indicators(
    page=1,
    pageSize=500
)

# With filters
indicators = dhis.meta.indicators(
    filters=["name:ilike:coverage"]
)

# Custom fields
indicators = dhis.meta.indicators(
    fields="id,name,shortName,numerator,denominator,indicatorType[name]"
)
```

### Get Indicator Groups

```python
# Get all groups
groups = dhis.meta.indicator_groups()

# With filters
groups = dhis.meta.indicator_groups(
    filters=["name:ilike:immunization"]
)
```

## Custom API Endpoint (Alternative)

For endpoints not covered by toolbox methods:

```python
# Get indicators with full details
response = dhis.api.get(
    "indicators",
    params={
        "fields": "id,name,shortName,code,numerator,denominator,"
                  "numeratorDescription,denominatorDescription,"
                  "indicatorType[id,name,factor],"
                  "indicatorGroups[id,name]",
        "paging": False
    }
)
indicators = response.get("indicators", [])
```

### Get Indicator by ID

```python
def get_indicator(dhis, indicator_id: str) -> dict:
    """Get single indicator with full details."""
    return dhis.api.get(
        f"indicators/{indicator_id}",
        params={
            "fields": "*,indicatorType[*],indicatorGroups[id,name],"
                      "legendSets[id,name]"
        }
    )
```

### Get Indicators by Group

```python
def get_indicators_by_group(dhis, group_id: str) -> list:
    """Get all indicators in a group."""
    response = dhis.api.get(
        "indicators",
        params={
            "fields": "id,name,shortName,numerator,denominator",
            "filter": f"indicatorGroups.id:eq:{group_id}",
            "paging": False
        }
    )
    return response.get("indicators", [])
```

### Parse Indicator Formula

```python
def extract_data_elements_from_formula(formula: str) -> list:
    """Extract data element IDs from indicator formula."""
    import re
    # Pattern matches #{dataElementId.categoryOptionComboId}
    pattern = r'#\{([a-zA-Z0-9]+)(?:\.[a-zA-Z0-9]+)?\}'
    return re.findall(pattern, formula)

def get_indicator_data_elements(dhis, indicator_id: str) -> dict:
    """Get data elements used in indicator numerator and denominator."""
    indicator = get_indicator(dhis, indicator_id)

    numerator_des = extract_data_elements_from_formula(indicator.get("numerator", ""))
    denominator_des = extract_data_elements_from_formula(indicator.get("denominator", ""))

    return {
        "numerator_data_elements": numerator_des,
        "denominator_data_elements": denominator_des
    }
```

## Indicator Types

| Type | Factor | Description |
|------|--------|-------------|
| Percentage | 100 | Value × 100 |
| Per 1000 | 1000 | Rate per 1000 |
| Per 10000 | 10000 | Rate per 10000 |
| Per 100000 | 100000 | Rate per 100000 |
| Number | 1 | Raw calculated value |

## Formula Syntax

Indicator formulas use this syntax:

| Pattern | Description |
|---------|-------------|
| `#{dataElementId}` | Data element total |
| `#{dataElementId.cocId}` | Data element with disaggregation |
| `#{dataElementId.*}` | Data element all disaggregations |
| `D{programId.dataElementId}` | Program data element |
| `A{programId.attributeId}` | Program attribute |
| `I{programIndicatorId}` | Program indicator |
| `N{indicatorId}` | Indicator (nested) |
| `C{constantId}` | Constant |
| `OUG{orgUnitGroupId}` | Org unit group count |

## Common Filters

| Filter | Description |
|--------|-------------|
| `indicatorType.name:eq:Percentage` | Percentage indicators |
| `name:ilike:coverage` | Name contains |
| `indicatorGroups.id:eq:xyz` | In specific group |
| `numerator:ilike:abc123` | Uses data element in numerator |

## Output Fields

Common fields to request:

```
id,name,shortName,code,description,
numerator,denominator,
numeratorDescription,denominatorDescription,
indicatorType[id,name,factor],
indicatorGroups[id,name],
annualized,decimals
```
