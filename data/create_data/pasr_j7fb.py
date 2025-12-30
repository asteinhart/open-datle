"""
Data for Emergency Response Incidents
Dataset Identifier: pasr-j7fb
Total Rows: 12k
Data Last Updated: June 23, 2025
Last Fetched: 2025-12-29
SOURCE: https://data.cityofnewyork.us/Public-Safety/Emergency-Response-Incidents/pasr-j7fb/about_data
"""

import polars as pl

from data.utils.utils import load_data, prepare_dataset_for_db, upload_dataset

ID = "pasr-j7fb"
LIMIT = 12000
SOURCE = "https://data.cityofnewyork.us/Public-Safety/Emergency-Response-Incidents/pasr-j7fb/about_data"
data = load_data(ID, LIMIT)


def emergency_responses_per_year(data) -> dict:

    # are any creation date null?
    assert data.filter(pl.col("creation_date").is_null()).height == 0

    # convert occur_date to year
    data = data.with_columns(
        pl.col("creation_date").str.to_datetime().dt.year().alias("year")
    )

    by_year = (
        data.filter(
            ~pl.col("year").is_in(
                [2011, 2022]
            )  # remove 2011 and 2022 since not full years
        )
        .group_by("year")
        .len()
        .sort("year")
    )

    filename = prepare_dataset_for_db(
        dataset=by_year,
        dataset_x="year",
        dataset_y="len",
        title="Emergency Response Incidents per Year",
        type="line",
        city="New York City",
        y_min=0,
        y_max=1500,
        source=SOURCE,
        subtitle="Number of emergency response incidents reported each year, 2012 to 2021",
        note="Only included full years provided by the city.",
    )

    return filename


if __name__ == "__main__":
    filename = emergency_responses_per_year(data)
    upload_dataset(filename)
