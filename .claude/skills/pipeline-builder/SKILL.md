---
name: pipeline-builder
description: Guide for creating OpenHEXA data pipelines. Use when users ask to create a pipeline, build a data pipeline, automate data processing, extract data from DHIS2/IASO, or schedule data workflows. Covers pipeline architecture, @pipeline and @parameter decorators, tasks, file/database I/O, connections, and the OpenHEXA toolbox.
---

# Pipeline Builder

Create OpenHEXA data pipelines for automated data processing.

## Workflow

Before writing a pipeline:

1. **Check existing pipelines** → Use `list_pipelines()` to see workspace pipelines
2. **Check templates** → Use `list_pipeline_templates()` for curated examples
3. **Analyze relevant code** → Study template pipelines for best practices
4. **Design the pipeline**:
   - Parameters and their types (inputs)
   - Workflow: Tasks or simple functions
   - Outputs: files, database tables, datasets
   - Logging and error handling

## Pipeline Structure

### Directory Layout

```
my_pipeline/
├── pipeline.py           # Main pipeline code (required)
├── requirements.txt      # Dependencies (optional)
└── utils.py/            # utils functions to separate from pipeline.py and import it (optional)
```

### Minimal Pipeline

```python
from openhexa.sdk import current_run, pipeline, workspace

@pipeline("my-pipeline-name")
def my_pipeline():
    result = extract_data()
    transformed = transform_data(result)
    load_data(transformed)

@my_pipeline.task
def extract_data():
    current_run.log_info("Extracting data...")
    return {"key": "value"}

@my_pipeline.task
def transform_data(data):
    current_run.log_info("Transforming...")
    return data

@my_pipeline.task
def load_data(data):
    current_run.log_info("Loading...")
    current_run.log_info(f"Loaded {len(data)} records")

if __name__ == "__main__":
    my_pipeline()
```

## The @pipeline Decorator

```python
from openhexa.sdk import pipeline

@pipeline("pipeline-code-name", timeout=7200)  # timeout in seconds
def my_pipeline():
    pass
```

- Default timeout: 4 hours (14400s)
- Maximum timeout: 12 hours (43200s)

## The @parameter Decorator

Stack multiple parameters before the pipeline function:

```python
from openhexa.sdk import pipeline, parameter
from openhexa.sdk import DHIS2Connection, PostgreSQLConnection, Dataset, File

@pipeline("etl-pipeline")
@parameter("start_date", name="Start Date", type=str, required=True)
@parameter("limit", name="Record Limit", type=int, default=1000)
@parameter("include_inactive", name="Include Inactive", type=bool, default=False)
@parameter("regions", name="Regions", type=str, multiple=True,
    choices=["North", "South", "East", "West"])
@parameter("dhis2_conn", name="DHIS2 Connection", type=DHIS2Connection, required=True)
@parameter("output_file", name="Output File", type=File, directory="outputs")
def etl_pipeline(start_date, limit, include_inactive, regions, dhis2_conn, output_file):
    pass
```

### Parameter Types

| Type | Description |
|------|-------------|
| `str` | Text input |
| `int` | Integer input |
| `float` | Decimal input |
| `bool` | Checkbox (True/False) |
| `DHIS2Connection` | DHIS2 server connection |
| `IASOConnection` | IASO server connection |
| `PostgreSQLConnection` | PostgreSQL database |
| `S3Connection` | S3 bucket connection |
| `GCSConnection` | Google Cloud Storage |
| `Dataset` | OpenHEXA dataset |
| `File` | File browser selection |

### DHIS2/IASO Widgets

Auto-populate dropdowns from connected systems:

```python
from openhexa.sdk.pipelines.parameter import DHIS2Widget, IASOWidget

@parameter("dhis2_conn", type=DHIS2Connection, required=True)
@parameter("org_units", name="Organisation Units", type=str, multiple=True,
    widget=DHIS2Widget.ORG_UNITS, connection="dhis2_conn")
@parameter("datasets", name="Datasets", type=str, multiple=True,
    widget=DHIS2Widget.DATASETS, connection="dhis2_conn")
@parameter("data_elements", name="Data Elements", type=str, multiple=True,
    widget=DHIS2Widget.DATA_ELEMENTS, connection="dhis2_conn")
```

Available widgets:
- **DHIS2:** `ORG_UNITS`, `ORG_UNIT_LEVELS`, `ORG_UNIT_GROUPS`, `DATASETS`, `DATA_ELEMENTS`, `INDICATORS`
- **IASO:** `IASO_ORG_UNITS`, `IASO_FORMS`, `IASO_PROJECTS`

### Scheduling Requirements

For a pipeline to be schedulable, ALL parameters must be optional:
- Set `required=False`, OR
- Set `required=True` AND provide a `default` value

## Tasks with @task

Tasks form a DAG (Directed Acyclic Graph) based on dependencies:

