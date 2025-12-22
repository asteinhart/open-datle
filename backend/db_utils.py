"""
Database utility functions for DuckDB
"""

import duckdb
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

DB_PATH = "open_datle.db"


def get_connection():
    """Get a database connection"""
    return duckdb.connect(DB_PATH)


def find_dataset_by_date(date_str: str) -> Optional[Dict[str, Any]]:
    """
    Find dataset ID by date (YYYYMMDD format)

    Args:
        date_str: Date in YYYYMMDD format

    Returns:
        Dict with date and dataset_id, or None if not found
    """
    # Convert YYYYMMDD to YYYY-MM-DD
    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

    con = get_connection()
    result = con.execute(
        """
        SELECT day, dataset_id 
        FROM schedule 
        WHERE day = ?
    """,
        [formatted_date],
    ).fetchone()
    con.close()

    if result:
        # Convert date back to YYYYMMDD
        day_str = result[0].strftime("%Y%m%d")
        return {"date": day_str, "dataset_id": result[1]}
    return None


def get_dataset(dataset_id: int) -> Optional[Dict[str, Any]]:
    """
    Get dataset by ID

    Args:
        dataset_id: Dataset ID

    Returns:
        Dict with dataset details, or None if not found
    """
    con = get_connection()
    result = con.execute(
        """
        SELECT dataset_id, title, x_axis_label, y_axis_label, data_id, type, source
        FROM dataset
        WHERE dataset_id = ?
    """,
        [dataset_id],
    ).fetchone()
    con.close()

    if result:
        return {
            "dataset_id": result[0],
            "title": result[1],
            "x_axis_label": result[2],
            "y_axis_label": result[3],
            "data": json.loads(result[4]),
            "type": result[5],
            "source": result[6],
        }
    return None


def save_user_guess_line(user_id: int, dataset_id: int, user_line: List[Dict]) -> bool:
    """
    Save or update user's line guess

    Args:
        user_id: User ID
        dataset_id: Dataset ID
        user_line: List of points

    Returns:
        True if successful, False otherwise
    """
    try:
        con = get_connection()

        # Check if entry exists
        existing = con.execute(
            """
            SELECT id FROM user_data_line
            WHERE user_id = ? AND dataset_id = ?
        """,
            [user_id, dataset_id],
        ).fetchone()

        if existing:
            # Update existing
            con.execute(
                """
                UPDATE user_data_line
                SET user_line = ?, submitted_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND dataset_id = ?
            """,
                [json.dumps(user_line), user_id, dataset_id],
            )
        else:
            # Insert new
            con.execute(
                """
                INSERT INTO user_data_line (id, user_id, dataset_id, user_line)
                VALUES (nextval('seq_user_data_line_id'), ?, ?, ?)
            """,
                [user_id, dataset_id, json.dumps(user_line)],
            )

        con.close()
        return True
    except Exception as e:
        print(f"Error saving user guess: {e}")
        return False


def get_user_guess(user_id: int, dataset_id: int) -> Optional[Dict[str, Any]]:
    """
    Get user's guess for a dataset

    Args:
        user_id: User ID
        dataset_id: Dataset ID

    Returns:
        Dict with user_line and submitted_at, or None if not found
    """
    con = get_connection()
    result = con.execute(
        """
        SELECT user_line, submitted_at
        FROM user_data_line
        WHERE user_id = ? AND dataset_id = ?
    """,
        [user_id, dataset_id],
    ).fetchone()
    con.close()

    if result:
        return {"user_line": json.loads(result[0]), "submitted_at": result[1]}
    return None


def create_user(email: str) -> Optional[int]:
    """
    Create a new user

    Args:
        email: User email

    Returns:
        User ID if successful, None otherwise
    """
    try:
        con = get_connection()
        con.execute(
            """
            INSERT INTO users (user_id, email)
            VALUES (nextval('seq_user_id'), ?)
        """,
            [email],
        )

        result = con.execute("SELECT currval('seq_user_id')").fetchone()
        con.close()
        return result[0] if result else None
    except Exception as e:
        print(f"Error creating user: {e}")
        return None


if __name__ == "__main__":
    # Test the functions
    print("Testing database functions...")

    # Test find_dataset_by_date
    result = find_dataset_by_date("20240101")
    print(f"\nFind dataset by date: {result}")

    # Test get_dataset
    if result:
        dataset = get_dataset(result["dataset_id"])
        print(f"\nGet dataset: {dataset}")
