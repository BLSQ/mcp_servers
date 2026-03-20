"""
Database Operations Example

Demonstrates:
- Writing DataFrames to the workspace database (SQLAlchemy)
- Registering database outputs
- Using an external PostgreSQL connection
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine

from openhexa.sdk import (
    PostgreSQLConnection,
    current_run,
    parameter,
    pipeline,
    workspace,
)


@pipeline("db-pipeline")
@parameter("output_table", name="Output Table", type=str, default="my_table")
@parameter("pg_conn", name="External DB", type=PostgreSQLConnection, required=False)
def db_pipeline(output_table, pg_conn):
    df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
    save_to_workspace_db(df, output_table)

    if pg_conn:
        rows = query_external_db(pg_conn, "SELECT * FROM other_table LIMIT 10")
        current_run.log_info(f"Fetched {len(rows)} rows from external DB")


# --- Write to workspace database ---


def save_to_workspace_db(df: pd.DataFrame, table_name: str):
    """Save DataFrame to the workspace database."""
    engine = create_engine(workspace.database_url)
    df.to_sql(table_name, con=engine, if_exists="replace", index=False)
    current_run.add_database_output(table_name)
    current_run.log_info(f"Saved {len(df)} rows to '{table_name}'")


# --- Query an external PostgreSQL connection ---


def query_external_db(pg_conn: PostgreSQLConnection, query: str):
    """Query an external PostgreSQL database using a connection parameter."""
    connection = psycopg2.connect(pg_conn.url)
    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


if __name__ == "__main__":
    db_pipeline()
