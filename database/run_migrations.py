"""
Run database migrations for Neon PostgreSQL
Requires: pip install psycopg2-binary python-dotenv
"""

import os
import psycopg2
from dotenv import load_dotenv
import glob

# Load environment variables
load_dotenv("../app/.env")

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables")

def run_migration(file_path):
    """Run a single migration file"""
    print(f"Running migration: {os.path.basename(file_path)}")

    with open(file_path, 'r') as f:
        sql = f.read()

    # Connect and run migration
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    try:
        cur.execute(sql)
        conn.commit()
        print(f"✅ Migration completed: {os.path.basename(file_path)}")
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {os.path.basename(file_path)}")
        print(f"Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def main():
    print("🔄 Running database migrations...")

    # Find all migration files
    migration_files = sorted(glob.glob("migrations/*.sql"))

    if not migration_files:
        print("No migration files found in migrations/ directory")
        return

    print(f"Found {len(migration_files)} migration files")

    # Run each migration
    for migration_file in migration_files:
        run_migration(migration_file)

    print("\n✅ All migrations completed successfully!")

if __name__ == "__main__":
    main()