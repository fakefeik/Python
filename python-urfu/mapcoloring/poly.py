"""
Module for working with polygons
"""
import copy

MAX = 10 ** 10


def is_inside(poly1, poly2):
    """
    Checks whether one polygon is inside another.
    :param poly1: list
    :param poly2: list
    :return: bool
    """
    poly1_leftmost, poly1_rightmost, poly1_upmost, poly1_downmost = _get_most_coordinates(poly1)
    poly2_leftmost, poly2_rightmost, poly2_upmost, poly2_downmost = _get_most_coordinates(poly2)

    return (poly2_leftmost[0] > poly1_leftmost[0] and
            poly2_rightmost[0] < poly1_rightmost[0] and
            poly2_upmost[1] > poly1_upmost[1] and
            poly2_downmost[1] < poly1_downmost[1])


def _get_most_coordinates(poly):
    """
    Gets upmost, leftmost, downmost and rightmost coordinates of a polygon.
    :param poly: list
    :return: tuple
    """
    poly_leftmost = [MAX, 0]
    poly_rightmost = [0, 0]
    poly_upmost = [0, MAX]
    poly_downmost = [0, 0]
    for coordinate in poly:
        if coordinate[0] < poly_leftmost[0]:
            poly_leftmost = coordinate
        if coordinate[0] > poly_rightmost[0]:
            poly_rightmost = coordinate
        if coordinate[1] < poly_upmost[1]:
            poly_upmost = coordinate
        if coordinate[1] > poly_downmost[1]:
            poly_downmost = coordinate
    return poly_leftmost, poly_rightmost, poly_upmost, poly_downmost


def are_intersecting(poly1, poly2):
    """
    Checks if two polygons are intersecting.
    :param poly1: list
    :param poly2: list
    :return: bool
    """
    poly1 = copy.deepcopy(poly1)
    poly2 = copy.deepcopy(poly2)
    poly1.append(poly1[0])
    poly2.append(poly2[0])
    for i in range(len(poly1) - 1):
        for j in range(len(poly2) - 1):
            if _intersect(poly1[i], poly1[i + 1],
                          poly2[j], poly2[j + 1]):
                return True
    return False


def _intersect(point1, point2, point3, point4):
    """
    Checks if there is intersection between two lines.
    :param point1: [x, y]
    :param point2: [x, y]
    :param point3: [x, y]
    :param point4: [x, y]
    :return: bool
    """
    a1 = point2[0] - point1[0]
    b1 = point1[1] - point2[1]
    c1 = a1 * point1[1] + b1 * point1[0]

    a2 = point4[0] - point3[0]
    b2 = point3[1] - point4[1]
    c2 = a2 * point3[1] + b2 * point3[0]

    determinate = a1 * b2 - a2 * b1

    intersection = None
    if determinate != 0:
        x = (b2 * c1 - b1 * c2) / determinate
        y = (a1 * c2 - a2 * c1) / determinate

        intersect = [y, x]

        if (_in_bounded_box(point1, point2, intersect)
                and _in_bounded_box(point3, point4, intersect)):
            intersection = intersect
    return intersection


def _in_bounded_box(point1, point2, point3):
    """
    Checks something.
    :param point1: [x, y]
    :param point2: [x, y]
    :param point3: [x, y]
    :return: bool
    """
    if point1[0] < point2[0]:
        between_lats = point1[0] <= point3[0] <= point2[0]
    else:
        between_lats = point2[0] <= point3[0] <= point1[0]

    if point1[1] < point2[1]:
        between_lons = point1[1] <= point3[1] <= point2[1]
    else:
        between_lons = point2[1] <= point3[1] <= point1[1]
    return between_lats and between_lons
