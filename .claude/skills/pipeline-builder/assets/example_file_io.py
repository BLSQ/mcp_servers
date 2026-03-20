"""
File I/O Example

Demonstrates:
- Reading files from the workspace
- Writing files to the workspace
- Registering file outputs
"""

import pandas as pd

from openhexa.sdk import current_run, pipeline, workspace


@pipeline("file-pipeline")
def file_pipeline():
    df = read_csv("input/data.csv")
    current_run.log_info(f"Read {len(df)} rows")
    save_csv(df, "output/results.csv")


# --- Reading files ---

def read_csv(relative_path: str) -> pd.DataFrame:
    """Read a CSV file from the workspace files directory."""
    path = f"{workspace.files_path}/{relative_path}"
    return pd.read_csv(path)


# --- Writing files ---

def save_csv(df: pd.DataFrame, relative_path: str):
    """Save a DataFrame as CSV in the workspace files directory."""
    path = f"{workspace.files_path}/{relative_path}"
    df.to_csv(path, index=False)
    current_run.add_file_output(path)
    current_run.log_info(f"Saved {len(df)} rows to {path}")


if __name__ == "__main__":
    file_pipeline()
