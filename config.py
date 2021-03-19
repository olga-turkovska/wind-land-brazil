import logging
from pathlib import Path

REPOSITORY_MODE = ''

# Case-study region
FED_STATE_CODE = 'BA'  # 'BA' | CE' | 'RN' | 'RS'

# Settings
SKIP_ORIGIN_DATA_FORMATTING = True
EXCLUDE_WIND_TURBINES_BY_YEAR = 2019

WIND_PARK_BOUNDARIES_METHOD = 'convex_hull'
BUFFER_CONVEX_HULL_M = 0.0001

CLUSTERING_METHOD = 'maximum_distance'
CLUSTERING_DISTANCE_M = 3000

# Coordinate reference systems (CRS / crs)
CRS_GLOBAL_WGS84_DEG = 'EPGS:4326'
CRS_BRAZIL_SIRGAS2000_DEG = 'EPSG:4674'
CRS_BRAZIL_POLYCONIC_M = 'EPSG:5880'

# Years before commission date
YEARS_BEFORE = 2

# Buffer radius, m
BUFFER_DEPLOYMENT_REGION_M = 3000

# Data directories
ORIGIN = Path('./data/origin/')

if REPOSITORY_MODE == 'BETA':
    MIDWAY = Path('./data/beta/midway/')
    READY = Path('./data/beta/ready/')
    ANALYSIS = Path('./data/beta/analysis/')
    FIGURE = Path('./data/beta/figures/')
    TABLE = Path('./data/beta/tables/')
else:
    MIDWAY = Path('./data/midway/')
    READY = Path('./data/ready/')
    RESULTS = Path('./data/results/')
    FIGURE = Path('./data/figures/')
    TABLE = Path('./data/tables/')

BRAZIL = {'BA': ['BAHIA', 'bahia',  'NorthEast', 'MIXED'],
          'CE': ['CEARÁ', 'ceara',  'NorthEast', 'CAATINGA'],
          'RN': ['RIO GRANDE DO NORTE', 'rio_norte',  'NorthEast', 'MIXED'],
          'RS': ['RIO GRANDE DO SUL', 'rio_sul', 'South', 'MIXED']}

FED_STATE = BRAZIL.get(FED_STATE_CODE)[0]
FED_STATE_NAME = BRAZIL.get(FED_STATE_CODE)[1]
REGION = BRAZIL.get(FED_STATE_CODE)[2]
BIOME = BRAZIL.get(FED_STATE_CODE)[3]

COUNTRY_CODE = 'BR'

# Reclassified land type codes
ANTHROPOGENIC_USE = 40
NATIVE_VEGETATION = 50
DUNES = 60
WATER = 70
NODATA = 255

ERL_PAPER_CLASSIFICATION = [ANTHROPOGENIC_USE, NATIVE_VEGETATION, DUNES, WATER]

# Language
PT = 'ÇÁÉÍÓÚÂÊÔÃÕÀÈÌÒÙÜ'
EN = 'CAEIOUAEOAOAEIOUU'
TRANSLATE_CHARACTERS = str.maketrans(PT, EN)

# Origin data
ORIGIN_BRAZIL_SHP = 'BRUFE250GC_SIR.shp'
ORIGIN_WIND_PARKS_SHP = 'Polígono_do_Parque_Eolioelétrico_EOL.shp'
ORIGIN_WIND_TURBINES_SHP = 'Aerogeradores.shp'
ORIGIN_WIND_PARKS_CSV = '2019_09_18_BIG_operational_wind_parks_origin.csv'
ORIGIN_BIOME_TIF = BIOME + '.tif'
ORIGIN_POWER_DENSITY_TIF = 'BRA_power-density_100m.tif'
ORIGIN_HUMAN_FOOTPRINT_TIF = 'HFP2009.tif'

# File names
# HYBRID keyword refers to a data set that includes parameters from various sources i.e., land cover maps, wind parks

BR_HUMAN_FOOTPRINT = 'BR_human_footprint.tif'
FED_STATE_HUMAN_FOOTPRINT = f'{FED_STATE_CODE}_human_footprint.tif'
COUNTRY_WT_SHP = COUNTRY_CODE + '_wind_turbines.shp'
FED_STATE_ANEEL_WT_SHP = FED_STATE_CODE + '_aneel_wind_turbines.shp'
FED_STATE_WT_SHP = FED_STATE_CODE + '_wind_turbines.shp'

COUNTRY_ANEEL_WP_CSV = 'BR_ANEEL_wind_parks.csv'
FED_STATE_WP_SHP = FED_STATE_CODE + '_wind_parks_ch_00.shp'

FED_STATE_WP_CORRECTED_SHP = FED_STATE_CODE + '_wind_parks_ch_00_cor.shp'
FED_STATE_BUFFER_CORRECTED_SHP = FED_STATE_CODE + 'wp_buffer_' + str(BUFFER_DEPLOYMENT_REGION_M) + '_cor.shp'

FED_STATE_TIF = FED_STATE_CODE + '.tif'
FED_STATE_SHP = FED_STATE_CODE + '.shp'

FED_STATE_CLUSTER_WP_PARAMETERS_CSV = FED_STATE_CODE + '_cluster_wp_parameters.csv'

FED_STATE_CLUSTER_HYBRID_SHP = FED_STATE_CODE + '_cluster_hybrid.shp'
FED_STATE_CLUSTER_HYBRID_CSV = FED_STATE_CODE + '_cluster_hybrid.csv'
FED_STATE_BUFFER_HYBRID_CSV = FED_STATE_CODE + '_buffer_hybrid.csv'

FED_STATE_POWER_DENSITY_1KM_TIF = FED_STATE_CODE + '_power_density_1km.tif'
FED_STATE_POWER_DENSITY_30M_TIF = FED_STATE_CODE + '_power_density_30m.tif'

AREA_TIF = FED_STATE.replace(' ', '').translate(TRANSLATE_CHARACTERS) + '_area_m2.tif'
LAND_COVER_TIF = FED_STATE.replace(' ', '').translate(TRANSLATE_CHARACTERS) + '.tif'
"""
if BIOME == 'MIXED':
    LAND_COVER_TIF = FED_STATE.replace(' ', '').translate(TRANSLATE_CHARACTERS) + '.tif'
    # AREA_TIF = FED_STATE.replace(' ', '').translate(TRANSLATE_CHARACTERS) + '_area_m2.tif'
    ORIGIN_BIOME_TIF = None
else:
    LAND_COVER_TIF = ORIGIN_BIOME_TIF
    # AREA_TIF = BIOME + '_area_m2.tif'
"""

# Set-up logger-----------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('log.log')
formatter = logging.Formatter('%(asctime)s : %(levelname)s: %(filename)s : %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

ESRISHAPE_FILE_EXTENSION = '.shp'
GEOJSON_FILE_EXTENSION = '.geojson'
RASTER_FILE_EXTENSION = '.tif'
TABLE_FILE_EXTENSION = '.csv'

# columns
# geometry for powe plant boundaries
column_geometry = 'geometry'
# cluster ID
column_cl_id = 'cluster_id'

# cluster geometry
column_geometry_cl = 'geometry_cl'

# deployment region geometry
column_geometry_dr = 'geometry_dr'

# comissioning year
column_comm_year = 'comm_year'

RASTER_LAYERS = {'land_use': LAND_COVER_TIF,
                 'area_ha': AREA_TIF,
                 'power_density': FED_STATE_POWER_DENSITY_30M_TIF}

CLUSTER_TYPES = {40: 'AnthLd',
                 50: 'NatVeg',
                 60: 'Coast'}

