import polars as pl
from sodapy import Socrata
import os
import json
import requests
from pathlib import Path


from data.utils.env import APP_TOKEN, PASSWORD

PREPARED_DATA_DIR = Path("./data/prepared_data")

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


def load_data(
    dataset_identifier: str, limit: int = 1000, save_local: bool = True
) -> pl.DataFrame:
    """
    Load data from a local parquet file if it exists, otherwise fetch from API.

    Parameters:
    - dataset_identifier: The identifier of the dataset to load.
    - limit: The maximum number of records to fetch if loading from API.

    Returns:
    - A Polars DataFrame containing the loaded data.
    """
    file_path = f"data/temp_data/{dataset_identifier}.parquet"

    if os.path.exists(file_path):
        data = pl.read_parquet(file_path)
    else:
        data = fetch_data_from_api(dataset_identifier, limit=limit)
        if save_local:
            data.write_parquet(file_path)

    return data


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
    dataset_x: str,
    dataset_y: str,
    title: str,
    type: str,
    city: str,
    source: str,
    subtitle: str = None,
    y_min: float = None,
    y_max: float = None,
    note: str = None,
    export_to_json: bool = True,
    verbose: bool = True,
) -> str:
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
            {"x": row[dataset_x], "y": row[dataset_y], "sort_order": idx + 1}
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
            if not os.path.exists("data/prepared_data"):
                os.makedirs("data/prepared_data")

            json_name = f"{staging['title'].replace(' ', '_').lower()}.json"
            file_name = f"data/prepared_data/{json_name}"

            with open(file_name, "w") as f:
                json.dump(staging, f)

            if verbose:
                print(f"Exported prepared dataset to {file_name}")
        except Exception as e:
            print(f"Error exporting to JSON: {e}")

    return json_name


def upload_dataset(
    filename: str, api_url: str = "http://localhost:5173/api/v1/dataset"
) -> bool:
    """
    Upload a prepared dataset JSON file to the API

    Parameters:
    - filename: Name of the JSON file in data/prepared_data/ directory
    - api_url: API endpoint URL (default: http://localhost:5173/api/v1/dataset)

    Returns:
    - True if upload successful, False otherwise
    """

    try:
        # Construct file path
        file_path = PREPARED_DATA_DIR / filename

        # Check if file exists
        if not file_path.exists():
            print(f"❌ Error: File not found: {file_path}")
            print(f"\nAvailable files in {PREPARED_DATA_DIR}:")

            if PREPARED_DATA_DIR.exists():
                files = [f.name for f in PREPARED_DATA_DIR.glob("*.json")]
                for f in files:
                    print(f"  - {f}")
            return False

        # Read and parse JSON file
        print(f"📂 Reading file: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            dataset = json.load(f)

        # Validate required fields
        if not all(key in dataset for key in ["title", "type", "city", "data"]):
            print("❌ Error: Dataset missing required fields (title, type, city, data)")
            return False

        print(f"📊 Dataset: {dataset['title']}")
        print(f"   Type: {dataset['type']}")
        print(f"   City: {dataset['city']}")
        print(f"   Data points: {len(dataset['data'])}")

        # Upload to API
        print(f"\n🚀 Uploading to {api_url}...")

        response = requests.post(
            api_url,
            headers={"Content-Type": "application/json"},
            json=dataset,
        )

        result = response.json()

        if response.ok:
            print(f"✅ Success! Dataset created with ID: {result['dataset_id']}")
            if "message" in result:
                print(f"   Message: {result['message']}")
            print(f"\n🔗 View at: {api_url}?id={result['dataset_id']}")
            return True
        else:
            print(f"❌ Error: {response.status_code} {response.reason}")
            print(f"   {result.get('error', json.dumps(result))}")
            return False

    except Exception as error:
        print(f"❌ Error: {error}")
        return False


def delete_dataset(
    dataset_id: int, api_url: str = "http://localhost:5173/api/v1/dataset"
) -> bool:
    """
    Delete a dataset from the API

    Parameters:
    - dataset_id: ID of the dataset to delete
    - api_url: API endpoint URL (default: http://localhost:5173/api/v1/dataset)

    Returns:
    - True if deletion successful, False otherwise
    """

    try:
        print(f"\nDeleting dataset with ID: {dataset_id}...")

        response = requests.delete(
            f"{api_url}?id={dataset_id}",
            headers={"Content-Type": "application/json"},
        )

        result = response.json()

        if response.ok:
            print("✅ Dataset deleted successfully")
            print(f"Dataset ID: {result['dataset_id']}")
            return True
        else:
            print("❌ Failed to delete dataset")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False

    except Exception as error:
        print(f"❌ Error deleting dataset: {error}")
        return False


## option to just run upload or delete from here
if __name__ == "__main__":
    # Example usage:
    # upload_dataset("example_dataset.json")
    # delete_dataset(3)
    pass
