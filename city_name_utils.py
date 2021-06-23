def city_dictionary():
    cities = {
        'sf': ('San Francisco', 'california'),
        'chicago': ('Chicago', 'illinois'),
        'nyc': ('New York', 'new_york')
    }
    return cities


def get_city_state(city_nickname):
    cities = city_dictionary()
    return cities[city_nickname]


def get_city_list():
    cities = city_dictionary()
    return cities.keys()


if __name__ == '__main__':
    pass
