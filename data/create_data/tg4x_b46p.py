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
    upload_dataset,
)


ID = "tg4x-b46p"
LIMIT = 16000
SOURCE = "https://data.cityofnewyork.us/City-Government/Film-Permits/tg4x-b46p"
data = load_data(ID, LIMIT)


def permits_by_borough(data) -> dict:
    """
    permits by borough in 2025, eventTyoe = Shooting, based on EnteredOn date
    """

    data = data.filter(
        (pl.col("eventtype") == "Shooting Permit")
        & (
            pl.col("startdatetime").str.to_datetime("%Y-%m-%dT%H:%M:%S%.3f").dt.year()
            == 2025
        )
    )

    by_borough = data.group_by("borough").len()
    # order
    by_borough_sort = by_borough.sort("len", descending=True)

    # map boroughs
    by_borough_sort = by_borough_sort.with_columns(
        pl.col("borough").replace(BOROUGH_MAP).alias("borough")
    )

    # convert borough to int
    by_borough_sort = by_borough_sort.with_columns(pl.col("borough").cast(pl.Int64))
    print(by_borough_sort)

    file_name = prepare_dataset_for_db(
        dataset=by_borough_sort,
        dataset_x="borough",
        dataset_y="len",
        title="Film Permits by Borough",
        type="order",
        city="New York City",
        source=SOURCE,
        subtitle="Number of permits for filming in each NYC borough in 2025",
        note="",
    )

    return file_name


if __name__ == "__main__":
    file_name = permits_by_borough(data)
    upload_dataset(file_name)
