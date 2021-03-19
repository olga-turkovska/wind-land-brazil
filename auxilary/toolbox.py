import pandas as pd
import rasterio
import geopandas
import shapely.geometry
from config import *


def drop_duplicated_column(data: pd.DataFrame, drop_column: str):
    return data.drop(axis=1, columns=drop_column)


def open_data(path, **kwargs):
    if path.suffix == TABLE_FILE_EXTENSION:
        return pd.read_csv(path)
    elif path.suffix == ESRISHAPE_FILE_EXTENSION:
        return geopandas.read_file(path)
    elif path.suffix == RASTER_FILE_EXTENSION:
        return rasterio.open(path)


def store_data(path, data, raster_meta=None, raster_bands=None):
    if path.suffix == TABLE_FILE_EXTENSION:
        data.to_csv(path, index=False)
    elif path.suffix == ESRISHAPE_FILE_EXTENSION:
        data.to_file(path, driver='ESRI Shapefile')
    elif path.suffix == GEOJSON_FILE_EXTENSION:
        data.to_file(path, driver='GeoJSON')
    elif path.suffix == RASTER_FILE_EXTENSION:
        with rasterio.open(path, 'w', **raster_meta) as src:
            src.write(data)
    return 0


def fix_invalid_geometry(geometry):
    return geometry.buffer(0.000001)
