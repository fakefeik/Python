"""
Module for parsing serialization.
"""
from country import Country, Graph


def load(file):
    """
    Loads countries from file and returns Graph(countries).
    :param file: str
    :return: Graph
    """
    countries = []
    for line in file:
        coordinates = line.replace('\n', '').split('; ')
        coordinates = [[int(x.split(', ')[0]),
                        int(x.split(', ')[1])] for x in coordinates]
        countries.append(Country(coordinates))
    return Graph(countries)


def save(data):
    """
    Saves countries to file.
    :param data: Graph
    """
    countries = [item[0].coordinates for item in data.items]
    string = ''
    for country in countries:
        for j, coordinates in enumerate(country):
            for i, coord in enumerate(coordinates):
                string += str(coord)
                if i == 0:
                    string += ', '
            if j != len(country) - 1:
                string += '; '
        string += '\n'
    return string
