---
name: dhis2-data-elements
description: Extract data elements and data element groups from DHIS2. Use for data element metadata, groups, or category option combos. Routed via dhis2 skill for general DHIS2 requests.
---

# DHIS2 Data Elements

Extract data element metadata from DHIS2 instances.

**Prerequisites**: Client setup from `dhis2` skill (assumes `dhis` is initialized)

## Get Data Elements

```python
# Get all data elements
data_elements = dhis.meta.data_elements()

# With pagination
data_elements = dhis.meta.data_elements(
    page=1,
    pageSize=500
)

# With filters
data_elements = dhis.meta.data_elements(
    filters=["domainType:eq:AGGREGATE"]  # Only aggregate data elements
)

# Custom fields
data_elements = dhis.meta.data_elements(
    fields="id,name,shortName,valueType,aggregationType,domainType"
)
```

### Get Data Element Groups

```python
# Get all groups
groups = dhis.meta.data_element_groups()

# With filters
groups = dhis.meta.data_element_groups(
    filters=["name:ilike:malaria"]
)
```

### Get Category Option Combos

```python
# Get all category option combos
cocs = dhis.meta.category_option_combos()

# With filters
cocs = dhis.meta.category_option_combos(
    filters=["name:ne:default"]
)
```

## DataFrame Helper Methods

### Add Data Element Names to Data

```python
# If you have a DataFrame with data element IDs
df = dhis.meta.add_dx_name_column(
    dataframe=df,
    dx_id_column="dataElement"
)
# Adds 'dataElement_name' column
```

### Add Category Option Combo Names

```python
df = dhis.meta.add_coc_name_column(
    dataframe=df,
    coc_column="categoryOptionCombo"
)
# Adds 'categoryOptionCombo_name' column
```

## Custom API Endpoint (Alternative)

For endpoints not covered by toolbox methods:

```python
# Get data elements with full details
response = dhis.api.get(
    "dataElements",
    params={
        "fields": "id,name,shortName,code,valueType,aggregationType,"
                  "categoryCombo[id,name,categoryOptionCombos[id,name]]",
        "paging": False
    }
)
data_elements = response.get("dataElements", [])
```

### Get Data Element by ID

```python
def get_data_element(dhis, de_id: str) -> dict:
    """Get single data element with full details."""
    return dhis.api.get(
        f"dataElements/{de_id}",
        params={
            "fields": "*,categoryCombo[*,categoryOptionCombos[*]],"
                      "dataElementGroups[id,name]"
        }
    )
```

### Get Data Elements by Group

```python
def get_data_elements_by_group(dhis, group_id: str) -> list:
    """Get all data elements in a group."""
    response = dhis.api.get(
        "dataElements",
        params={
            "fields": "id,name,shortName,valueType",
            "filter": f"dataElementGroups.id:eq:{group_id}",
            "paging": False
        }
    )
    return response.get("dataElements", [])
```

## Common Filters

| Filter | Description |
|--------|-------------|
| `domainType:eq:AGGREGATE` | Aggregate data elements |
| `domainType:eq:TRACKER` | Tracker data elements |
| `valueType:eq:NUMBER` | Numeric values |
| `valueType:eq:INTEGER` | Integer values |
| `name:ilike:malaria` | Name contains |
| `dataElementGroups.id:eq:xyz` | In specific group |

## Value Types

| Type | Description |
|------|-------------|
| `NUMBER` | Decimal number |
| `INTEGER` | Whole number |
| `INTEGER_POSITIVE` | Positive integer |
| `INTEGER_ZERO_OR_POSITIVE` | Zero or positive |
| `TEXT` | Free text |
| `LONG_TEXT` | Long text |
| `BOOLEAN` | Yes/No |
| `TRUE_ONLY` | Only true value |

## Output Fields

Common fields to request:

```
id,name,shortName,code,
valueType,aggregationType,domainType,
categoryCombo[id,name],
dataElementGroups[id,name],
description,formName
```
