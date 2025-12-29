import polars as pl

from data.utils.utils import (
    fetch_data_from_api,
    prepare_dataset_for_db,
    BOROUGH_MAP,
)


"""
Data for FDNY Firehouse Listing
Dataset Identifier: hc8x-tcnd
Total Rows: 219
Data Last Updated: 4/8/2022, 2:08:37 PM
Last Fetched: 2025-12-28
SOURCE: https://data.cityofnewyork.us/Public-Safety/FDNY-Firehouse-Listing/hc8x-tcnd/about_data
"""

ID = "hc8x-tcnd"
SOURCE = "https://data.cityofnewyork.us/Public-Safety/FDNY-Firehouse-Listing/hc8x-tcnd/about_data"
data = fetch_data_from_api("hc8x-tcnd", limit=219)


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
        title="FDNY Firehouses per Borough",
        type="order",
        city="New York City",
        source=SOURCE,
        subtitle="Number of firehouses in each NYC borough",
        note="Data as of April 2022",
        export_to_json=True,
        verbose=True,
    )

    return True


if __name__ == "__main__":
    firehouses_per_borough(data)
