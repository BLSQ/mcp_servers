"""
Example OpenHEXA Pipeline: DHIS2 Data Extract

This pipeline demonstrates:
- DHIS2 connection with widgets for parameter selection
- Task-based workflow with parallel execution
- File and database outputs
- Proper logging and error handling
"""

import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

from openhexa.sdk import (
    DHIS2Connection,
    current_run,
    parameter,
    pipeline,
    workspace,
)
from openhexa.sdk.pipelines.parameter import DHIS2Widget
from openhexa.toolbox.dhis2 import DHIS2


@pipeline("dhis2-data-extract", timeout=7200)
@parameter(
    "dhis2_connection",
    name="DHIS2 Connection",
    type=DHIS2Connection,
    required=True,
    help="Select a DHIS2 connection",
)
@parameter(
    "org_units",
    name="Organisation Units",
    type=str,
    multiple=True,
    required=False,
    widget=DHIS2Widget.ORG_UNITS,
    connection="dhis2_connection",
    help="Select organisation units to extract",
)
@parameter(
    "data_elements",
    name="Data Elements",
    type=str,
    multiple=True,
    required=False,
    widget=DHIS2Widget.DATA_ELEMENTS,
    connection="dhis2_connection",
    help="Select data elements to extract",
)
@parameter(
    "periods",
    name="Periods",
    type=str,
    multiple=True,
    default=["2024"],
    help="Periods to extract (e.g., 2024, 202401, 2024Q1)",
)
@parameter(
    "output_table",
    name="Output Table Name",
    type=str,
    default="dhis2_extract",
    help="Name of the database table to create",
)
def dhis2_data_extract(
    dhis2_connection: DHIS2Connection,
    org_units: list[str] | None,
    data_elements: list[str] | None,
    periods: list[str],
    output_table: str,
):
    """Main pipeline function orchestrating the ETL workflow."""
    current_run.log_info("Starting DHIS2 Data Extract pipeline")

    # Extract phase
    metadata = extract_metadata(dhis2_connection)
    data = extract_data(dhis2_connection, org_units, data_elements, periods)

    # Transform phase
    transformed = transform_data(data, metadata)

    # Load phase
    load_to_database(transformed, output_table)
    save_to_file(transformed)

    current_run.log_info("Pipeline completed successfully")


@dhis2_data_extract.task
def extract_metadata(dhis2_connection: DHIS2Connection) -> dict:
    """Extract metadata for enriching data values."""
    current_run.log_info("Extracting DHIS2 metadata...")

    try:
        cache_dir = Path(workspace.files_path) / ".cache"
        dhis = DHIS2(dhis2_connection, cache_dir=cache_dir)

        org_units = dhis.meta.organisation_units()
        data_elements = dhis.meta.data_elements()

        current_run.log_info(
            f"Extracted metadata: {len(org_units)} org units, {len(data_elements)} data elements"
        )

        return {
            "org_units": org_units,
            "data_elements": data_elements,
        }
    except Exception as e:
        current_run.log_error(f"Failed to extract metadata: {e}")
        raise


@dhis2_data_extract.task
def extract_data(
    dhis2_connection: DHIS2Connection,
    org_units: list[str] | None,
    data_elements: list[str] | None,
    periods: list[str],
) -> pd.DataFrame:
    """Extract data values from DHIS2."""
    current_run.log_info("Extracting DHIS2 data values...")

    if not org_units:
        current_run.log_warning("No org units specified, using root org unit")
        org_units = None

    if not data_elements:
        current_run.log_warning("No data elements specified, extracting all")
        data_elements = None

    try:
        cache_dir = Path(workspace.files_path) / ".cache"
        dhis = DHIS2(dhis2_connection, cache_dir=cache_dir)

        data = dhis.data_value_sets.get(
            data_element=data_elements,
            org_unit=org_units,
            period=periods,
        )

        current_run.log_info(f"Extracted {len(data)} data values")
        return data
    except Exception as e:
        current_run.log_error(f"Failed to extract data: {e}")
        raise


@dhis2_data_extract.task
def transform_data(data: pd.DataFrame, metadata: dict) -> pd.DataFrame:
    """Transform and enrich data with metadata."""
    current_run.log_info("Transforming data...")

    if data.empty:
        current_run.log_warning("No data to transform")
        return data

    try:
        # Add org unit names
        org_units = metadata["org_units"]
        if "orgUnit" in data.columns and not org_units.empty:
            org_unit_names = org_units.set_index("id")["name"].to_dict()
            data["org_unit_name"] = data["orgUnit"].map(org_unit_names)

        # Add data element names
        data_elements = metadata["data_elements"]
        if "dataElement" in data.columns and not data_elements.empty:
            de_names = data_elements.set_index("id")["name"].to_dict()
            data["data_element_name"] = data["dataElement"].map(de_names)

        current_run.log_info(f"Transformed {len(data)} records")
        return data
    except Exception as e:
        current_run.log_error(f"Failed to transform data: {e}")
        raise


@dhis2_data_extract.task
def load_to_database(data: pd.DataFrame, table_name: str) -> None:
    """Load data to the workspace database."""
    current_run.log_info(f"Loading data to database table: {table_name}")

    if data.empty:
        current_run.log_warning("No data to load to database")
        return

    try:
        engine = create_engine(workspace.database_url)
        data.to_sql(
            table_name,
            con=engine,
            if_exists="replace",
            index=False,
        )
        current_run.add_database_output(table_name)
        current_run.log_info(f"Loaded {len(data)} records to table '{table_name}'")
    except Exception as e:
        current_run.log_error(f"Failed to load to database: {e}")
        raise


@dhis2_data_extract.task
def save_to_file(data: pd.DataFrame) -> None:
    """Save data to CSV file."""
    current_run.log_info("Saving data to CSV file...")

    if data.empty:
        current_run.log_warning("No data to save to file")
        return

    try:
        output_path = f"{workspace.files_path}/dhis2_extract.csv"
        data.to_csv(output_path, index=False)
        current_run.add_file_output(output_path)
        current_run.log_info(f"Saved {len(data)} records to {output_path}")
    except Exception as e:
        current_run.log_error(f"Failed to save file: {e}")
        raise


if __name__ == "__main__":
    dhis2_data_extract()
