def get_city_state(city_nickname):
    cities = {
        'sf': ('San Francisco', 'california'),
        'chicago': ('Chicago', 'illinois'),
        'nyc': ('New York', 'new_york')
    }
    return cities[city_nickname]
