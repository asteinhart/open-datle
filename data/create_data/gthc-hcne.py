import geopandas as gpd
import polars as pl
from data.utils.utils import (
    prepare_dataset_for_db,
    upload_dataset,
    BOROUGH_MAP,
)


def create_land_area_dataset():
    """
    Create a dataset of land area of NYC boroughs.

    This function loads the borough boundaries dataset, calculates the land area of each borough in square miles, maps the borough names to integers, and prepares the dataset for upload to the database.
    """
    # Load the datasets
    boundaries = gpd.read_file("data/ref/Borough_Boundaries_20260215.geojson")

    # Calculate land area of each borough from square feet to  square miles
    boundaries["land_area_sq_mi"] = (
        boundaries["geometry"].to_crs({"init": "epsg:3857"}).area / 2.59e6
    )
    # round, no decimals
    boundaries["land_area_sq_mi"] = boundaries["land_area_sq_mi"].round()

    # Map borough names to integers
    boundaries["borough"] = boundaries["boroname"].replace(BOROUGH_MAP).astype(int)

    # Keep only borough and land area columns and convert to polars dataframe
    boundaries = boundaries[["borough", "land_area_sq_mi"]]
    boundaries = pl.from_pandas(boundaries)

    boundaries = boundaries.sort("land_area_sq_mi", descending=True)

    # prepare dataset for database
    filename = prepare_dataset_for_db(
        dataset=boundaries,
        dataset_x="borough",
        dataset_y="land_area_sq_mi",
        title="Land Area of NYC Boroughs",
        type="order",
        city="New York City",
        source="https://data.cityofnewyork.us/City-Government/Borough-Boundaries/gthc-hcne/about_data",
        subtitle="Land area of each NYC borough in square miles",
    )

    return filename


if __name__ == "__main__":
    file_name = create_land_area_dataset()
    upload_dataset(file_name)
