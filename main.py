import technologies
import land_use
from beta_preprocessing import preprocess_data
from config import READY, TABLE_FILE_EXTENSION, ERL_PAPER_CLASSIFICATION
from auxilary import open_data


def main():
    wind_power = technologies.WindPower()
    """
    preprocess_data(wind_power, format_origin=True, create_dataset=True, cluster_technology=True)    
    
    for spatial_dimension in ['cluster_id', 'deployment_region']: 
        land_use.extract_raster_layers_for_technology(wind_power, spatial_dimension=spatial_dimension,
                                                      layers=['land_use', 'area_ha'])
        land_use.extract_land_use_pattern_for_technology(wind_power, spatial_dimension)
        land_use.reclassify_land_use_codes(READY / f'{wind_power.state_code}_{wind_power.technology_code}'
                                           f'_{spatial_dimention}_land_use_patterns{TABLE_FILE_EXTENSION}',
                                           code_field='code')
        land_use.extract_land_use_before_comissioning(READY / f'{wind_power.state_code}_{wind_power.technology_code}'
                                                      f'_cluster_land_use_patterns_reclass{TABLE_FILE_EXTENSION}',
                                                      year_before=YEARS_BEFORE)

    land_use.extract_land_use_by_year(READY /f'{wind_power.state_code}_{wind_power.technology_code}'
                                             f'_cluster_land_use_patterns_reclass{TABLE_FILE_EXTENSION}',
                                             year=2018)
    """
    data_cluster = land_use.determine_cluster_type(READY / f'{wind_power.state_code}_{wind_power.technology_code}'
                                                   f'_cluster_land_use_patterns_reclass_before{TABLE_FILE_EXTENSION}',
                                                   formated_data=False)
    data_cluster_final = land_use.calculate_area_shares(data_cluster)

    data_region = open_data(READY / f'{wind_power.state_code}_{wind_power.technology_code}'
                            f'_deployment_region_land_use_patterns_reclass_before{TABLE_FILE_EXTENSION}')
    data_region_formated = land_use.modify_data_format(data_region)
    data_region_final = land_use.calculate_area_shares(data_region_formated,
                                                       land_use_codes=ERL_PAPER_CLASSIFICATION)

    land_use.merge_cluster_and_deployment_region(data_cluster_final, data_region_final,
                                                 land_use_codes=ERL_PAPER_CLASSIFICATION)
    return 0


if __name__ == '__main__':
    main()
