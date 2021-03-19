import geopandas
import pandas as pd
from re import sub
import matplotlib.pyplot as plt
import shapely

from config import *
from auxilary import open_data, fix_invalid_geometry
from pre_processing.aneel_data import column_code, column_comm_year, column_geometry, wind_turbine_column_names


class WindPower:

    origin_vector_country_wind_turbines = f'Aerogeradores{ESRISHAPE_FILE_EXTENSION}'
    origin_vector_aneel_country_wind_parks = f'Polígono_do_Parque_Eolioelétrico_EOL{ESRISHAPE_FILE_EXTENSION}'

    def __init__(self, location_data_source='aneel', state_code=FED_STATE_CODE,
                 boundary_method=WIND_PARK_BOUNDARIES_METHOD, buffer_convex_hull=BUFFER_CONVEX_HULL_M,
                 clustering_method=CLUSTERING_METHOD,
                 clustering_distance=CLUSTERING_DISTANCE_M,
                 buffer_deployment_region=BUFFER_DEPLOYMENT_REGION_M,
                 technology_code='EOL'):

        self.data_source = location_data_source
        self.state_code = state_code
        self.boundary_method = boundary_method
        self.buffer_convex_hull = buffer_convex_hull
        if self.buffer_convex_hull == 0:
            raise ValueError('Buffer radius for convex hull boundaries is zero.')
        self.clustering_method = clustering_method
        self.clustering_distance = clustering_distance
        self.buffer_deployment_region = buffer_deployment_region
        self.technology_code = technology_code

    @property
    def vector_country_wind_turbines(self):
        return f'{COUNTRY_CODE}_wind_turbines{ESRISHAPE_FILE_EXTENSION}'

    @property
    def vector_state_wind_turbines(self):
        return f'{self.state_code}_wind_turbines{ESRISHAPE_FILE_EXTENSION}'

    @property
    def vector_state_wind_parks_boundaries(self):
        if self.boundary_method == 'convex_hull':
            if self.buffer_convex_hull < 1:
                return f'{self.state_code}_wind_parks_ch_buf_0{ESRISHAPE_FILE_EXTENSION}'
            else:
                return f'{self.state_code}_wind_parks_ch_buf_{self.buffer_convex_hull}{ESRISHAPE_FILE_EXTENSION}'
        else:
            logger.info('Other boundaries methods are not implemented. The data set is not saved')
            return 0

    @property
    def vector_state_cluster_boundaries(self):
        if self.clustering_method == 'maximum_distance':
            return f'{self.state_code}_wind_clusters_md_{self.clustering_distance}{ESRISHAPE_FILE_EXTENSION}'
        else:
            logger.info('Other methods are not implemented')
            return 0

    @property
    def vector_state_technology_deployment_region(self):
        return f'{self.state_code}_wind_deployment_region_{self.buffer_deployment_region}{ESRISHAPE_FILE_EXTENSION}'

    def create_wind_park_boundaries(self, data=None):
        if self.boundary_method == 'convex_hull':
            return self.__create_wind_park_boundaries_by_convex_hull(data)
        else:
            logger.info(f'Choose convex hull to create wind park boundaries. Other methods are not implemented.')
            return 0

    def create_wind_park_parameters_dataset(self, data=None, name='wp_name', capacity='capacity', turbines='turbines',
                                            comm_date='comm_date', comm_year='comm_year') -> pd.DataFrame:
        wind_turbines = data
        try:
            logger.info(f'{wind_turbines.crs}')
        except AttributeError:
            wind_turbines = open_data(MIDWAY / self.vector_state_wind_turbines)
            logger.info(f'{wind_turbines.crs}')

        wind_parks_aneel = open_data(MIDWAY/f'{sub("origin", "", (ORIGIN/ORIGIN_WIND_PARKS_CSV).stem)}'
                                            f'{(ORIGIN/ORIGIN_WIND_PARKS_CSV).suffix}')

        wind_park_parameters = pd.DataFrame(columns=[name, capacity, turbines, comm_year])

        wind_park_parameters[name] = wind_turbines.dissolve(by=column_code)[name]
        wind_park_parameters[capacity] = wind_turbines.dissolve(by=column_code, aggfunc='sum')[capacity]
        wind_park_parameters[turbines] = wind_turbines.dissolve(by=column_code, aggfunc='count')[name]

        wind_park_parameters = \
            wind_park_parameters.merge(wind_parks_aneel.set_index(column_code)[comm_date].to_frame(),
                                       on=column_code, how='left').copy()

        wind_park_parameters[comm_year] = pd.DatetimeIndex(wind_park_parameters[comm_date]).year
        wind_park_parameters = wind_park_parameters.drop(columns=comm_date)

        return wind_park_parameters

    def create_spatial_clusters(self, data: geopandas.GeoDataFrame, cluster_by_year: bool):
        if self.clustering_method == 'maximum_distance':
            return self.__create_spatial_clusters_by_maximum_distance(data, cluster_by_year)
        else:
            logger.info('Choose maximum_distance method to create spatial clusters. Other methods are not implemented.')
            return 0

    def create_deployment_region_boundaries(self, data: geopandas.GeoDataFrame):
        gdf = geopandas.GeoDataFrame(data.drop(column_geometry, axis=1), geometry=column_geometry_cl, crs=data.crs)
        gdf = gdf.to_crs(CRS_BRAZIL_POLYCONIC_M).copy()
        gdf[column_geometry_dr] = gdf[column_geometry_cl].buffer(self.buffer_deployment_region)
        polygons = geopandas.GeoDataFrame(gdf.drop(column_geometry_cl, axis=1), geometry=column_geometry_dr,
                                          crs=CRS_BRAZIL_POLYCONIC_M)
        polygons = polygons.to_crs(CRS_BRAZIL_SIRGAS2000_DEG)
        gdf = gdf.to_crs(CRS_BRAZIL_SIRGAS2000_DEG)
        print(gdf.info())
        return geopandas.overlay(polygons, gdf, how='difference')

    def __create_wind_park_boundaries_by_convex_hull(self, data=None) -> geopandas.GeoDataFrame:
        wind_turbines = data
        try:
            logger.info(f'{wind_turbines.crs}')
        except AttributeError:
            wind_turbines = open_data(MIDWAY / self.vector_state_wind_turbines)
            logger.info(f'{wind_turbines.crs}')

        wind_parks = wind_turbines.dissolve(by=column_code)
        wind_parks[column_geometry] = \
            wind_parks[column_geometry].apply(lambda x: x.convex_hull.buffer(self.buffer_convex_hull))
        return geopandas.GeoDataFrame(wind_parks[column_geometry], crs=wind_turbines.crs)

    def __create_spatial_clusters_by_maximum_distance(self, data: geopandas.GeoDataFrame,
                                                      cluster_by_year: bool, display_clusters=False) \
            -> geopandas.GeoDataFrame:

        if cluster_by_year:
            # group spatial boundaries of power plants by commissioning year
            data_by_year = data.dissolve(by=column_comm_year).reset_index()[[column_comm_year, column_geometry]]
            data_by_year = data_by_year.to_crs(crs=CRS_BRAZIL_POLYCONIC_M).copy()

            for year in data_by_year[column_comm_year].drop_duplicates():
                count_polygons = 1
                # create multipolygons to measure the distance between the power plants
                distance_multipolygons = data_by_year[data_by_year[column_comm_year] ==
                                                      year].geometry.apply(lambda x: x.buffer(self.clustering_distance))
                distance_multipolygons = distance_multipolygons.to_crs(CRS_BRAZIL_SIRGAS2000_DEG)

                # create spatial clusters
                for multipolygon in distance_multipolygons:
                    try:
                        logger.info(f'{len(list(distance_multipolygons.values[0].geoms))} spatial clusters'
                                    f' detected for {year}')

                        for polygon in list(multipolygon.geoms):
                            mask = (data[column_comm_year] == year) & (data.geometry.intersects(polygon))

                            cluster_id = f'{self.state_code}_EOL_P{year}_G{count_polygons}'
                            cluster_geometry = data[mask].geometry.apply(
                                lambda x: polygon.intersection(x)).unary_union

                            data.loc[mask, column_cl_id] = cluster_id
                            data.loc[mask, column_geometry_cl] = cluster_geometry.wkt

                            count_polygons = count_polygons + 1

                            if display_clusters:
                                df = data[data[column_cl_id] == cluster_id][column_geometry_cl].apply(shapely.wkt.loads)
                                gdf = geopandas.GeoDataFrame(df, geometry=column_geometry_cl)
                                ax = geopandas.GeoSeries(polygon).plot()
                                gdf.plot(ax=ax, color='coral')
                                plt.title(cluster_id)
                                plt.show()

                    except AttributeError:
                        logger.info(f'1 spatial cluster detected for {year}')

                        cluster_id = f'{self.state_code}_EOL_P{year}_G0'
                        cluster_geometry = data[data[column_comm_year] ==
                                                year].geometry.apply(lambda x: multipolygon.intersection(x)).unary_union

                        data.loc[data[column_comm_year] == year, column_cl_id] = cluster_id
                        data.loc[data[column_comm_year] == year, column_geometry_cl] = cluster_geometry.wkt

                        if display_clusters:
                            df = data[data[column_cl_id] == cluster_id][column_geometry_cl].apply(shapely.wkt.loads)
                            gdf = geopandas.GeoDataFrame(df, geometry=column_geometry_cl)
                            ax = distance_multipolygons.plot()
                            gdf.plot(ax=ax, color='coral')
                            plt.title(cluster_id)
                            plt.show()

            data[column_geometry_cl] = data[column_geometry_cl].apply(shapely.wkt.loads).copy()
            print(data.info())
            return data
        else:
            logger.info('Not implemented')
            return 0

