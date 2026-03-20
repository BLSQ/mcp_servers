"""
DHIS2 Pipeline Example

Demonstrates:
- DHIS2Connection parameter with widgets (org units, data elements, datasets, indicators)
- DHIS2 toolbox initialization with cache
- Metadata extraction (org units, data elements, indicators, datasets)
- Data value extraction (data_value_sets.get)
- Analytics extraction (analytics.get)
"""

import pandas as pd
from pathlib import Path

from openhexa.sdk import (
    DHIS2Connection,
    current_run,
    parameter,
    pipeline,
    workspace,
)
from openhexa.sdk.pipelines.parameter import DHIS2Widget
from openhexa.toolbox.dhis2 import DHIS2


# --- Parameter configuration with DHIS2 widgets ---

@pipeline("dhis2-extract")
@parameter("dhis2_conn", name="DHIS2 Connection", type=DHIS2Connection, required=True)
@parameter(
    "org_units",
    name="Organisation Units",
    type=str,
    multiple=True,
    required=False,
    widget=DHIS2Widget.ORG_UNITS,
    connection="dhis2_conn",
)
@parameter(
    "data_elements",
    name="Data Elements",
    type=str,
    multiple=True,
    required=False,
    widget=DHIS2Widget.DATA_ELEMENTS,
    connection="dhis2_conn",
)
@parameter(
    "datasets",
    name="Datasets",
    type=str,
    multiple=True,
    required=False,
    widget=DHIS2Widget.DATASETS,
    connection="dhis2_conn",
)
@parameter("periods", name="Periods", type=str, multiple=True, default=["2024"])
def dhis2_extract(dhis2_conn, org_units, data_elements, datasets, periods):
    data = extract_data(dhis2_conn, org_units, data_elements, periods)
    current_run.log_info(f"Extracted {len(data)} records")


# Available DHIS2 widgets:
# DHIS2Widget.ORG_UNITS, DHIS2Widget.ORG_UNIT_LEVELS, DHIS2Widget.ORG_UNIT_GROUPS
# DHIS2Widget.DATASETS, DHIS2Widget.DATA_ELEMENTS, DHIS2Widget.INDICATORS


# --- DHIS2 toolbox usage ---

def init_dhis2(dhis2_conn: DHIS2Connection) -> DHIS2:
    """Initialize DHIS2 client with cache."""
    cache_dir = Path(workspace.files_path) / ".cache"
    return DHIS2(dhis2_conn, cache_dir=cache_dir)


def extract_metadata(dhis2_conn: DHIS2Connection) -> dict:
    """Extract metadata from DHIS2."""
    dhis = init_dhis2(dhis2_conn)

    org_units = dhis.meta.organisation_units()
    data_elements = dhis.meta.data_elements()
    indicators = dhis.meta.indicators()
    datasets = dhis.meta.datasets()

    current_run.log_info(
        f"Metadata: {len(org_units)} org units, "
        f"{len(data_elements)} data elements, "
        f"{len(indicators)} indicators, "
        f"{len(datasets)} datasets"
    )
    return {
        "org_units": org_units,
        "data_elements": data_elements,
        "indicators": indicators,
        "datasets": datasets,
    }


def extract_data(
    dhis2_conn: DHIS2Connection,
    org_units: list[str] | None,
    data_elements: list[str] | None,
    periods: list[str],
) -> pd.DataFrame:
    """Extract data values from DHIS2."""
    dhis = init_dhis2(dhis2_conn)

    data = dhis.data_value_sets.get(
        data_element=data_elements,
        org_unit=org_units,
        period=periods,
    )
    return data


def extract_analytics(
    dhis2_conn: DHIS2Connection,
    data_elements: list[str],
    org_units: list[str],
    periods: list[str],
) -> pd.DataFrame:
    """Extract aggregated analytics from DHIS2."""
    dhis = init_dhis2(dhis2_conn)

    data = dhis.analytics.get(
        data_element=data_elements,
        org_unit=org_units,
        period=periods,
    )
    return data


if __name__ == "__main__":
    dhis2_extract()
