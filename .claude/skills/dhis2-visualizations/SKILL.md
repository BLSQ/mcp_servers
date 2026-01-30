---
name: dhis2-visualizations
description: Extract DHIS2 visualizations (favorites) metadata and data. Use for chart/table configurations, visualization data, or dashboard items. Routed via dhis2 skill for general DHIS2 requests.
---

# DHIS2 Visualizations

Extract visualization (favorite) metadata and data from DHIS2.

**Prerequisites**: Client setup from `dhis2` skill (assumes `dhis` is initialized)

**Note:** The OpenHEXA toolbox does not have built-in methods for visualizations. Use `dhis.api.get()` with custom endpoints.

## Get Visualization Metadata

### List All Visualizations

```python
def list_visualizations(dhis, page_size: int = 50) -> list:
    """List all visualizations in the system."""
    response = dhis.api.get(
        "visualizations",
        params={
            "fields": "id,name,type,displayName,created,lastUpdated",
            "paging": False
        }
    )
    return response.get("visualizations", [])
```

### Get Visualization by ID

```python
def get_visualization_metadata(dhis, visualization_id: str) -> dict:
    """Get full metadata for a visualization."""
    return dhis.api.get(
        f"visualizations/{visualization_id}",
        params={
            "fields": "*,"
                      "dataDimensionItems[*,indicator[id,displayName],dataElement[id,displayName]],"
                      "organisationUnits[id,displayName],"
                      "periods[*],"
                      "columns[*],"
                      "rows[*],"
                      "filters[*],"
                      "relativePeriods[*],"
                      "legendSet[id,name]"
        }
    )
```

### Search Visualizations

```python
def search_visualizations(dhis, search_term: str) -> list:
    """Search visualizations by name."""
    response = dhis.api.get(
        "visualizations",
        params={
            "fields": "id,name,type,displayName",
            "filter": f"displayName:ilike:{search_term}",
            "paging": False
        }
    )
    return response.get("visualizations", [])
```

## Get Visualization Data

### Extract Data from Visualization

```python
def get_visualization_data(dhis, visualization_id: str) -> tuple[pd.DataFrame, dict]:
    """
    Extract analytics data from a DHIS2 visualization.

    Returns a DataFrame with the data and metadata for ID-to-name mapping.
    """
    try:
        response = dhis.api.get(
            f"visualizations/{visualization_id}/data.json"
        )

        headers = response.get("headers", [])
        rows = response.get("rows", [])

        if not rows:
            return pd.DataFrame(), response

        # Create column names from headers
        columns = [
            h.get("name", h.get("column", f"col_{i}"))
            for i, h in enumerate(headers)
        ]
        df = pd.DataFrame(rows, columns=columns)

        # Extract metadata for mapping
        metadata = response.get("metaData", {})

        return df, metadata

    except Exception as e:
        print(f"Error extracting visualization data: {e}")
        return pd.DataFrame(), {}
```

### Map IDs to Names

```python
def map_ids_to_names(df: pd.DataFrame, metadata: dict, column: str) -> pd.DataFrame:
    """Map DHIS2 IDs to display names using visualization metadata."""
    items = metadata.get("items", {})

    if column in df.columns:
        df[f"{column}_name"] = df[column].map(
            lambda x: items.get(x, {}).get("name", x)
        )

    return df
```

## Get Dashboard Visualizations

### List Dashboards

```python
def list_dashboards(dhis) -> list:
    """List all dashboards."""
    response = dhis.api.get(
        "dashboards",
        params={
            "fields": "id,name,displayName,dashboardItems[id,type,visualization[id,name]]",
            "paging": False
        }
    )
    return response.get("dashboards", [])
```

### Get Dashboard Items

```python
def get_dashboard_visualizations(dhis, dashboard_id: str) -> list:
    """Get all visualizations from a dashboard."""
    dashboard = dhis.api.get(
        f"dashboards/{dashboard_id}",
        params={
            "fields": "dashboardItems[id,type,visualization[id,name,type],"
                      "map[id,name],eventChart[id,name],eventReport[id,name]]"
        }
    )
    return dashboard.get("dashboardItems", [])
```

## Get Maps

### Get Map Metadata

```python
def get_map_metadata(dhis, map_id: str) -> dict:
    """Get map configuration."""
    return dhis.api.get(
        f"maps/{map_id}",
        params={
            "fields": "*,mapViews[*,columns[*],rows[*],filters[*],"
                      "organisationUnits[id,name],dataDimensionItems[*]]"
        }
    )
```

### Get Map Data

```python
def get_map_data(dhis, map_id: str) -> tuple[pd.DataFrame, dict]:
    """Get data for a map visualization."""
    response = dhis.api.get(
        f"maps/{map_id}/data.json"
    )

    headers = response.get("headers", [])
    rows = response.get("rows", [])
    columns = [h.get("name", f"col_{i}") for i, h in enumerate(headers)]

    return pd.DataFrame(rows, columns=columns), response.get("metaData", {})
```

## Visualization Types

| Type | Description |
|------|-------------|
| `COLUMN` | Vertical bar chart |
| `STACKED_COLUMN` | Stacked vertical bars |
| `BAR` | Horizontal bar chart |
| `STACKED_BAR` | Stacked horizontal bars |
| `LINE` | Line chart |
| `AREA` | Area chart |
| `PIE` | Pie chart |
| `RADAR` | Radar/spider chart |
| `GAUGE` | Gauge chart |
| `YEAR_OVER_YEAR_LINE` | Year comparison |
| `YEAR_OVER_YEAR_COLUMN` | Year comparison bars |
| `SINGLE_VALUE` | Single KPI value |
| `PIVOT_TABLE` | Pivot table |
| `SCATTER` | Scatter plot |

## Complete Example

```python
def extract_and_process_visualization(dhis, visualization_id: str) -> pd.DataFrame:
    """Extract visualization data with names."""

    # Get metadata first
    meta = get_visualization_metadata(dhis, visualization_id)
    print(f"Visualization: {meta.get('displayName')}")
    print(f"Type: {meta.get('type')}")

    # Get data
    df, metadata = get_visualization_data(dhis, visualization_id)

    if df.empty:
        return df

    # Map common dimensions to names
    for col in ["dx", "ou", "pe"]:
        df = map_ids_to_names(df, metadata, col)

    return df

# Usage
df = extract_and_process_visualization(dhis, "DkPKc1EUmC2")
print(df.head())
```

## Error Handling

```python
def safe_get_visualization(dhis, visualization_id: str) -> dict | None:
    """Safely get visualization with error handling."""
    try:
        return get_visualization_metadata(dhis, visualization_id)
    except Exception as e:
        if "404" in str(e):
            print(f"Visualization {visualization_id} not found")
        elif "403" in str(e):
            print(f"Access denied to visualization {visualization_id}")
        else:
            print(f"Error: {e}")
        return None
```
