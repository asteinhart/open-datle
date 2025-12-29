"""
Data for Air Quality
Dataset Identifier: c3uy-2p5r
Total Rows: 18.9k
Data Last Updated:
Last Fetched: 2025-12-29
SOURCE: https://data.cityofnewyork.us/Environment/Air-Quality/c3uy-2p5r/
"""

import polars as pl

from data.utils.utils import load_data, prepare_dataset_for_db, upload_dataset

ID = "c3uy-2p5r"
LIMIT = 18900
SOURCE = "https://data.cityofnewyork.us/Environment/Air-Quality/c3uy-2p5r/"
data = load_data(ID, LIMIT)


def air_quality_per_year(data) -> dict:
    """
    Analyze air quality trends over time.

    Parameters:
    - data: Polars DataFrame containing air quality data.

    Returns:
    - Dictionary with analysis results.
    """

    # filter to just yearly avg pm25 by borough, convert data_value to float, and aggregate
    averages_pm25_mean = (
        data.filter(
            (pl.col("indicator_id") == "365")
            & (pl.col("time_period").str.starts_with("Annual"))
        )
        .with_columns(pl.col("data_value").cast(pl.Float64))
        .group_by("time_period")
        .agg(pl.col("data_value").mean().alias("avg_pm25"))
        .with_columns(pl.col("time_period").str.slice(-4).cast(pl.Int64).alias("year"))
        .sort("year")
    )

    filename = prepare_dataset_for_db(
        dataset=averages_pm25_mean,
        dataset_x="year",
        dataset_y="avg_pm25",
        title="Average Air Quality in NYC",
        type="line",
        city="New York City",
        y_min=0,
        y_max=15,
        source=SOURCE,
        subtitle="Average annual PM2.5 levels in New York City from air quality monitoring stations",
        note=None,
    )

    return True


if __name__ == "__main__":
    filename = air_quality_per_year(data)
    upload_dataset(filename)
