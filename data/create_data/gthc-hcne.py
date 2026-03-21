import geopandas as gpd
from data.utils.utils import (
    prepare_dataset_for_db,
    upload_dataset,
    BOROUGH_MAP,
)


# Load the datasets
boundaries = gpd.read_file('ref/Borough_Boundaries_20260215.geojson')

# Calculate land area of each borough in square kilometers
boundaries['land_area_km2'] = boundaries['geometry'].to_crs({'init': 'epsg:3857'}).area / 10**6

# Map borough names to integers
boundaries['borough'] = boundaries['boro_name'].replace(BOROUGH_MAP).astype(int)


# prepare dataset for database
prepare_dataset_for_db(
    dataset=boundaries,
    dataset_x='borough',
    dataset_y='land_area_km2',
    title='Land Area of NYC Boroughs',
    type='order',
    city='New York City',
    source='https://data.cityofnewyork.us/City-Government/Borough-Boundaries/gthc-hcne/about_data',
    subtitle='Land area of each NYC borough in square kilometers',
)