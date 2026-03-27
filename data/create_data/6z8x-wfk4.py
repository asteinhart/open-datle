"""
Data for NYC Evictions
Dataset Identifier: 6z8x-wfk4
Total Rows: 130k+
SOURCE: https://data.cityofnewyork.us/Housing-Development/Evictions/6z8x-wfk4/about_data
"""

import polars as pl

from data.utils.utils import (
	load_data,
	prepare_dataset_for_db,
	upload_dataset,
)


ID = "6z8x-wfk4"
LIMIT = 130000
SOURCE = "https://data.cityofnewyork.us/Housing-Development/Evictions/6z8x-wfk4/about_data"
data = load_data(ID, LIMIT)


def evictions_per_year(data) -> dict:

	data = data.with_columns(
		pl.col("executed_date")
		.str.to_datetime(strict=False)
		.dt.year()
		.alias("executed_year"),
		pl.col("executed_date")
		.str.to_datetime(strict=False)
		.dt.month()
		.alias("executed_month"),
	)

	full_years = (
		data.filter(
			pl.col("executed_year").is_not_null() & pl.col("executed_month").is_not_null()
		)
		.group_by("executed_year")
		.agg(pl.col("executed_month").n_unique().alias("month_count"))
		.filter(pl.col("month_count") == 12)
		.select("executed_year")
	)

	by_year = (
		data.filter(pl.col("executed_year").is_not_null())
		.join(full_years, on="executed_year", how="inner")
		.group_by("executed_year")
		.len()
		.sort("executed_year")
	)
	print(by_year)

	filename = prepare_dataset_for_db(
		dataset=by_year,
		dataset_x="executed_year",
		dataset_y="len",
		title="NYC Evictions per Year",
		type="line",
		city="New York City",
		y_min=0,
		source=SOURCE,
		subtitle="Number of executed evictions per year",
		note="",
	)

	return filename


if __name__ == "__main__":
	filename = evictions_per_year(data)
	upload_dataset(filename)
