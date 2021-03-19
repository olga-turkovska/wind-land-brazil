import geopandas
import rasterio
import pandas as pd
import numpy as np
import re
import pathlib

from config import *
import technologies
from auxilary import open_data, store_data, band_year, erl_paper


def extract_raster_layers_for_technology(technology, spatial_dimension, layers):

    if spatial_dimension == 'cluster':
        if isinstance(technology, technologies.WindPower):
            vectors = geopandas.read_file(MIDWAY / technology.vector_state_cluster_boundaries)
            dir_name = f'{technology.clustering_method}_{technology.clustering_distance}'

        else:
            logger.info('Not implemented')

    elif spatial_dimension == 'deployment_region':
        if isinstance(technology, technologies.WindPower):
            vectors = geopandas.read_file(MIDWAY / technology.vector_state_technology_deployment_region)
            dir_name = f'buffer_radius_{technology.buffer_deployment_region}'
        else:
            logger.info('Not implemented')

    for lr in layers:
        store_path = f'{lr}/{type(technology).__name__}/{spatial_dimension}/{dir_name}'
        Path(READY / store_path).mkdir(parents=True, exist_ok=True)

        with rasterio.open(MIDWAY / RASTER_LAYERS.get(lr)) as src:
            vectors = vectors.to_crs(src.crs)

            for idx in vectors[column_cl_id].drop_duplicates():
                polygon = vectors[vectors[column_cl_id] == idx][column_geometry].values[0]
                print(polygon)
                raster_out, transform_out = rasterio.mask.mask(src, [polygon], crop=True)
                print(raster_out.shape)
                store_data(READY / store_path / f'{idx}{RASTER_FILE_EXTENSION}', raster_out,
                           raster_meta={'transform': transform_out,
                                        'driver': 'Gtiff',
                                        'height': raster_out.shape[1],
                                        'width': raster_out.shape[2],
                                        'count': src.count,
                                        'dtype': raster_out.dtype,
                                        'crs': src.crs})
    return 0


def extract_land_use_pattern_for_technology(technology, spatial_dimension):

    columns = ['state', 'cluster_id', 'comm_year', 'year', 'code', 'area_m2']
    patterns = pd.DataFrame(columns=columns)
    total_cluster_area = 0
    if spatial_dimension == 'cluster':
        technology_attributes = geopandas.read_file(MIDWAY / technology.vector_state_cluster_boundaries)
        dir_name = f'{technology.clustering_method}_{technology.clustering_distance}'

    elif spatial_dimension == 'deployment_region':
        technology_attributes = geopandas.read_file(MIDWAY / technology.vector_state_technology_deployment_region)
        dir_name = f'buffer_radius_{technology.buffer_deployment_region}'

    for idx in technology_attributes[column_cl_id].drop_duplicates():
        print(idx)

        comm_year = technology_attributes[technology_attributes[column_cl_id] == idx][column_comm_year].values[0]
        land_use = rasterio.open(READY / 'land_use' / type(technology).__name__ / spatial_dimension / dir_name /
                                 f'{idx}{RASTER_FILE_EXTENSION}')
        grid_area_ha = rasterio.open(READY / 'area_ha' / type(technology).__name__ / spatial_dimension / dir_name /
                                     f'{idx}{RASTER_FILE_EXTENSION}')
        cluster_area_km = grid_area_ha.read(1)[grid_area_ha.read(1) != NODATA].sum() * 1e-6
        if comm_year < 2019:
            total_cluster_area = total_cluster_area + cluster_area_km
        else:
            total_cluster_area = total_cluster_area + cluster_area_km

        for band in range(1, land_use.count + 1):
            codes = np.unique(land_use.read(band))
            codes = codes[codes != NODATA]

            for code in codes:
                row = [FED_STATE_CODE, idx, comm_year, band_year.get(band), code]
                area_m2 = np.sum(grid_area_ha.read(1) * [land_use.read(band) == code])
                row.append(area_m2)

                patterns = patterns.append(dict(zip(columns, row)), ignore_index=True)
                del row

        print(cluster_area_km)
    print(total_cluster_area)
    patterns.to_csv(READY / f'{idx[:6]}_{spatial_dimension}_land_use_patterns{TABLE_FILE_EXTENSION}')
    return 0


