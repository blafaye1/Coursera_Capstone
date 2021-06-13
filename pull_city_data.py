import numpy as np
import geopandas as gpd
from shapely import geometry
# Will remove these imports
from bokeh.io import output_file, save
from bokeh.plotting import figure


def construct_grid(polygon, increment):

    sorted_lats = sorted(polygon.exterior.coords, key=lambda x: x[1])
    sorted_lons = sorted(polygon.exterior.coords, key=lambda x: x[0])

    min_lat, max_lat = sorted_lats[0][1], sorted_lats[-1][1]
    min_lon, max_lon = sorted_lons[0][0], sorted_lons[-1][0]

    point_grid = {
        'lats': [],
        'lons': []
    }

    for point_lat in np.arange(min_lat, max_lat, increment):
        for point_lon in np.arange(min_lon, max_lon, increment):
            point = geometry.Point(point_lon, point_lat)
            if polygon.contains(point):
                point_grid['lats'].append(point_lat)
                point_grid['lons'].append(point_lon)

    return point_grid


def define_city_geometry(city, state):
    state_df = gpd.read_file('sandbox/shape_data/{0}/{0}.shp'.format(state))
    city_df = state_df[state_df['NAME'] == city]

    city_geometry = city_df.iloc[0]['geometry']

    return city_geometry
    # return


def polygon2patch(city_geometry):
    geometry_data = {
        'xs': [],
        'ys': []
    }

    if isinstance(city_geometry, geometry.Polygon):
        geometry_data['xs'].append([point[0] for point in city_geometry.exterior.coords])
        geometry_data['ys'].append([point[1] for point in city_geometry.exterior.coords])
        for ring in city_geometry.interiors:
            geometry_data['xs'].append([point[0] for point in ring.coords])
            geometry_data['ys'].append([point[1] for point in ring.coords])
    else:
        for polygon in city_geometry:
            geometry_data['xs'].append([point[0] for point in polygon.exterior.coords])
            geometry_data['ys'].append([point[1] for point in polygon.exterior.coords])
            for ring in polygon.interiors:
                geometry_data['xs'].append([point[0] for point in ring.coords])
                geometry_data['ys'].append([point[1] for point in ring.coords])

    return geometry_data


def plot_init_grid(city, state, f_out):
    default_increment = 0.01
    city_geometry = define_city_geometry(city, state)
    if isinstance(city_geometry, geometry.Polygon):
        city_grid = construct_grid(city_geometry, default_increment)
    else:
        city_grid = {
            'lats': [],
            'lons': []
        }
        for poly in city_geometry:
            point_grid = construct_grid(poly, default_increment)
            city_grid['lats'].extend(point_grid['lats'])
            city_grid['lons'].extend(point_grid['lons'])

    polygon_points = polygon2patch(city_geometry)

    output_file(f_out)
    p = figure()
    p.circle('lons', 'lats', source=city_grid)
    p.multi_polygons(xs=[[polygon_points['xs']]],
                     ys=[[polygon_points['ys']]],
                     alpha=0.5, color='green')

    save(p)

    return


if __name__ == '__main__':
    plot_init_grid('Chicago', 'illinois', "tmp_chicago_test.html")
    plot_init_grid('San Francisco', 'california', "tmp_sf_test.html")
    pass