```python
@my_pipeline.task
def task_a():
    return "data_a"

@my_pipeline.task
def task_b():
    return "data_b"

@my_pipeline.task
def task_c(a_result, b_result):  # Waits for task_a and task_b
    return f"{a_result} + {b_result}"

def my_pipeline():
    a = task_a()
    b = task_b()      # Runs in parallel with task_a
    c = task_c(a, b)  # Runs after both complete
```


**Rules:**
- Return values must be pickleable
- Pass outputs as individual arguments (not in lists/dicts)
- Don't do data processing in the main pipeline function
- It is not mandatory to write tasks in a pipeline. Only if one wants to have parallelized tasks. But it's perfect to have just functions.

## File I/O

### Reading Files

```python
import pandas as pd
from openhexa.sdk import workspace

@my_pipeline.task
def read_data():
    # Read from workspace files
    path = f"{workspace.files_path}/input/data.csv"
    df = pd.read_csv(path)
    return df
```

### Writing Files

```python
@my_pipeline.task
def save_results(df):
    output_path = f"{workspace.files_path}/output/results.csv"
    df.to_csv(output_path, index=False)
    current_run.add_file_output(output_path)  # Register as output
```

## Database Operations

### Write to Workspace Database

```python
from sqlalchemy import create_engine
from openhexa.sdk import workspace, current_run

@my_pipeline.task
def save_to_database(df):
    engine = create_engine(workspace.database_url)
    df.to_sql(
        "my_table",
        con=engine,
        if_exists="replace",
        index=False
    )
    current_run.add_database_output("my_table")  # Register as output
```

## Using Connections

### DHIS2 with Toolbox

```python
from openhexa.sdk import workspace, DHIS2Connection
from openhexa.toolbox.dhis2 import DHIS2

@my_pipeline.task
def extract_dhis2(dhis2_conn: DHIS2Connection):
    dhis = DHIS2(dhis2_conn, cache_dir=f"{workspace.files_path}/.cache")

    # Get metadata
    org_units = dhis.meta.organisation_units()

    # Get data values
    data = dhis.data_value_sets.get(
        data_element=["abc123"],
        org_unit=["xyz789"],
        period=["2024"]
    )
    return data
```

### IASO with Toolbox

```python
from openhexa.toolbox.iaso import IASO

@my_pipeline.task
def extract_iaso(iaso_conn):
    iaso = IASO(iaso_conn.url, iaso_conn.username, iaso_conn.password)

    forms = iaso.get_form_instances(
        form_ids=[123],
        org_unit_ids=[456]
    )
    return forms
```

### PostgreSQL Connection

```python
import psycopg2
from openhexa.sdk import PostgreSQLConnection

@my_pipeline.task
def query_postgres(pg_conn: PostgreSQLConnection):
    connection = psycopg2.connect(pg_conn.url)
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM my_table")
        return cursor.fetchall()
```

## Logging

```python
from openhexa.sdk import current_run

@my_pipeline.task
def my_task():
    current_run.log_debug("Debug details")
    current_run.log_info("Processing started")
    current_run.log_warning("Missing optional data")
    current_run.log_error("Failed to process record")
    current_run.log_critical("Pipeline cannot continue")
```

## Error Handling

```python
@my_pipeline.task
def safe_extract():
    try:
        data = fetch_external_data()
        current_run.log_info(f"Fetched {len(data)} records")
        return data
    except ConnectionError as e:
        current_run.log_error(f"Connection failed: {e}")
        raise
    except Exception as e:
        current_run.log_critical(f"Unexpected error: {e}")
        raise
```

## OpenHEXA Toolbox

Import the toolbox for specialized data connectors:

```python
# Full import
import openhexa.toolbox

# Specific modules
from openhexa.toolbox.dhis2 import DHIS2
from openhexa.toolbox.iaso import IASO
```

### DHIS2 Toolbox Methods

```python
dhis = DHIS2(connection)

# Metadata
dhis.meta.organisation_units()
dhis.meta.data_elements()
dhis.meta.indicators()
dhis.meta.datasets()

# Data retrieval
dhis.data_value_sets.get(data_element=[...], org_unit=[...], period=[...])
dhis.analytics.get(data_element=[...], org_unit=[...], period=[...])
```

## Deployment

### Requirements File

Create `requirements.txt` for dependencies:

```
openhexa.sdk>=0.1.0
openhexa.toolbox>=0.1.0
pandas>=2.0.0
polars>=0.19.0
```

### Uploading a Pipeline

The pipeline is uploaded as a ZIP file containing:
- `pipeline.py` (required - main code)
- `requirements.txt` (optional - dependencies)
- Additional Python modules (optional)

Use the openhexa_mcp_server tools: `create_pipeline` if the pipeline does not yet exist or `upload_pipeline_version` if it exists and a new version must be uploaded.

## Complete Example

See `assets/example_pipeline.py` for a complete working example that demonstrates:
- DHIS2 connection and data extraction
- Parameter configuration with widgets
- Task-based workflow
- Database output
- Proper logging and error handling