def reclassify_land_use_codes(data_path, reclass_scheme=erl_paper, code_field=None):
    if data_path.suffix == TABLE_FILE_EXTENSION:
        data = open_data(data_path)
        print(data.info())
        data['code_reclass'] = data[code_field].apply(lambda x: reclass_scheme.get(x))
        store_data(READY / f'{data_path.stem}_reclass{TABLE_FILE_EXTENSION}', data)
    return 0


def extract_land_use_before_comissioning(data_path, year_before):
    data = open_data(data_path)
    data = data[data['year'] == data['comm_year'] - year_before].reset_index(drop=True)
    store_data(READY / f'{data_path.stem}_before{TABLE_FILE_EXTENSION}', data)
    return 0


def extract_land_use_by_year(data_path, year):
    data = open_data(data_path)
    data = data[data['year'] == year].reset_index(drop=True)
    store_data(READY / f'{data_path.stem}_{year}{TABLE_FILE_EXTENSION}', data)
    return 0


def modify_data_format(data, code_field='code_reclass', groupby_fields=['state', 'cluster_id', 'comm_year', 'year'],
                       keep_columns=['area_m2'], pivot_index='cluster_id'):
    groupby_fields.append(code_field)
    grouped_by_land_use_code = data.groupby(groupby_fields).sum().loc[:, keep_columns].reset_index()
    pivoted = grouped_by_land_use_code.pivot(index=pivot_index, columns=code_field, values='area_m2')
    del groupby_fields[groupby_fields.index(code_field)]

    to_merge = grouped_by_land_use_code.groupby(groupby_fields).count().reset_index()[groupby_fields]
    merged = pivoted.merge(to_merge, on=['cluster_id'])
    return merged


def determine_cluster_type(data_path, formated_data, land_use_codes=[40, 50]):
    data = open_data(data_path)
    if formated_data:
        df = data
    else:
        df = modify_data_format(data)

    df['type_code'] = df[land_use_codes].idxmax(1)
    df['cluster_type'] = df['type_code'].apply(lambda x: CLUSTER_TYPES.get(x))
    df = df.drop(columns='type_code')

    return df


def calculate_area_shares(data, land_use_codes=[40, 50]):
    try:
        data['cluster_area_m2'] = data[land_use_codes].sum(axis=1)
    except KeyError as e:
        redundant_code = re.findall(r'[1-9][0]', e.__str__())[0]
        del land_use_codes[land_use_codes.index(int(redundant_code))]
        data['cluster_area_m2'] = data[land_use_codes].sum(axis=1)

    for code in land_use_codes:
        column_name = f'{code}_percentage'
        data[column_name] = data[code] / data['cluster_area_m2'] * 1e2
    return data


def merge_cluster_and_deployment_region(cluster, region, land_use_codes: list):
    print(region.info())
    columns = ['cluster_id']
    for code in land_use_codes:
        column_name = f'{code}_percentage'
        columns.append(column_name)

    try:
        region_to_merge = region[columns]
    except KeyError as e:
        redundant_column = f'{re.findall(r"[1-9][0]", e.__str__())[0]}_percentage'
        del columns[columns.index(redundant_column)]
        region_to_merge = region[columns]
    columns_renamed = [f'{x}_dr' for x in columns if x != 'cluster_id']

    region_to_merge = region_to_merge.rename(columns=dict(zip([x for x in columns if x != 'cluster_id'],
                                                              columns_renamed)))

    merged = cluster.merge(region_to_merge, on='cluster_id')
    merged.to_csv(RESULTS / f'{FED_STATE_CODE}_EOL_land_use_patterns{TABLE_FILE_EXTENSION}')
    return 0
