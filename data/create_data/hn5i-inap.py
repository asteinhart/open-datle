"""
Data for NYC Tree Points
Dataset Identifier: hn5i-inap
SOURCE: https://data.cityofnewyork.us/Environment/Street-Tree-Points/hn5i-inap/about_data
"""

import polars as pl

from data.utils.utils import load_data, prepare_dataset_for_db, upload_dataset


ID = "hn5i-inap"
SOURCE = "https://data.cityofnewyork.us/Environment/Street-Tree-Points/hn5i-inap/about_data"
data = load_data(ID)


def trees_planted_per_year(data) -> dict:

	date_col = "planteddate" if "planteddate" in data.columns else "createddate"

	if date_col not in data.columns:
		raise ValueError("Expected one of ['planteddate', 'createddate'] columns in dataset")

	by_year = (
		data.with_columns(
			pl.col(date_col)
			.str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S%.f", strict=False)
			.dt.year()
			.alias("year")
		)
		.filter(pl.col("year").is_not_null())
		.group_by("year")
		.len()
		.sort("year")
	)
	print(by_year)

	filename = prepare_dataset_for_db(
		dataset=by_year,
		dataset_x="year",
		dataset_y="len",
		title="Trees Planted per Year",
		type="line",
		city="New York City",
		y_min=0,
		source=SOURCE,
		subtitle="Number of tree point records per year in NYC",
	)

	return filename


if __name__ == "__main__":
	filename = trees_planted_per_year(data)
	upload_dataset(filename)
