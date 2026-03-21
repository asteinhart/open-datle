import duckdb
import os

# Ensure the directory for the database exists
os.makedirs("database", exist_ok=True)

# Create or connect to DuckDB database
con = duckdb.connect("database/open_datle.db")

# Create tables
con.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        cookie VARCHAR UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""
)

con.execute(
    """
    CREATE SEQUENCE IF NOT EXISTS seq_user_id START 1
"""
)

con.execute(
    """
    CREATE TABLE IF NOT EXISTS datasets_meta (
        dataset_id INTEGER PRIMARY KEY,
        title VARCHAR NOT NULL,
        type VARCHAR NOT NULL CHECK (type IN ('line', 'order')),
        city VARCHAR NOT NULL,
        subtitle VARCHAR,
        y_min DOUBLE,
        y_max DOUBLE,
        source VARCHAR,
        note VARCHAR,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""
)

# creating data# After datasets_meta table
con.execute(
    """
    CREATE TABLE IF NOT EXISTS data (
        data_id INTEGER PRIMARY KEY,
        dataset_id INTEGER,
        x DOUBLE NOT NULL,
        y DOUBLE NOT NULL,
        sort_order INTEGER NOT NULL,
        FOREIGN KEY (dataset_id) REFERENCES datasets_meta(dataset_id) ON DELETE RESTRICT
    )
"""
)

con.execute("CREATE SEQUENCE IF NOT EXISTS seq_data_id START 1")
con.execute(
    "CREATE INDEX IF NOT EXISTS idx_data_dataset ON data(dataset_id, sort_order)"
)

con.execute(
    """
    CREATE SEQUENCE IF NOT EXISTS seq_dataset_id START 1
"""
)

con.execute(
    """
    CREATE TABLE IF NOT EXISTS schedule (
        schedule_id INTEGER PRIMARY KEY,
        day DATE UNIQUE NOT NULL,
        dataset_id INTEGER NOT NULL,
        FOREIGN KEY (dataset_id) REFERENCES datasets_meta(dataset_id)
    )
"""
)

con.execute(
    """
    CREATE SEQUENCE IF NOT EXISTS seq_schedule_id START 1
"""
)


# Create indexes
con.execute("CREATE INDEX IF NOT EXISTS idx_schedule_day ON schedule(day)")


print("Database and tables created successfully!")

con.close()


# # user line in part 2
# con.execute(
#     """
#     CREATE TABLE IF NOT EXISTS user_data_line (
#         id INTEGER PRIMARY KEY,
#         user_id INTEGER NOT NULL,
#         dataset_id INTEGER NOT NULL,
#         user_line JSON NOT NULL,
#         submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#         FOREIGN KEY (user_id) REFERENCES users(user_id),
#         FOREIGN KEY (dataset_id) REFERENCES dataset(dataset_id),
#         UNIQUE (user_id, dataset_id)
#     )
# """
# )

# con.execute(
#     """
#     CREATE SEQUENCE IF NOT EXISTS seq_user_data_line_id START 1
# """
# )


# #index


# con.execute(
#     "CREATE INDEX IF NOT EXISTS idx_user_data_line_user ON user_data_line(user_id)"
# )


# con.execute(
#     "CREATE INDEX IF NOT EXISTS idx_user_data_line_dataset ON user_data_line(dataset_id)"
# )
