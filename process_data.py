import geopandas
import rasterio
import os
import time

from config import *
from pre_processing import *
"""
land_cover_raster = rasterio.open(os.path.join(ORIGIN, LAND_COVER_TIF))
brazil = geopandas.read_file(os.path.join(ORIGIN, ORIGIN_BRAZIL_SHP))
state_polygon = brazil[brazil.NM_ESTADO == FED_STATE]
print(state_polygon.geometry.values)
raster_out, transform_out = rasterio.mask.mask(land_cover_raster, state_polygon.geometry.values, crop=True)
print(land_cover_raster.meta)

meta = land_cover_raster.meta
print(raster_out.shape)
meta.update({'driver': 'GTIff',
             'count': 34,
             'width': raster_out.shape[2],
             'height': raster_out.shape[1],
             'crs': {'init': 'epsg:4326'},
             'transform': transform_out,
             'compress': 'lzw'})
print(meta)

with rasterio.open(os.path.join(READY,
                                FED_STATE.replace(' ', '').translate(TRANSLATE_CHARACTERS) + '.tif'),
                   'w', **meta) as r:
    r.write(raster_out)
"""
# create_reference_area()
# create_one_buffer_wind_parks(BUFFER, False)
# get_wind_parks_group()
# get_land_cover_area_shp()
# get_land_cover_buffer_csv()
# combine_cluster_data()

get_land_cover_for_state_parks(reclassify=True)
get_power_density_for_state_parks()
get_area_for_state_parks()

# get_area_for_state_parks()
# get_land_cover_area()
# get_land_cover_area_shp()
# get_land_cover_buffer_csv()



# turbines = geopandas.read_file(os.path.join(MIDWAY, COUNTRY_WT_SHP))
# operational_turbines = turbines[turbines.comm_oper == 1]
# print(operational_turbines.info())
# brazil = geopandas.read_file(os.path.join(ORIGIN, ORIGIN_BRAZIL_SHP))
# northeast = brazil[brazil.NM_REGIAO == 'NORDESTE']
# print(northeast.info())

# overlay_vectors(operational_turbines, northeast, 'intersection', 'aneel_wind_turbines_northeast.shp')

# extract_state_wind_turbines()
# select_turbines_for_analysis()
# create_reference_area()
# buffer_wind_parks()
# get_wind_parks_group()



# get_land_cover_for_state_parks(reclassify=True)
#get_power_density_for_state_parks()

# vector = geopandas.read_file(os.path.join(ORIGIN, ORIGIN_BRAZIL_SHP))
# raster = rasterio.open(os.path.join(ORIGIN, 'CAATINGA.tif'))

# state = vector[vector.NM_ESTADO == FED_STATE]
#mask_raster_with_vector(vector, raster, 34, 'RN_CAATINGA.tif')

# biome='MATAATLANTICA'
"""
for band in range(9, 35):
    band_tif = biome + '_' + str(band) + '.tif'
    raster = rasterio.open(os.path.join(MIDWAY, band_tif))
    print(band_tif)
    name = FED_STATE_CODE + '_' + band_tif
    mask_raster_with_vector(vector, raster, 1, name)
"""

def step_2(state, biome):
    state_shp = state + '.shp'
    biome_shp = biome + '.shp'
    output_shp = state + '_' + biome + '.shp'
    overlay_vectors(state_shp, biome_shp,'intersection', output_shp)


def step_3(biome, intersected_shp):
    biome_tif = biome + '.tif'

    try:
        mask_raster_with_vector(intersected_shp, biome_tif)

    except MemoryError:
        with rasterio.open(os.path.join(ORIGIN, biome_tif)) as raster:
            count = 1
            for band in range(1, 35):
                band_tif = biome + '_' + str(band) + '.tif'
                extract_raster_band(raster, biome, band)
                mask_raster_with_vector(intersected_shp, band_tif, count, name)
