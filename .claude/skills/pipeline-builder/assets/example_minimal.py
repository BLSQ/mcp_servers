"""
Minimal OpenHEXA Pipeline

Demonstrates the simplest possible pipeline structure:
- @pipeline decorator with timeout
- @parameter decorator with basic types
- Simple function-based workflow
- Logging with current_run
"""

from openhexa.sdk import current_run, parameter, pipeline, workspace


@pipeline("my-pipeline", timeout=7200)
@parameter("start_date", name="Start Date", type=str, required=True)
@parameter("limit", name="Record Limit", type=int, default=1000)
@parameter("include_inactive", name="Include Inactive", type=bool, default=False)
@parameter(
    "regions",
    name="Regions",
    type=str,
    multiple=True,
    choices=["North", "South", "East", "West"],
)
def my_pipeline(start_date, limit, include_inactive, regions):
    """Main pipeline function — orchestrates only, no data processing here."""
    current_run.log_info("Starting pipeline")

    data = extract(start_date)
    transformed = transform(data, limit)
    load(transformed)

    current_run.log_info("Pipeline completed")


def extract(start_date):
    current_run.log_info(f"Extracting data from {start_date}...")
    return {"key": "value"}


def transform(data, limit):
    current_run.log_info(f"Transforming (limit={limit})...")
    return data


def load(data):
    current_run.log_info(f"Loaded {len(data)} records")


if __name__ == "__main__":
    my_pipeline()
