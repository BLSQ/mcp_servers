"""
IASO Pipeline Example

Demonstrates:
- IASOConnection parameter with widgets (org units, forms, projects)
- IASO toolbox initialization
- Form instance extraction
"""

from openhexa.sdk import (
    IASOConnection,
    current_run,
    parameter,
    pipeline,
)
from openhexa.sdk.pipelines.parameter import IASOWidget
from openhexa.toolbox.iaso import IASO


# --- Parameter configuration with IASO widgets ---


@pipeline("iaso-extract")
@parameter("iaso_conn", name="IASO Connection", type=IASOConnection, required=True)
@parameter(
    "org_units",
    name="Organisation Units",
    type=str,
    multiple=True,
    required=False,
    widget=IASOWidget.IASO_ORG_UNITS,
    connection="iaso_conn",
)
@parameter(
    "forms",
    name="Forms",
    type=str,
    multiple=True,
    required=False,
    widget=IASOWidget.IASO_FORMS,
    connection="iaso_conn",
)
def iaso_extract(iaso_conn, org_units, forms):
    data = extract_forms(iaso_conn, form_ids=[123], org_unit_ids=[456])
    current_run.log_info(f"Extracted {len(data)} form instances")


# Available IASO widgets:
# IASOWidget.IASO_ORG_UNITS, IASOWidget.IASO_FORMS, IASOWidget.IASO_PROJECTS


# --- IASO toolbox usage ---


def extract_forms(iaso_conn: IASOConnection, form_ids: list, org_unit_ids: list):
    """Extract form instances from IASO."""
    iaso = IASO(iaso_conn.url, iaso_conn.username, iaso_conn.password)

    forms = iaso.get_form_instances(
        form_ids=form_ids,
        org_unit_ids=org_unit_ids,
    )
    return forms


if __name__ == "__main__":
    iaso_extract()
