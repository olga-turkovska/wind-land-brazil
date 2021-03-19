from geopandas import GeoDataFrame
from pre_processing import *
from technologies import WindPower
from auxilary import drop_duplicated_column, open_data, store_data


def preprocess_data(technology, format_origin=False, create_dataset=False, cluster_technology=False):
    formatted_data = None
    technology_dataset = None

    if format_origin:
        formatted_data = format_original_data(technology)
    else:
        logger.info('Skip formatting original data sets')

    if create_dataset:
        technology_dataset = create_technology_dataset(technology, formatted_data)
    else:
        logger.info('Skip creating boundaries')

    if cluster_technology:
        clustered = add_spatial_dimensions(technology,  deployment_region=True, data=technology_dataset)
    else:
        logger.info("Skip adding spatial dimensions")

    return clustered


def format_original_data(technology):
    if isinstance(technology, WindPower):
        input_data = open_data(ORIGIN / technology.origin_vector_country_wind_turbines)

        # clean raw data
        translated_data = translate_column_names(input_data, wind_turbine_column_names)
        cleaned_data = drop_duplicated_column(translated_data, duplicated_column)

        store_data(MIDWAY / technology.vector_country_wind_turbines, cleaned_data)

        # select the power generation plants for the study
        # 1. select the operational plants
        operational_plants = cleaned_data[cleaned_data[column_oprational_plants] == code_operational_plants].copy()

        # update power plants regiostration codes following BIG ANEEL data
        updated_plants = update_wind_park_registration_data(operational_plants).copy()

        # 2. select the case-study state by the registration code (CEG) of the power plants
        state_plants = select_case_study_state_plants_by_registration_code(updated_plants, technology.state_code)

        store_data(MIDWAY / technology.vector_state_wind_turbines, state_plants)
    else:
        logger.info("Other technologies have not been implemented yet")

    return state_plants


def create_technology_dataset(technology, data=None):
    if isinstance(technology, WindPower):
        # create wind park boundaries
        wind_parks_boundaries = technology.create_wind_park_boundaries(data=data)

        # create wind park parameters
        wind_park_parameters = technology.create_wind_park_parameters_dataset()

        # merge two data sets
        wind_parks = wind_parks_boundaries.merge(wind_park_parameters, on=column_code, how='left').copy()

        # exclude wind parks built in certain year from further analysis
        state_technology_dataset = wind_parks[wind_parks[column_comm_year] != EXCLUDE_WIND_TURBINES_BY_YEAR].copy()

        store_data(MIDWAY / technology.vector_state_wind_parks_boundaries, state_technology_dataset)
        
    else:
        logger.info("Other technologies have not been implemented yet")

    return state_technology_dataset


def add_spatial_dimensions(technology, deployment_region: bool, data=None, cluster_by_year=True):
    if isinstance(technology, WindPower):
        try:
            logger.info(f'{data.crs}')
        except AttributeError:
            data = open_data(MIDWAY / technology.vector_state_wind_parks_boundaries)
            logger.info(f'{data.crs}')
        gdf = technology.create_spatial_clusters(data, cluster_by_year)

        # add cluster ID to the technology dataset
        store_data(MIDWAY / technology.vector_state_wind_parks_boundaries,
                   gdf.drop(column_geometry_cl, axis=1))

        # store cluster boundaries
        store_data(MIDWAY / technology.vector_state_cluster_boundaries,
                   gdf.drop(column_geometry, axis=1).rename(columns={column_geometry_cl: column_geometry}))

        if deployment_region:
            gdf = technology.create_deployment_region_boundaries(gdf)
        else:
            logger.info('Deployment region was not added')

        # store deployment region boundaries
        store_data(MIDWAY / technology.vector_state_technology_deployment_region, gdf)
        return gdf
