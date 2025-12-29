"""
Data for FDNY Firehouse Listing
Dataset Identifier: hc8x-tcnd
Total Rows: 219
Data Last Updated: 4/8/2022, 2:08:37 PM
Last Fetched: 2025-12-28
SOURCE: https://data.cityofnewyork.us/Public-Safety/FDNY-Firehouse-Listing/hc8x-tcnd/about_data
"""

import polars as pl

from data.utils.utils import (
    load_data,
    prepare_dataset_for_db,
    upload_dataset,
    BOROUGH_MAP,
)


ID = "hc8x-tcnd"
LIMIT = 219
SOURCE = "https://data.cityofnewyork.us/Public-Safety/FDNY-Firehouse-Listing/hc8x-tcnd"
data = load_data(ID, LIMIT)


def firehouses_per_borough(data) -> dict:
    """
    Count firehouses per borough.

    Parameters:
    - data: Polars DataFrame containing firehouse data.

    Returns:
    - Dictionary with boroughs as keys and counts as values.
    """
    by_borough = data.group_by("borough").len()
    # order
    by_borough_sort = by_borough.sort("len", descending=True)

    # map boroughs
    by_borough_sort = by_borough_sort.with_columns(
        pl.col("borough").replace(BOROUGH_MAP).alias("borough")
    )

    # convert borough to int
    by_borough_sort = by_borough_sort.with_columns(pl.col("borough").cast(pl.Int64))

    prepare_dataset_for_db(
        dataset=by_borough_sort,
        dataset_x="borough",
        dataset_y="len",
        title="FDNY Firehouses per Borough",
        type="order",
        city="New York City",
        source=SOURCE,
        subtitle="Number of firehouses in each NYC borough",
        note="Data as of April 2022",
    )

    return True


if __name__ == "__main__":
    file_name = firehouses_per_borough(data)
    upload_dataset(file_name)
