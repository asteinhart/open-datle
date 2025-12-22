# DuckDB Database Setup

## Requirements

```bash
pip install duckdb
```

## Setup Instructions

### 1. Create Database and Tables

```bash
cd db
python init_db.py
```

This creates `open_datle.db` with all necessary tables.

### 2. Load Sample Data

```bash
python seed_db.py
```

This populates the database with sample users, datasets, schedules, and user guesses.

## Python API Usage

The `db_utils.py` file provides convenient functions to interact with the database:

```python
from db_utils import (
    find_dataset_by_date,
    get_dataset,
    save_user_guess_line,
    get_user_guess,
    create_user
)

# Find dataset by date
result = find_dataset_by_date('20240101')
# Returns: {'date': '20240101', 'dataset_id': 1}

# Get dataset details
dataset = get_dataset(1)
# Returns: {
#     'dataset_id': 1,
#     'title': 'NYC Temperature Over Time',
#     'x_axis_label': 'Year',
#     'y_axis_label': 'Temperature (°F)',
#     'data': [...],
#     'type': 'line',
#     'source': '...'
# }

# Save user guess
save_user_guess_line(
    user_id=1,
    dataset_id=1,
    user_line=[{"x": 2020, "y": 54}, {"x": 2021, "y": 56}]
)

# Get user's guess
guess = get_user_guess(user_id=1, dataset_id=1)

# Create new user
user_id = create_user('newuser@example.com')
```

## Direct DuckDB Queries

You can also use DuckDB directly:

```python
import duckdb

con = duckdb.connect('open_datle.db')

# Query datasets
datasets = con.execute("SELECT * FROM dataset").fetchall()

# Query with parameters
result = con.execute("""
    SELECT * FROM schedule WHERE day = ?
""", ['2024-01-01']).fetchone()

con.close()
```

## Database Schema

- **users**: user_id, email, created_at
- **dataset**: dataset_id, title, x_axis_label, y_axis_label, data_id (JSON), type, source, created_at
- **schedule**: id, day, dataset_id
- **user_data_line**: id, user_id, dataset_id, user_line (JSON), submitted_at

## Testing

Run the test suite:

```bash
python db_utils.py
```

This will test all the database functions with sample data.
