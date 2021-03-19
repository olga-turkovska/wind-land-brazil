import geopandas
import pandas as pd
from re import sub
from config import *
from auxilary import open_data, store_data

code_operational_plants = 1

column_code = 'CEG'
column_comm_year = 'comm_year'
column_geometry = 'geometry'
column_oprational_plants = 'comm_oper'
column_state = 'state'

duplicated_column = 'operating'

wind_turbine_column_names = ['capacity', 'total_height_m', 'hub_height_m', 'rotor_diam_m',
                             'data_updated', 'wp_code', 'wp_name', 'wt_type', 'easting',
                             'northing', 'comm_oper', 'owner', 'CEG',
                             'data_version', 'datum ', 'zone', 'operating', 'geometry']


def translate_column_names(input_data: geopandas.GeoDataFrame,
                           english_column_names: list) -> geopandas.GeoDataFrame:
    data_origin = input_data
    logger.info(f'Column names in Portuguese:\n {data_origin.columns.values}')
    logger.info(f'Column names in English:\n {english_column_names}')

    # translate Portuguese column values to English
    translate = dict(zip(data_origin.columns.values, english_column_names))
    data_translated = data_origin.rename(columns=translate)

    logger.info(f'{data_translated.info()}')

    return data_translated


def format_strings_origin_wind_park_data(path=ORIGIN/ORIGIN_WIND_PARKS_CSV) -> pd.DataFrame:
    data = pd.read_csv(path, header=0, names=['CEG', 'wp_name', 'comm_date', 'capacity_aut_kW',
                                              'capacity_kW', 'unknown', 'owner', 'municipality'])

    ceg = data.CEG.str.split('-', expand=True)
    ceg[0] = ceg[0].str.replace('.', '')
    ceg[1] = ceg[1].str.replace('.', '-')
    ceg[1] = ceg[1].str.replace(' ', '')
    data[column_code] = ceg[0].str.cat(ceg[1], '-')

    data[column_state] = data.CEG.str.extract(r'([A-Z][A-Z])(\d)')[0]
    print(data.head())

    store_data(MIDWAY/f'{sub("origin", "", path.stem)}{path.suffix}', data)
    return data


def update_wind_park_registration_data(data):
    try:
        data_new_code = open_data(MIDWAY/f'{sub("origin", "", (ORIGIN/ORIGIN_WIND_PARKS_CSV).stem)}'
                                         f'{(ORIGIN/ORIGIN_WIND_PARKS_CSV).suffix}')
    except FileNotFoundError:
        data_new_code = format_strings_origin_wind_park_data()

    codes_to_update = list(data_new_code.CEG[data_new_code.CEG.str.contains(r'\d{6}-\d-0[2-9]')])

    for code in codes_to_update:
        data[column_code].where(~data.CEG.str.contains(code[7:15]), code, inplace=True)
    return data


def select_case_study_state_plants_by_registration_code(data, state_code):
    return data[data[column_code].str.contains(state_code)]
