import polars as pl
from sodapy import Socrata
import os
import json


from data.utils.env import APP_TOKEN, PASSWORD

# Borough mapping for NYC order-type datasets
BOROUGH_MAP = {
    "Manhattan": 1,
    "Brooklyn": 2,
    "Queens": 3,
    "The Bronx": 4,
    "Bronx": 4,
    "Staten Island": 5,
}


def set_client() -> Socrata:
    """
    Set up and return a Socrata client for accessing the API.

    Returns:
    - An instance of sodapy.Socrata.
    """
    client = Socrata(
        "data.cityofnewyork.us",
        APP_TOKEN,
        username="asteinhart3@gmail.com",
        password=PASSWORD,
    )

    return client


def fetch_data_from_api(dataset_identifier: str, limit: int = 1000) -> pl.DataFrame:
    """
    Fetch data from a Socrata API and return it as a Polars DataFrame.

    Parameters:
    - client: An instance of sodapy.Socrata to interact with the API.
    - dataset_identifier: The identifier of the dataset to fetch.
    - limit: The maximum number of records to fetch.

    Returns:
    - A Polars DataFrame containing the fetched data.
    """
    client = set_client()

    results = client.get(dataset_identifier, limit=limit)
    df = pl.DataFrame(results)
    return df


def verify_line(dataset: dict) -> bool:
    """
    Verify if the dataset conforms to the "line" format.

    Expected format:
    {
        "title": str,
        "type": "line",
        "city": str,
        "subtitle": str (optional),
        "y_min": float (optional),
        "y_max": float (optional),
        "source": str (optional),
        "data": [
            {"x": float, "y": float, "sort_order": int},
            ...
        ]
    }

    Parameters:
    - dataset: The dataset to verify.

    Returns:
    - True if the dataset is in "line" format, False otherwise.
    """


def verify_dataset(
    dataset: dict,
) -> bool:
    """
    Verify if the dataset type is valid and conforms to the expected format.

    Parameters:
    - dataset: The dataset dictionary to verify.
    - type: The type of dataset to verify. Must be either "line" or "order".

    Returns:
    - True if the dataset type is valid and format is correct, False otherwise.
    """

    try:
        # Check required top-level fields
        if not isinstance(dataset, dict):
            print("Dataset must be a dictionary")
            return False

        if "title" not in dataset or not isinstance(dataset["title"], str):
            print("Missing or invalid 'title' field")
            return False

        if dataset.get("type") not in ["line", "order"]:
            print("Type must be 'line' or 'order'")
            return False

        if "city" not in dataset or not isinstance(dataset["city"], str):
            print("Missing or invalid 'city' field")
            return False

        if "data" not in dataset or not isinstance(dataset["data"], list):
            print("Missing or invalid 'data' field")
            return False

        if len(dataset["data"]) == 0:
            print("Data array cannot be empty")
            return False

        # Check optional fields if present
        if "subtitle" in dataset and dataset["subtitle"] is not None:
            if not isinstance(dataset["subtitle"], str):
                print("'subtitle' must be a string or None")
                return False

        if "y_min" in dataset and dataset["y_min"] is not None:
            if not isinstance(dataset["y_min"], (int, float)):
                print("'y_min' must be a number or None")
                return False

        if "y_max" in dataset and dataset["y_max"] is not None:
            if not isinstance(dataset["y_max"], (int, float)):
                print("'y_max' must be a number or None")
                return False

        if "source" in dataset and dataset["source"] is not None:
            if not isinstance(dataset["source"], str):
                print("'source' must be a string or None")
                return False

        # Check data array format
        for i, point in enumerate(dataset["data"]):
            if not isinstance(point, dict):
                print(f"Data point {i} must be a dictionary")
                return False

            if "x" not in point or not isinstance(point["x"], (int, float)):
                print(f"Data point {i} missing or invalid 'x' field (must be number)")
                return False

            if "y" not in point or not isinstance(point["y"], (int, float)):
                print(f"Data point {i} missing or invalid 'y' field (must be number)")
                return False

            if "sort_order" not in point or not isinstance(point["sort_order"], int):
                print(
                    f"Data point {i} missing or invalid 'sort_order' field (must be integer)"
                )
                return False

        # Check sort_order uniqueness and sequence
        sort_orders = [point["sort_order"] for point in dataset["data"]]
        if len(sort_orders) != len(set(sort_orders)):
            print("sort_order values must be unique")
            return False

        return True

    except Exception as e:
        print(f"Validation error: {e}")
        return False


def prepare_dataset_for_db(
    dataset: dict,
    title: str,
    type: str,
    city: str,
    source: str,
    subtitle: str = None,
    y_min: float = None,
    y_max: float = None,
    note: str = None,
    export_to_json: bool = False,
    verbose: bool = False,
) -> bool:
    """
    Prepare dataset for database insertion.

    Parameters:
    - dataset: The dataset dictionary to prepare.

    Returns:
    - A tuple containing metadata and data points ready for DB insertion.
    """
    staging = {
        "title": title,
        "type": type,
        "city": city,
        "subtitle": subtitle,
        "y_min": y_min,
        "y_max": y_max,
        "source": source,
        "note": note,
        "data": [
            {"x": row["borough"], "y": row["len"], "sort_order": idx + 1}
            for idx, row in enumerate(dataset.iter_rows(named=True))
        ],
    }
    if verbose:
        print(
            f"Prepared dataset: {staging['title']} with {len(staging['data'])} points"
        )

    if not verify_dataset(staging):
        raise ValueError("Prepared data does not conform to expected format.")

    if verbose:
        print("Dataset verification passed.")

    if export_to_json:
        try:
            if not os.path.exists("prepared_data"):
                os.makedirs("prepared_data")

            file_name = (
                f"prepared_data/{staging['title'].replace(' ', '_').lower()}.json"
            )

            with open(file_name, "w") as f:
                json.dump(staging, f)

            if verbose:
                print(f"Exported prepared dataset to {file_name}")
        except Exception as e:
            print(f"Error exporting to JSON: {e}")

    return True
