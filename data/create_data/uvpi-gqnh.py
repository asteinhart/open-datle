"""
Data for NYC Street Tree Census
Dataset Identifier: uvpi-gqnh
Total Rows: 700k+
SOURCE: https://data.cityofnewyork.us/Environment/2015-Street-Tree-Census-Tree-Data/uvpi-gqnh/about_data
"""

import polars as pl

from data.utils.utils import (
	BOROUGH_MAP,
	load_data,
	prepare_dataset_for_db,
	upload_dataset,
)


ID = "uvpi-gqnh"
LIMIT = 700000
SOURCE = "https://data.cityofnewyork.us/Environment/2015-Street-Tree-Census-Tree-Data/uvpi-gqnh/about_data"
data = load_data(ID, LIMIT)


def trees_with_status_per_borough(data) -> dict:

	by_borough = (
		data.filter(
			pl.col("status")
			.str.strip_chars()
			.str.to_lowercase()
			.eq("alive")
			& pl.col("boroname").is_not_null()
		)
		.group_by("boroname")
		.len()
		.with_columns(pl.col("boroname").replace(BOROUGH_MAP).alias("borough"))
		.drop("boroname")
		.with_columns(pl.col("borough").cast(pl.Int64))
		.sort("len", descending=True)
	)
	print(by_borough)

	filename = prepare_dataset_for_db(
		dataset=by_borough,
		dataset_x="borough",
		dataset_y="len",
		title="Number of Trees by Borough in 2015 NYC Street Tree Census",
		type="order",
		city="New York City",
		source=SOURCE,
		subtitle="Number of alive street trees by borough",
	)

	return filename


if __name__ == "__main__":
	filename = trees_with_status_per_borough(data)
	upload_dataset(filename)
