import numpy as np
import math
from pyproj import CRS, Transformer
from scipy.optimize import minimize_scalar


def gen_wgs2merc():
    crs_wgs = CRS("EPSG:4326")
    crs_merc = CRS("EPSG:3785")
    crs_transformer = Transformer.from_crs(crs_wgs, crs_merc)
    return crs_transformer.transform


def kil2mil(km):
    return km * 0.621371


def calc_dist_latlon(lat_1, lon_1, lat_2, lon_2, unit='mi'):
    r_earth = 6371  # avg radius of Earth in km
    d_lat = np.radians(lat_2 - lat_1)
    d_lon = np.radians(lon_2 - lon_1)

    a = ((math.sin(d_lat / 2) * math.sin(d_lat / 2)) +
         (math.cos(np.radians(lat_1)) * math.cos(np.radians(lat_2)) *
          math.sin(d_lon / 2) * math.sin(d_lon / 2)))

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = r_earth * c

    if unit == 'km':
        return d
    elif unit == 'mi':
        return kil2mil(d)
    else:
        print("Units not recognized.")
        return 0


def gen_func_to_opt(start_lat, start_lon, var):
    if var == 'lat':
        def func_to_opt(x):
            return abs(calc_dist_latlon(start_lat, start_lon, x, start_lon) - 1)
    else:
        def func_to_opt(x):
            return abs(calc_dist_latlon(start_lat, start_lon, start_lat, x) - 1)
    return func_to_opt


def find_a_mile(start_lat, start_lon, var):
    func_to_opt = gen_func_to_opt(start_lat, start_lon, var)
    if var == 'lat':
        bounds = (start_lat, start_lat + 10)
    elif var == 'lon':
        bounds = (start_lon, start_lon + 10)
    else:
        print('Specify which variable to optimize')
        return

    optimized = minimize_scalar(func_to_opt, method='bounded', bounds=bounds)

    if var == 'lat':
        new_lat = optimized.x
        new_lon = start_lon
        axis = 1
    else:
        new_lat = start_lat
        new_lon = optimized.x
        axis = 0

    difference = wgs2merc(start_lat, start_lon)[axis] - wgs2merc(new_lat, new_lon)[axis]
    return int(abs(difference))


def find_avg_city_mile(min_lat, min_lon, max_lat, max_lon):
    dist_1 = find_a_mile(min_lat, min_lon, 'lat')
    dist_2 = find_a_mile(min_lat, min_lon, 'lon')
    dist_3 = find_a_mile(max_lat, max_lon, 'lat')
    dist_4 = find_a_mile(max_lat, max_lon, 'lon')

    return (dist_1 + dist_2 + dist_3 + dist_4) / 4


if __name__ == '__main__':
    pass
