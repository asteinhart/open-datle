"""
Data for NYC Fire Hydrants
Dataset Identifier: 5bgh-vtsn
Total Rows: 120k+
SOURCE: https://data.cityofnewyork.us/Environment/Fire-Hydrants/5bgh-vtsn/about_data
"""

from fileinput import filename
import polars as pl

from data.utils.utils import (
    BOROUGH_MAP,
	load_data,
	prepare_dataset_for_db,
	upload_dataset,
)


ID = "5bgh-vtsn"
LIMIT = 120000
SOURCE = "https://data.cityofnewyork.us/Environment/Fire-Hydrants/5bgh-vtsn/about_data"
data = load_data(ID, LIMIT)


def hydrants_per_borough(data) -> dict:

    by_borough = (
        data.filter(pl.col("boro").is_not_null())
        .with_columns(pl.col("boro").cast(pl.Int64).alias("borough"))
        .filter(pl.col("borough").is_between(1, 5, closed="both"))
        .with_columns(
            pl.col("borough").map_elements(
                lambda x: {1: "Manhattan", 2: "Bronx", 3: "Brooklyn", 4: "Queens", 5: "Staten Island"}.get(x, x)
            ).alias("borough")
        )
        .group_by("borough")
        .len()
        .sort("borough")
    )

    # map boroughs to integers using BOROUGH_MAP
    by_borough = by_borough.with_columns(
        pl.col("borough").replace(BOROUGH_MAP).cast(int).alias("borough")
    )
    by_borough = by_borough.sort("len", descending=True)

    print(by_borough)

    filename = prepare_dataset_for_db(
		dataset=by_borough,
		dataset_x="borough",
		dataset_y="len",
		title="NYC Fire Hydrants by Borough",
		type="order",
		city="New York City",
		source=SOURCE,
		subtitle="Number of fire hydrants by borough",

	)

    return filename


if __name__ == "__main__":
	filename = hydrants_per_borough(data)
	upload_dataset(filename)
