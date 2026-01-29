---
name: dhis2-tracker
description: Extract individual-level/case-based data from DHIS2 Tracker. Use for tracked entities, enrollments, events, or relationships. Routed via dhis2 skill for general DHIS2 requests.
---

# DHIS2 Tracker

Extract individual-level and case-based data from DHIS2 Tracker programs.

## Overview

DHIS2 Tracker manages individual-level data through:
- **Tracked Entities**: Persons, commodities, or other tracked objects
- **Enrollments**: A tracked entity's participation in a program
- **Events**: Data capture occurrences within an enrollment
- **Relationships**: Links between tracked entities

## Setup

```python
from openhexa.sdk import workspace
from openhexa.toolbox.dhis2 import DHIS2

# Get DHIS2 connection
dhis2_connection = workspace.dhis2_connection("connection_identifier")
dhis = DHIS2(dhis2_connection, cache_dir=f"{workspace.files_path}/.cache")
```

## Extracting Events (Toolbox Method)

The openhexa.toolbox provides a built-in method for event data extraction.

```python
# Extract events for a program
events_df = dhis.tracker.extract_event_data_values(
    programs=["IpHINAT79UW"],  # Program UID(s)
    org_units=["ImspTQPwCqd"],  # Org unit UID(s)
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# Extract with additional filters
events_df = dhis.tracker.extract_event_data_values(
    programs=["IpHINAT79UW"],
    org_units=["ImspTQPwCqd"],
    start_date="2024-01-01",
    end_date="2024-12-31",
    org_unit_mode="DESCENDANTS"  # Include children org units
)
```

## Extracting Tracked Entities (API Method)

For tracked entities, use `api.get()` directly.

```python
def get_tracked_entities(
    dhis,
    program: str,
    org_unit: str,
    page_size: int = 50,
    fields: str = "*"
) -> list:
    """Get tracked entities enrolled in a program."""
    all_entities = []
    page = 1

    while True:
        response = dhis.api.get(
            "tracker/trackedEntities",
            params={
                "program": program,
                "orgUnit": org_unit,
                "ouMode": "DESCENDANTS",
                "fields": fields,
                "page": page,
                "pageSize": page_size
            }
        )

        entities = response.get("instances", [])
        if not entities:
            break

        all_entities.extend(entities)
        page += 1

        # Check if last page
        if len(entities) < page_size:
            break

    return all_entities

# Usage
entities = get_tracked_entities(
    dhis,
    program="IpHINAT79UW",
    org_unit="ImspTQPwCqd"
)
```

### Convert to DataFrame

```python
import pandas as pd

def tracked_entities_to_df(entities: list, attributes: list = None) -> pd.DataFrame:
    """Convert tracked entities to DataFrame with attributes as columns."""
    rows = []
    for entity in entities:
        row = {
            "trackedEntity": entity.get("trackedEntity"),
            "orgUnit": entity.get("orgUnit"),
            "createdAt": entity.get("createdAt"),
            "updatedAt": entity.get("updatedAt")
        }

        # Extract attributes
        for attr in entity.get("attributes", []):
            attr_id = attr.get("attribute")
            row[attr_id] = attr.get("value")

        rows.append(row)

    df = pd.DataFrame(rows)

    # Filter to specific attributes if provided
    if attributes:
        keep_cols = ["trackedEntity", "orgUnit", "createdAt", "updatedAt"] + attributes
        df = df[[c for c in keep_cols if c in df.columns]]

    return df
```

## Extracting Enrollments (API Method)

```python
def get_enrollments(
    dhis,
    program: str,
    org_unit: str,
    enrollment_status: str = None
) -> list:
    """Get enrollments for a program."""
    params = {
        "program": program,
        "orgUnit": org_unit,
        "ouMode": "DESCENDANTS",
        "fields": "enrollment,trackedEntity,program,status,enrolledAt,occurredAt,orgUnit"
    }

    if enrollment_status:
        params["status"] = enrollment_status  # ACTIVE, COMPLETED, CANCELLED

    all_enrollments = []
    page = 1

    while True:
        params["page"] = page
        response = dhis.api.get("tracker/enrollments", params=params)

        enrollments = response.get("instances", [])
        if not enrollments:
            break

        all_enrollments.extend(enrollments)

        if len(enrollments) < 50:
            break
        page += 1

    return all_enrollments
```

