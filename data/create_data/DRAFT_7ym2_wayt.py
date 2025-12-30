"""
Data for Automated Traffic Volume Counts
Dataset Identifier: 7ym2-wayt
Total Rows: 1900000
Data Last Updated: September 20, 2025
Last Fetched: 2025-12-28
SOURCE: https://data.cityofnewyork.us/Transportation/Automated-Traffic-Volume-Counts/7ym2-wayt/about_data
"""

import polars as pl

from data.utils.utils import (
    load_data,
    prepare_dataset_for_db,
    upload_dataset,
    BOROUGH_MAP,
)

ID = "7ym2-wayt"
LIMIT = 1900000
SOURCE = "https://data.cityofnewyork.us/Transportation/Automated-Traffic-Volume-Counts/7ym2-wayt/about_data"
data = load_data(ID, LIMIT)


# hm need to think about this, maybe like how many peopel go over a bridge in a day if there is enough readings. will need to look more at data
