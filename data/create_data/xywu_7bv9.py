"""
Data for New York City Population by Borough, 1950 - 2040
Dataset Identifier: xywu-7bv9
Total Rows: 6
Data Last Updated: April 29, 2014
Last Fetched: 2025-12-29
SOURCE: https://data.cityofnewyork.us/City-Government/New-York-City-Population-by-Borough-1950-2040/xywu-7bv9/about_data
"""

import polars as pl

from data.utils.utils import load_data, prepare_dataset_for_db, upload_dataset

ID = "xywu-7bv9"
LIMIT = 6
SOURCE = "https://data.cityofnewyork.us/City-Government/New-York-City-Population-by-Borough-1950-2040/xywu-7bv9/about_data"
data = load_data(ID, LIMIT)


def population_per_year(data) -> dict:

    COLUMNS = [
        "_1950",
        "_1960",
        "_1970",
        "_1980",
        "_1990",
        "_2000",
        "_2010",
        "_2020",
        "_2030",
        "_2040",
    ]

    # convert year to int
    data_long = (
        data.filter(pl.col("borough") == "NYC Total")
        .select(COLUMNS)
        .unpivot()
        .with_columns(
            pl.col("variable").str.replace_all("_", "").cast(pl.Int64).alias("year"),
            pl.col("value").cast(pl.Int64).alias("population"),
        )
        .select(["year", "population"])
    )

    filename = prepare_dataset_for_db(
        dataset=data_long,
        dataset_x="year",
        dataset_y="population",
        title="New York City Population by Year",
        type="line",
        city="New York City",
        y_min=6000000,
        y_max=10000000,
        source=SOURCE,
        subtitle="Total population of New York City from 1950 to projected 2040",
        note="Data as of April 2014.",
    )

    return filename


if __name__ == "__main__":
    filename = population_per_year(data)
    upload_dataset(filename)
