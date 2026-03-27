"""
Data for NYPD Arrest Data (Historic)
Dataset Identifier: 8h9b-rp9u
Total Rows: ~6M+
SOURCE: https://data.cityofnewyork.us/Public-Safety/NYPD-Arrests-Data-Historic-/8h9b-rp9u/about_data
"""

import polars as pl

from data.utils.utils import (
	load_data,
	prepare_dataset_for_db,
	upload_dataset,
)


ID = "8h9b-rp9u"
LIMIT = 6000000
SOURCE = "https://data.cityofnewyork.us/Public-Safety/NYPD-Arrests-Data-Historic-/8h9b-rp9u/about_data"
data = load_data(ID, LIMIT)


def arrests_per_year(data) -> dict:

	data = data.with_columns(
		pl.col("arrest_date")
		.str.to_datetime(strict=False)
		.dt.year()
		.alias("arrest_year")
	)

	by_year = (
		data.filter(
			pl.col("arrest_year").is_not_null() & pl.col("arrest_key").is_not_null()
		)
		.group_by("arrest_year")
		.agg(pl.col("arrest_key").n_unique().alias("len"))
		.sort("arrest_year")
	)
	print(by_year)

	filename = prepare_dataset_for_db(
		dataset=by_year,
		dataset_x="arrest_year",
		dataset_y="len",
		title="NYPD Arrests per Year",
		type="line",
		city="New York City",
		y_min=0,
		source=SOURCE,
		subtitle="Number of NYPD arrests recorded each year from 2006 to 2025",
		note="Computed from arrest_date and unique arrest_key values.",
	)

	return filename


if __name__ == "__main__":
	filename = arrests_per_year(data)
	#upload_dataset(filename)
