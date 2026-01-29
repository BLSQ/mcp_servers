---
name: sql-tables
description: Read and write SQL tables from Python code (pipelines or notebooks). Use when needing to query database tables, write DataFrames to database, or manage table schemas. Provides best practices for SQLAlchemy, type mapping, and safe table operations.
---

# SQL Tables

Best practices for reading and writing SQL tables from Python code in OpenHEXA pipelines and notebooks.

## Database Connection

### Using Environment Variable

```python
import os
import pandas as pd
from sqlalchemy import create_engine

# Get database URL from environment
db_url = os.environ.get("WORKSPACE_DATABASE_URL")
engine = create_engine(db_url)
```

### Using OpenHEXA SDK (Pipelines)

```python
from openhexa.sdk import workspace

# Get database connection from workspace
db_url = workspace.database_url
engine = create_engine(db_url)
```

## Reading Tables

### Basic Query

```python
# Read entire table (use LIMIT for large tables)
df = pd.read_sql("SELECT * FROM my_table LIMIT 1000", engine)

# Read with specific columns
df = pd.read_sql("SELECT id, name, value FROM my_table", engine)

# Read with filters
df = pd.read_sql("""
    SELECT * FROM my_table
    WHERE created_at > '2024-01-01'
    AND status = 'active'
""", engine)
```

### Using Parameters (Prevent SQL Injection)

```python
from sqlalchemy import text

# ALWAYS use parameters for user-provided values
query = text("SELECT * FROM my_table WHERE org_unit = :ou AND period = :pe")
df = pd.read_sql(query, engine, params={"ou": org_unit_id, "pe": period})
```

### Check Table Exists

```python
from sqlalchemy import inspect

def table_exists(engine, table_name: str) -> bool:
    """Check if a table exists in the database."""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

# Usage
if table_exists(engine, "my_table"):
    df = pd.read_sql("SELECT * FROM my_table", engine)
```

### Get Table Schema

```python
from sqlalchemy import inspect

def get_table_columns(engine, table_name: str) -> list:
    """Get column names and types for a table."""
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    return [(col["name"], str(col["type"])) for col in columns]

# Usage
columns = get_table_columns(engine, "my_table")
for name, dtype in columns:
    print(f"  {name}: {dtype}")
```

## Writing Tables

### CRITICAL: Safety Rules

1. **NEVER overwrite existing tables you didn't create**
2. **Always check if table exists first**
3. **Explicitly specify column types** - don't rely on auto-inference
4. **Ask user to confirm types before writing**

### Check Before Writing

```python
from sqlalchemy import inspect

def safe_table_name(engine, proposed_name: str) -> str:
    """Return a safe table name, appending suffix if exists."""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    if proposed_name not in existing_tables:
        return proposed_name

    # Table exists - propose alternative
    suffix = 1
    while f"{proposed_name}_{suffix}" in existing_tables:
        suffix += 1

    return f"{proposed_name}_{suffix}"

# Usage
table_name = safe_table_name(engine, "analysis_results")
print(f"Will write to: {table_name}")
```

### Type Mapping

Always explicitly define column types:

```python
from sqlalchemy import String, Integer, Float, DateTime, Boolean, Text, Date

# Common type mappings
dtype_mapping = {
    # Identifiers
    "id": Integer,
    "uid": String(11),           # DHIS2 UIDs are 11 chars

    # Text fields
    "name": String(255),
    "description": Text,         # For long text
    "code": String(50),

    # Numeric fields
    "value": Float,
    "count": Integer,
    "amount": Float,

    # Date/time fields
    "created_at": DateTime,
    "updated_at": DateTime,
    "date": Date,
    "period": String(10),        # DHIS2 periods like "202401"

    # Boolean fields
    "is_active": Boolean,
    "is_deleted": Boolean,

    # Foreign keys / references
    "org_unit_id": String(11),
    "data_element_id": String(11),
    "indicator_id": String(11),
}
```

### Write with Explicit Types

