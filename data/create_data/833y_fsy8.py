"""
Data for NYPD Shooting Incident
Dataset Identifier: 833y-fsy8
Total Rows: 29.7k
Data Last Updated: April 15, 2025
Last Fetched: 2025-12-29
SOURCE: https://data.cityofnewyork.us/Public-Safety/NYPD-Shooting-Incident-Data-Historic-/833y-fsy8/
"""

import polars as pl

from data.utils.utils import (
    load_data,
    prepare_dataset_for_db,
    upload_dataset,
)

ID = "833y-fsy8"
LIMIT = 30000
SOURCE = "https://data.cityofnewyork.us/Public-Safety/NYPD-Shooting-Incident-Data-Historic-/833y-fsy8/"
data = load_data(ID, LIMIT)


def shooting_incidents_per_year(data) -> dict:

    # convert occur_date to year
    data = data.with_columns(
        pl.col("occur_date").str.to_datetime().dt.year().alias("occur_year")
    )

    by_year = (data.group_by("occur_year").len()).sort("occur_year")

    filename = prepare_dataset_for_db(
        dataset=by_year,
        dataset_x="occur_year",
        dataset_y="len",
        title="NYPD Shooting Incidents per Year",
        type="line",
        city="New York City",
        y_min=0,
        y_max=2200,
        source=SOURCE,
        subtitle="Number of shooting incidents reported by NYPD each year",
        note="Data as of April 2025. Includes nonlethal and fatal shootings.",
    )

    return filename


if __name__ == "__main__":
    filename = shooting_incidents_per_year(data)
    upload_dataset(filename)
