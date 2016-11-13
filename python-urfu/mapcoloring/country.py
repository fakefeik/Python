"""
Module for working with countries.
"""
import poly


class Country:
    """
    Class for country.
    """
    def __init__(self, coordinates=None):
        self.coordinates = coordinates

    def __eq__(self, other):
        return self.coordinates == other.coordinates

    def __contains__(self, item):
        return (poly.are_intersecting(self.coordinates, item.coordinates) or
                poly.is_inside(self.coordinates, item.coordinates) or
                poly.is_inside(item.coordinates, self.coordinates))


class Graph:
    """
    Class representing graph.
    """
    def __init__(self, items):
        self.items = [[item, None] for item in items]

    def __eq__(self, other):
        return self.items == other.items

    def get_neighbours(self, item):
        """
        Returns all neighbours of given Country item.
        :param item: Country
        """
        for i in self.items:
            if i[0] in item[0] and i != item:
                yield i
