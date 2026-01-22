Jupyter Notebook Guidelines
When creating or modifying Jupyter notebooks:

The WORKSPACE_DATABASE_URL is '${WORKSPACE_DATABASE_URL}'
Database Access
Always use WORKSPACE_DATABASE_URL to connect to the database:

import os
import pandas as pd
from sqlalchemy import create_engine


engine = create_engine()
df = pd.read_sql("SELECT * FROM my_table LIMIT 100", engine)
Writing Tables to Database
When writing data to the database:

NEVER overwrite an existing table that you did not created - always use check if the table exists first and propose an alternative name for the table to create. If you created the table and you iterate, it's okay:

Explicitly specify column types - don't rely on automatic type inference:


from sqlalchemy import String, Integer, Float, DateTime, Boolean

dtype_mapping = {
    'id': Integer,
    'name': String(255),
    'value': Float,
    'created_at': DateTime,
    'is_active': Boolean
}

df.to_sql('my_new_table', engine, if_exists='replace', index=False, dtype=dtype_mapping)
Ask the user to verify column types before writing - present a summary like:


Proposed column types for table 'my_new_table':
- id: Integer
- name: String(255)
- value: Float
- created_at: DateTime

Please confirm these types are correct before I write to the database.

Save the notebook in the notebooks folder.