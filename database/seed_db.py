import duckdb

# Connect to the database
con = duckdb.connect("db/open_datle.db")

# Insert sample users
users = [("test@example.com",), ("user2@example.com",), ("user3@example.com",)]

for email in users:
    con.execute(
        """
        INSERT INTO users (user_id, email)
        VALUES (nextval('seq_user_id'), ?)
    """,
        email,
    )

# Insert sample datasets metadata
datasets_meta = [
    (
        "NYC Temperature Over Time",  # title
        "line",  # type
        "New York City",  # city
        "Degrees in Fahrenheit",  # subtitle (nullable)
        None,  # y_min (nullable)
        None,  # y_max (nullable)
        "https://data.cityofnewyork.us/example",  # source
        None,  # note (nullable)
    ),
    (
        "Borough Population Ranking",  # title
        "order",  # type
        "New York City",  # city
        None,  # subtitle (nullable)
        None,  # y_min (nullable)
        None,  # y_max (nullable)
        "https://data.cityofnewyork.us/example2",  # source
        "Rank by population density",  # note (nullable)
    ),
]

for dataset in datasets_meta:
    con.execute(
        """
        INSERT INTO datasets_meta (dataset_id, title, type, city, subtitle, y_min, y_max, source, note)
        VALUES (nextval('seq_dataset_id'), ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        dataset,
    )

# Insert sample data points for dataset 1 (NYC Temperature)
data_points_1 = [
    (1, 2015, 52.3, 1),
    (1, 2016, 53.1, 2),
    (1, 2017, 54.7, 3),
    (1, 2018, 53.9, 4),
    (1, 2019, 55.2, 5),
    (1, 2020, 54.8, 6),
    (1, 2021, 56.4, 7),
    (1, 2022, 57.1, 8),
    (1, 2023, 58.3, 9),
]

for dataset_id, x, y, sort_order in data_points_1:
    con.execute(
        """
        INSERT INTO data (data_id, dataset_id, x, y, sort_order)
        VALUES (nextval('seq_data_id'), ?, ?, ?, ?)
    """,
        (dataset_id, x, y, sort_order),
    )

# Insert sample data points for dataset 2 (Borough Ranking)
# Note: x should be the borough name, but data.x is DOUBLE type
# Using numeric IDs for now (1=Manhattan, 2=Brooklyn, 3=Queens, 4=Bronx, 5=Staten Island)
data_points_2 = [
    (2, 1, 599, 1),  # Manhattan - highest
    (2, 2, 263, 2),  # Brooklyn
    (2, 3, 227, 3),  # Queens
    (2, 4, 141, 4),  # The Bronx
    (2, 5, 47, 5),  # Staten Island - lowest
]

for dataset_id, x, y, sort_order in data_points_2:
    con.execute(
        """
        INSERT INTO data (data_id, dataset_id, x, y, sort_order)
        VALUES (nextval('seq_data_id'), ?, ?, ?, ?)
    """,
        (dataset_id, x, y, sort_order),
    )

# Insert sample schedule
schedules = [("2025-12-20", 1), ("2025-12-21", 2)]

for day, dataset_id in schedules:
    con.execute(
        """
        INSERT INTO schedule (schedule_id, day, dataset_id)
        VALUES (nextval('seq_schedule_id'), ?, ?)
    """,
        (day, dataset_id),
    )

print("Sample data inserted successfully!")

# Show some data
print("\n=== Users ===")
print(con.execute("SELECT * FROM users").fetchall())

print("\n=== Datasets Metadata ===")
print(con.execute("SELECT dataset_id, title, type FROM datasets_meta").fetchall())

print("\n=== Data Points (Dataset 1) ===")
print(
    con.execute(
        "SELECT * FROM data WHERE dataset_id = 1 ORDER BY sort_order"
    ).fetchall()
)

print("\n=== Schedule ===")
print(con.execute("SELECT * FROM schedule").fetchall())

con.close()
