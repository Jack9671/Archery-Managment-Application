import pycountry

def get_countries()->list:
    """Get list of all countries"""
    countries = []
    for country in pycountry.countries:
        countries.append(country.name)
    return sorted(countries)

