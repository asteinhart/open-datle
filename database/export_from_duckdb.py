"""
Export data from DuckDB to JSON files for migration to Neon PostgreSQL
"""

import duckdb
import json
import os

# Connect to DuckDB
con = duckdb.connect("database/open_datle.db")

# Create export directory
os.makedirs("database/export", exist_ok=True)

# Export users
users = con.execute("SELECT * FROM users").fetchall()
users_data = []
for row in users:
    users_data.append(
        {
            "user_id": row[0],
            "email": row[1],
            "created_at": str(row[2]) if row[2] else None,
        }
    )

with open("database/export/users.json", "w") as f:
    json.dump(users_data, f, indent=2)

print(f"Exported {len(users_data)} users")

# Export datasets_meta
datasets = con.execute("SELECT * FROM datasets_meta").fetchall()
datasets_data = []
for row in datasets:
    datasets_data.append(
        {
            "dataset_id": row[0],
            "title": row[1],
            "type": row[2],
            "city": row[3],
            "subtitle": row[4],
            "y_min": row[5],
            "y_max": row[6],
            "source": row[7],
            "note": row[8],
            "created_at": str(row[9]) if len(row) > 9 and row[9] else None,
        }
    )

with open("database/export/datasets_meta.json", "w") as f:
    json.dump(datasets_data, f, indent=2)

print(f"Exported {len(datasets_data)} datasets")

# Export data points
data_points = con.execute(
    "SELECT * FROM data ORDER BY dataset_id, sort_order"
).fetchall()
data_data = []
for row in data_points:
    data_data.append(
        {
            "data_id": row[0],
            "dataset_id": row[1],
            "x": row[2],
            "y": row[3],
            "sort_order": row[4],
        }
    )

with open("database/export/data.json", "w") as f:
    json.dump(data_data, f, indent=2)

print(f"Exported {len(data_data)} data points")

# Export schedule
schedule = con.execute("SELECT * FROM schedule").fetchall()
schedule_data = []
for row in schedule:
    schedule_data.append(
        {"schedule_id": row[0], "day": str(row[1]), "dataset_id": row[2]}
    )

with open("database/export/schedule.json", "w") as f:
    json.dump(schedule_data, f, indent=2)

print(f"Exported {len(schedule_data)} schedule entries")

con.close()

print("\n✅ Export complete! Files created in database/export/")
print("Next step: Run import_to_neon.py to load data into Neon PostgreSQL")
