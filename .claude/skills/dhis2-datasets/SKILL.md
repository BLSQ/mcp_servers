---
name: dhis2-datasets
description: Extract datasets metadata from DHIS2. Use for dataset definitions, data entry forms, or reporting frequencies. Routed via dhis2 skill for general DHIS2 requests.
---

# DHIS2 Datasets

Extract dataset metadata from DHIS2 instances.

## Toolbox Methods (Recommended)

The OpenHEXA toolbox provides built-in methods for datasets.

### Setup

```python
from openhexa.sdk import workspace, DHIS2Connection
from openhexa.toolbox.dhis2 import DHIS2

dhis = DHIS2(dhis2_connection, cache_dir=f"{workspace.files_path}/.cache")
```

### Get Datasets

```python
# Get all datasets
datasets = dhis.meta.datasets()

# With pagination
datasets = dhis.meta.datasets(
    page=1,
    pageSize=100
)

# With filters
datasets = dhis.meta.datasets(
    filters=["name:ilike:monthly"]
)

# Custom fields
datasets = dhis.meta.datasets(
    fields="id,name,shortName,periodType,dataSetElements[dataElement[id,name]]"
)
```

## Custom API Endpoint (Alternative)

For endpoints not covered by toolbox methods:

```python
# Get datasets with full details
response = dhis.api.get(
    "dataSets",
    params={
        "fields": "id,name,shortName,code,periodType,"
                  "dataSetElements[dataElement[id,name]],"
                  "organisationUnits[id,name]",
        "paging": False
    }
)
datasets = response.get("dataSets", [])
```

### Get Dataset by ID

```python
def get_dataset(dhis, dataset_id: str) -> dict:
    """Get single dataset with full details."""
    return dhis.api.get(
        f"dataSets/{dataset_id}",
        params={
            "fields": "*,dataSetElements[*,dataElement[id,name,valueType]],"
                      "organisationUnits[id,name,level],"
                      "sections[id,name,dataElements[id,name]]"
        }
    )
```

### Get Datasets for Org Unit

```python
def get_datasets_for_org_unit(dhis, org_unit_id: str) -> list:
    """Get all datasets assigned to an org unit."""
    response = dhis.api.get(
        "dataSets",
        params={
            "fields": "id,name,periodType",
            "filter": f"organisationUnits.id:eq:{org_unit_id}",
            "paging": False
        }
    )
    return response.get("dataSets", [])
```

### Get Dataset Data Elements

```python
def get_dataset_data_elements(dhis, dataset_id: str) -> list:
    """Get all data elements in a dataset."""
    dataset = dhis.api.get(
        f"dataSets/{dataset_id}",
        params={
            "fields": "dataSetElements[dataElement[id,name,valueType,categoryCombo[id,name]]]"
        }
    )
    return [
        dse["dataElement"]
        for dse in dataset.get("dataSetElements", [])
    ]
```

### Get Dataset Sections

```python
def get_dataset_sections(dhis, dataset_id: str) -> list:
    """Get dataset form sections."""
    dataset = dhis.api.get(
        f"dataSets/{dataset_id}",
        params={
            "fields": "sections[id,name,sortOrder,dataElements[id,name]]"
        }
    )
    return dataset.get("sections", [])
```

## Period Types

| Period Type | Description | Example |
|-------------|-------------|---------|
| `Daily` | Daily reporting | 20240115 |
| `Weekly` | ISO week | 2024W03 |
| `Monthly` | Monthly | 202401 |
| `Quarterly` | Quarter | 2024Q1 |
| `SixMonthly` | Half-year | 2024S1 |
| `Yearly` | Annual | 2024 |
| `FinancialApril` | Fiscal year (Apr) | 2024April |
| `FinancialJuly` | Fiscal year (Jul) | 2024July |
| `FinancialOct` | Fiscal year (Oct) | 2024Oct |

## Common Filters

| Filter | Description |
|--------|-------------|
| `periodType:eq:Monthly` | Monthly datasets |
| `name:ilike:malaria` | Name contains |
| `organisationUnits.id:eq:xyz` | Assigned to org unit |
| `dataSetElements.dataElement.id:eq:abc` | Contains data element |

## Output Fields

Common fields to request:

```
id,name,shortName,code,
periodType,openFuturePeriods,
expiryDays,timelyDays,
dataSetElements[dataElement[id,name]],
organisationUnits[id,name],
sections[id,name,sortOrder]
```

## Completeness Reporting

### Get Dataset Completeness

```python
def get_dataset_completeness(dhis, dataset_id: str, period: str, org_unit_id: str) -> dict:
    """Get completeness stats for a dataset."""
    response = dhis.api.get(
        "completeDataSetRegistrations",
        params={
            "dataSet": dataset_id,
            "period": period,
            "orgUnit": org_unit_id,
            "children": True
        }
    )
    return response
```
