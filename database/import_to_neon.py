"""
Import data from JSON files to Neon PostgreSQL
Requires: pip install psycopg2-binary python-dotenv
"""

import json
import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../app/.env")

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables")

print(f"Connecting to Neon PostgreSQL...")

# Connect to Neon
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print("✅ Connected to Neon PostgreSQL\n")

# Import users
print("Importing users...")
with open("database/export/users.json", "r") as f:
    users = json.load(f)

if users:
    for user in users:
        cur.execute(
            """
            INSERT INTO users (user_id, cookie, created_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (cookie) DO NOTHING
            """,
            (
                user["user_id"],
                user.get("cookie", user.get("email", "anonymous")),
                user["created_at"],
            ),
        )

    # Update sequence to prevent conflicts
    cur.execute("SELECT setval('users_user_id_seq', (SELECT MAX(user_id) FROM users))")

print(f"✅ Imported {len(users)} users")

# Import datasets_meta
print("Importing datasets...")
with open("database/export/datasets_meta.json", "r") as f:
    datasets = json.load(f)

if datasets:
    for dataset in datasets:
        cur.execute(
            """
            INSERT INTO datasets_meta (dataset_id, title, type, city, subtitle, y_min, y_max, source, note, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (dataset_id) DO NOTHING
            """,
            (
                dataset["dataset_id"],
                dataset["title"],
                dataset["type"],
                dataset["city"],
                dataset["subtitle"],
                dataset["y_min"],
                dataset["y_max"],
                dataset["source"],
                dataset["note"],
                dataset["created_at"],
            ),
        )

    # Update sequence
    cur.execute(
        "SELECT setval('datasets_meta_dataset_id_seq', (SELECT MAX(dataset_id) FROM datasets_meta))"
    )

print(f"✅ Imported {len(datasets)} datasets")

# Import data points
print("Importing data points...")
with open("database/export/data.json", "r") as f:
    data_points = json.load(f)

if data_points:
    # Batch insert for better performance
    values = [
        (
            point["data_id"],
            point["dataset_id"],
            point["x"],
            point["y"],
            point["sort_order"],
        )
        for point in data_points
    ]

    execute_values(
        cur,
        """
        INSERT INTO data (data_id, dataset_id, x, y, sort_order)
        VALUES %s
        ON CONFLICT (data_id) DO NOTHING
        """,
        values,
    )

    # Update sequence
    cur.execute("SELECT setval('data_data_id_seq', (SELECT MAX(data_id) FROM data))")

print(f"✅ Imported {len(data_points)} data points")

# Import schedule
print("Importing schedule...")
with open("database/export/schedule.json", "r") as f:
    schedule = json.load(f)

if schedule:
    for entry in schedule:
        cur.execute(
            """
            INSERT INTO schedule (schedule_id, day, dataset_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (day) DO NOTHING
            """,
            (entry["schedule_id"], entry["day"], entry["dataset_id"]),
        )

    # Update sequence
    cur.execute(
        "SELECT setval('schedule_schedule_id_seq', (SELECT MAX(schedule_id) FROM schedule))"
    )

print(f"✅ Imported {len(schedule)} schedule entries")

# Commit all changes
conn.commit()

# Verify import
cur.execute("SELECT COUNT(*) FROM users")
user_count = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM datasets_meta")
dataset_count = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM data")
data_count = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM schedule")
schedule_count = cur.fetchone()[0]

print(f"\n📊 Import verification:")
print(f"  - Users: {user_count}")
print(f"  - Datasets: {dataset_count}")
print(f"  - Data points: {data_count}")
print(f"  - Schedule entries: {schedule_count}")

# Close connection
cur.close()
conn.close()

print("\n✅ Migration complete!")
print("Next step: Update API endpoints to use Neon PostgreSQL")
