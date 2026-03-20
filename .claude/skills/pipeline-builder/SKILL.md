---
name: pipeline-builder
description: Guide for creating OpenHEXA data pipelines. Use when users ask to create a pipeline, build a data pipeline, automate data processing, or schedule data workflows.
---

# Goal

Ensure every OpenHEXA pipeline is well-specified, correctly structured, and follows SDK conventions before any code is written.

# Rules

You must:
- Gather requirements before writing code (check for `requirements.md` or ask the user)
- Use `@pipeline` and `@parameter` decorators from `openhexa.sdk`
- Keep the main pipeline function as an orchestrator — delegate work to plain functions
- Log progress with `current_run.log_info/warning/error`
- Register outputs with `current_run.add_file_output()` or `current_run.add_database_output()`
- Make all optional parameters have a default value if the pipeline must be schedulable. Ask the user to provide them.

You must not:
- Do data processing directly in the `@pipeline`-decorated function
- Hardcode connection credentials — always use SDK connection types
- Skip the requirements step without explicit user consent
- Create unnecessary tasks — prefer simple functions over `@task`

# Workflow

1. **Check for requirements** → Look for `requirements.md` in the pipeline folder. If missing, ask the user to define or skip requirements. If present but incomplete, ask clarifying questions (act as product owner: challenge the goal, parameters, outputs, error handling).
2. **Check existing pipelines** → Use `list_pipelines()` to see workspace pipelines and avoid duplicates.
3. **Check templates** → Use `list_pipeline_templates()` for curated starting points.
4. **Design the pipeline** → Define parameters (inputs), workflow (functions), outputs (files/tables/datasets), and error handling.
5. **Write the code** → Create `pipeline.py` following the structure below. Add `requirements.txt` if needed. Optionally split helpers into `utils.py`.
6. **Deploy** → Use `create_pipeline` or `upload_pipeline_version` from the openhexa MCP server.

# Pipeline Structure

```
my_pipeline/
├── pipeline.py           # Main pipeline code (required)
├── requirements.txt      # Dependencies (optional)
└── utils.py              # Helper functions (optional)
```

```python
from openhexa.sdk import current_run, pipeline, parameter, workspace

@pipeline("my-pipeline-name", timeout=7200)  # timeout in seconds (default: 4h, max: 12h)
@parameter("start_date", name="Start Date", type=str, required=True)
@parameter("limit", name="Record Limit", type=int, default=1000)
def my_pipeline(start_date, limit):
    data = extract(start_date)
    transformed = transform(data, limit)
    load(transformed)

def extract(start_date):
    current_run.log_info(f"Extracting from {start_date}...")
    return {"key": "value"}

def transform(data, limit):
    current_run.log_info("Transforming...")
    return data

def load(data):
    current_run.log_info("Loading...")

if __name__ == "__main__":
    my_pipeline()
```

## Parameter Types

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

# Anti-patterns

- Do not invent requirements — always validate with the user
- Do not skip the requirements step without consent
- Do not put transformation logic in the `@pipeline` function
- Do not hardcode credentials or URLs
- Do not create overly complex pipelines — prefer simple, readable functions

# Available tools

From the `openhexa-mcp` server (if installed):
- `list_pipelines()` — list workspace pipelines
- `list_pipeline_templates()` — list curated templates
- `create_pipeline` — create a new pipeline
- `upload_pipeline_version` — upload a new version of an existing pipeline
- `list_connections()` — list available connections (DHIS2, IASO, PostgreSQL, etc.)

# Assets — On-Demand References

Only consult these when relevant to the user's request:

- For a **minimal pipeline example**: see `assets/example_minimal.py`
- For pipelines interacting with **DHIS2**: see `assets/example_dhis2.py`
- For pipelines interacting with **IASO**: see `assets/example_iaso.py`
- For pipelines writing to a **database**: see `assets/example_database.py`
- For pipelines reading/writing **files**: see `assets/example_file_io.py`
- For a **complete DHIS2 ETL pipeline**: see `assets/example_pipeline.py`

# Policy

- Prefer updating `requirements.md` over creating new planning documents
- Prefer simple functions over `@task` decorators
- Prefer `openhexa.toolbox` connectors over raw API calls
- Always check `list_connections()` before generating connection code