```python
# Define types for your DataFrame columns
dtype_mapping = {
    "org_unit": String(11),
    "period": String(10),
    "indicator": String(11),
    "value": Float,
    "created_at": DateTime,
}

# Write to database
df.to_sql(
    name="my_analysis_results",
    con=engine,
    if_exists="replace",      # or "append" for adding rows
    index=False,              # Don't write DataFrame index
    dtype=dtype_mapping
)
```

### Confirm Types Before Writing (Best Practice)

```python
def propose_column_types(df: pd.DataFrame) -> dict:
    """Propose SQLAlchemy types based on DataFrame dtypes."""
    from sqlalchemy import String, Integer, Float, DateTime, Boolean, Text

    type_map = {
        "int64": Integer,
        "int32": Integer,
        "float64": Float,
        "float32": Float,
        "bool": Boolean,
        "datetime64[ns]": DateTime,
        "object": String(255),  # Default string length
    }

    proposed = {}
    for col in df.columns:
        dtype_str = str(df[col].dtype)
        proposed[col] = type_map.get(dtype_str, String(255))

        # Adjust string length based on max value
        if dtype_str == "object":
            max_len = df[col].astype(str).str.len().max()
            if max_len > 255:
                proposed[col] = Text
            elif max_len <= 50:
                proposed[col] = String(50)
            elif max_len <= 100:
                proposed[col] = String(100)

    return proposed

# Usage
proposed_types = propose_column_types(df)
print("Proposed column types:")
for col, dtype in proposed_types.items():
    print(f"  - {col}: {dtype}")
print("\nPlease confirm these types are correct before writing.")
```

## Common Patterns

### Upsert (Insert or Update)

```python
from sqlalchemy.dialects.postgresql import insert

def upsert_dataframe(df: pd.DataFrame, table_name: str, engine, key_columns: list):
    """Insert or update rows based on key columns."""
    from sqlalchemy import Table, MetaData

    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=engine)

    for _, row in df.iterrows():
        stmt = insert(table).values(**row.to_dict())
        stmt = stmt.on_conflict_do_update(
            index_elements=key_columns,
            set_={c: stmt.excluded[c] for c in df.columns if c not in key_columns}
        )
        engine.execute(stmt)
```

### Chunked Writing (Large DataFrames)

```python
def write_chunked(df: pd.DataFrame, table_name: str, engine, chunk_size: int = 10000):
    """Write large DataFrame in chunks."""
    total_rows = len(df)

    for i in range(0, total_rows, chunk_size):
        chunk = df.iloc[i:i + chunk_size]

        # First chunk: replace, subsequent: append
        if_exists = "replace" if i == 0 else "append"

        chunk.to_sql(
            name=table_name,
            con=engine,
            if_exists=if_exists,
            index=False
        )

        print(f"Written {min(i + chunk_size, total_rows)}/{total_rows} rows")
```

### Transaction Management

```python
from sqlalchemy.orm import Session

def write_with_transaction(df: pd.DataFrame, table_name: str, engine):
    """Write with explicit transaction for rollback on error."""
    with engine.begin() as conn:
        df.to_sql(
            name=table_name,
            con=conn,
            if_exists="replace",
            index=False
        )
        # Commit happens automatically at end of 'with' block
        # Rollback happens automatically on exception
```

## Type Reference

| Python/Pandas Type | SQLAlchemy Type | PostgreSQL Type |
|-------------------|-----------------|-----------------|
| `int64` | `Integer` | `INTEGER` |
| `float64` | `Float` | `DOUBLE PRECISION` |
| `bool` | `Boolean` | `BOOLEAN` |
| `datetime64` | `DateTime` | `TIMESTAMP` |
| `object` (short) | `String(n)` | `VARCHAR(n)` |
| `object` (long) | `Text` | `TEXT` |
| `date` | `Date` | `DATE` |

## Checklist Before Writing

- [ ] Table name checked for conflicts
- [ ] Column types explicitly defined
- [ ] User confirmed column types
- [ ] Using `index=False` (unless index is needed)
- [ ] Large DataFrames chunked appropriately
- [ ] Connection properly closed after use
