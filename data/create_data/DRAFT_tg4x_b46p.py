"""
Data for Film Permits
Dataset Identifier: tg4x-b46p
Total Rows: 15.1k
Data Last Updated: December 28, 2025
Last Fetched: 2025-12-28
SOURCE: https://data.cityofnewyork.us/City-Government/Film-Permits/tg4x-b46p
"""

import polars as pl

from data.utils.utils import (
    load_data,
    prepare_dataset_for_db,
    BOROUGH_MAP,
)


ID = "tg4x-b46p"
LIMIT = 16000
SOURCE = "https://data.cityofnewyork.us/City-Government/Film-Permits/tg4x-b46p"
data = load_data(ID, LIMIT)


def permits_per_year(data) -> dict:

    # create year column from permit_start_date
    data = data.with_columns(
        pl.col("startdatetime")
        .str.to_datetime()
        .dt.month_start()
        .dt.date()
        .alias("month_start_first"),
        pl.col("enddatetime")
        .str.to_datetime()
        .dt.month_start()
        .dt.date()
        .alias("month_end_first"),
    )

    # concat year_start and year_end into a single year column
    data = data.with_columns(
        pl.coalesce(["month_start_first", "month_end_first"]).alias("month_first")
    )

    # remove nulls
    data = data.filter(pl.col("month_first").is_not_null())

    by_month = (data.group_by("month_first").len()).sort("month_first")

    by_month.plot.bar(x="month_first", y="len").show()


if __name__ == "__main__":
    permits_per_year(data)