## Extracting Events via API (Alternative)

For more control than the toolbox method:

```python
def get_events(
    dhis,
    program: str,
    org_unit: str,
    start_date: str = None,
    end_date: str = None,
    program_stage: str = None
) -> list:
    """Get events with custom filtering."""
    params = {
        "program": program,
        "orgUnit": org_unit,
        "ouMode": "DESCENDANTS",
        "fields": "event,enrollment,trackedEntity,program,programStage,orgUnit,occurredAt,status,dataValues"
    }

    if start_date:
        params["occurredAfter"] = start_date
    if end_date:
        params["occurredBefore"] = end_date
    if program_stage:
        params["programStage"] = program_stage

    all_events = []
    page = 1

    while True:
        params["page"] = page
        response = dhis.api.get("tracker/events", params=params)

        events = response.get("instances", [])
        if not events:
            break

        all_events.extend(events)

        if len(events) < 50:
            break
        page += 1

    return all_events

def events_to_df(events: list) -> pd.DataFrame:
    """Convert events to DataFrame with data values as columns."""
    rows = []
    for event in events:
        row = {
            "event": event.get("event"),
            "enrollment": event.get("enrollment"),
            "trackedEntity": event.get("trackedEntity"),
            "programStage": event.get("programStage"),
            "orgUnit": event.get("orgUnit"),
            "occurredAt": event.get("occurredAt"),
            "status": event.get("status")
        }

        for dv in event.get("dataValues", []):
            row[dv.get("dataElement")] = dv.get("value")

        rows.append(row)

    return pd.DataFrame(rows)
```

## Extracting Relationships (API Method)

```python
def get_relationships(dhis, tracked_entity: str) -> list:
    """Get relationships for a tracked entity."""
    response = dhis.api.get(
        "tracker/relationships",
        params={
            "trackedEntity": tracked_entity,
            "fields": "relationship,relationshipType,from,to"
        }
    )
    return response.get("instances", [])
```

## Common Query Parameters

| Parameter | Description | Values |
|-----------|-------------|--------|
| `ouMode` | Org unit selection mode | `SELECTED`, `DESCENDANTS`, `CHILDREN`, `ACCESSIBLE` |
| `status` | Enrollment/event status | `ACTIVE`, `COMPLETED`, `CANCELLED` |
| `occurredAfter` | Events after date | ISO date (2024-01-01) |
| `occurredBefore` | Events before date | ISO date (2024-12-31) |
| `fields` | Fields to return | `*`, specific fields comma-separated |
| `pageSize` | Results per page | Integer (default 50, max 1000) |

## Enriching with Metadata

```python
def add_attribute_names(df: pd.DataFrame, dhis, attribute_columns: list) -> pd.DataFrame:
    """Replace attribute IDs with display names in column headers."""
    for attr_id in attribute_columns:
        if attr_id in df.columns:
            try:
                attr_meta = dhis.api.get(f"trackedEntityAttributes/{attr_id}", params={"fields": "displayName"})
                df = df.rename(columns={attr_id: attr_meta.get("displayName", attr_id)})
            except:
                pass
    return df

def add_data_element_names(df: pd.DataFrame, dhis, de_columns: list) -> pd.DataFrame:
    """Replace data element IDs with display names in column headers."""
    for de_id in de_columns:
        if de_id in df.columns:
            try:
                de_meta = dhis.api.get(f"dataElements/{de_id}", params={"fields": "displayName"})
                df = df.rename(columns={de_id: de_meta.get("displayName", de_id)})
            except:
                pass
    return df
```

## Performance Tips

1. **Use pagination** - Always paginate for large datasets
2. **Specify fields** - Request only needed fields to reduce payload
3. **Filter by date** - Use `occurredAfter`/`occurredBefore` for events
4. **Use ouMode wisely** - `DESCENDANTS` can be slow for large hierarchies
5. **Prefer toolbox** - Use `extract_event_data_values()` when possible for events
