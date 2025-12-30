"""
Data for NYC Dog Licensing
Dataset Identifier: nu7n-tubp
Total Rows: 750k
Data Last Updated: February 25, 2025
Last Fetched: 2025-12-29
SOURCE: https://data.cityofnewyork.us/Health/NYC-Dog-Licensing-Dataset/nu7n-tubp/about_data
"""

import polars as pl

from data.utils.utils import (
    load_data,
    prepare_dataset_for_db,
    upload_dataset,
    BOROUGH_MAP,
)
import json

ID = "nu7n-tubp"
LIMIT = 750000
SOURCE = "https://data.cityofnewyork.us/Health/NYC-Dog-Licensing-Dataset/nu7n-tubp/about_data"
data = load_data(ID, LIMIT)


def licenses_per_year(data) -> dict:

    # add year dfor isseu and expiration date
    data = data.with_columns(
        pl.col("licenseissueddate").str.to_datetime().dt.year().alias("issue_year"),
        pl.col("licenseexpireddate")
        .str.to_datetime()
        .dt.year()
        .alias("expiration_year"),
    )

    # Create a table of active licenses per year
    # Generate years from earliest issue year to 2026
    min_year = data.select(pl.col("issue_year").min()).item()
    years = list(range(min_year, 2027))

    # For each year, count licenses that were active (issued <= year < expiration)
    active_counts = []
    for year in years:
        count = data.filter(
            (pl.col("issue_year") <= year) & (pl.col("expiration_year") >= year)
        ).height
        active_counts.append({"issue_year": year, "len": count})

    by_year = pl.DataFrame(active_counts)

    # fitler only >2016 and <2024 since thats the range of extracts i think
    by_year = by_year.filter(
        (pl.col("issue_year") >= 2016) & (pl.col("issue_year") <= 2024)
    )

    filename = prepare_dataset_for_db(
        dataset=by_year,
        dataset_x="issue_year",
        dataset_y="len",
        title="NYC Dog Licenses Issued per Year",
        type="line",
        city="New York City",
        y_min=0,
        y_max=80000,
        source=SOURCE,
        subtitle="Number of dog licenses issued in New York City each year",
        note="Data as of February 2025.",
    )

    return filename


def license_per_borough_2024(data) -> dict:

    # filter to extract year 2024
    data_2024 = data.filter(pl.col("extract_year") == "2024")

    # use ref/nyc_zip_borough to map zip to borough
    # TODO find a better zip to borough mapping
    with open("data/ref/nyc_zip_borough.json", "r") as f:
        # turn into column borough, zip
        borough_data = json.load(f)
        # Convert from {borough: [zips]} to long format
        rows = []
        for borough, zips in borough_data.items():
            for zip_code in zips:
                rows.append({"borough": borough, "zip": str(zip_code)})
        zip_borough = pl.DataFrame(rows)

    data_2024_borough = data_2024.join(
        zip_borough,
        left_on="zipcode",
        right_on="zip",
        how="left",
    )

    by_borough = data_2024_borough.group_by("borough").len().sort("len", reverse=True)
    # map boroughs
    by_borough = by_borough.with_columns(
        pl.col("borough").replace(BOROUGH_MAP).alias("borough")
    )

    filename = prepare_dataset_for_db(
        dataset=by_borough,
        dataset_x="borough",
        dataset_y="len",
        title="NYC Dog Licenses by Borough",
        type="order",
        city="New York City",
        source=SOURCE,
        subtitle="Total number of dog licenses issued in New York City by borough in 2024",
    )

    return filename


if __name__ == "__main__":
    filename = licenses_per_year(data)
    upload_dataset(filename)

    # filename = license_per_borough_2024(data)
    # upload_dataset(filename)
