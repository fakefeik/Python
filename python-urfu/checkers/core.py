"""
Core logic of checkers game
"""
from enum import Enum
import copy
import winsound


class Checker(Enum):
    """
    Checker enum
    """
    black = False
    white = True


class Mode(Enum):
    """
    Mode enum
    """
    two_players = 1
    computer = 2
    online = 3


class Difficulty(Enum):
    """
    Difficulty enum
    """
    easy = 1
    medium = 2
    hard = 3

QUEEN_COORDINATES_WHITE = [(1, 0), (3, 0), (5, 0), (7, 0), (9, 0)]
QUEEN_COORDINATES_BLACK = [(0, 9), (2, 9), (4, 9), (6, 9), (8, 9)]


# this looks ugly
def _get_binding_queen_moves(field, point, delta):
    """
    Returns binding queen moves
    :param field: list
    :param point: [x, y]
    :param delta: [dx, dy]
    :return: generator
    """
    for i in range(1, 10):
        if (in_field(field, (point[0] + (i + 1) * delta[0], point[1] + (i + 1) * delta[1])) and
                field[point[1] + i * delta[1]][point[0] + i * delta[0]]):
            if (field[point[1] + i * delta[1]][point[0] + i * delta[0]][0] != field[point[1]][point[0]][0] and
                    not field[point[1] + (i + 1) * delta[1]][point[0] + (i + 1) * delta[0]]):
                while (in_field(field, (point[0] + (i + 1) * delta[0], point[1] + (i + 1) * delta[1]))
                       and not field[point[1] + (i + 1) * delta[1]][point[0] + (i + 1) * delta[0]]):
                    yield point[0] + (i + 1) * delta[0], point[1] + (i + 1) * delta[1]
                    i += 1
            return


# ...and this
def get_binding_moves(field, point):
    """
    Returns binding moves
    :param field: list
    :param point: [x, y]
    :return: generator
    """
    if field[point[1]][point[0]][1]:
        for move in _get_binding_queen_moves(field, point, (1, 1)):
            yield move
        for move in _get_binding_queen_moves(field, point, (1, -1)):
            yield move
        for move in _get_binding_queen_moves(field, point, (-1, 1)):
            yield move
        for move in _get_binding_queen_moves(field, point, (-1, -1)):
            yield move
    else:
        if (in_field(field, (point[0] + 2, point[1] + 2)) and
                field[point[1] + 1][point[0] + 1] and
                field[point[1] + 1][point[0] + 1][0] != field[point[1]][point[0]][0] and
                not field[point[1] + 2][point[0] + 2]):
            yield point[0] + 2, point[1] + 2
        if (in_field(field, (point[0] - 2, point[1] + 2)) and
                field[point[1] + 1][point[0] - 1] and
                field[point[1] + 1][point[0] - 1][0] != field[point[1]][point[0]][0] and
                not field[point[1] + 2][point[0] - 2]):
            yield point[0] - 2, point[1] + 2
        if (in_field(field, (point[0] + 2, point[1] - 2)) and
                field[point[1] - 1][point[0] + 1] and
                field[point[1] - 1][point[0] + 1][0] != field[point[1]][point[0]][0] and
                not field[point[1] - 2][point[0] + 2]):
            yield point[0] + 2, point[1] - 2
        if (in_field(field, (point[0] - 2, point[1] - 2)) and
                field[point[1] - 1][point[0] - 1] and
                field[point[1] - 1][point[0] - 1][0] != field[point[1]][point[0]][0] and
                not field[point[1] - 2][point[0] - 2]):
            yield point[0] - 2, point[1] - 2


def _get_possible_queen_moves(field, point, direction):
    """
    Returns all not binding queen moves
    :param field: list
    :param point: [x, y]
    :param direction: [dx, dy]
    :return: generator
    """
    for i in range(1, 10):
        if in_field(field, (point[0] + i * direction[0],
                            point[1] + i * direction[1])):
            if field[point[1] + i * direction[1]][point[0] + i * direction[0]]:
                break
            yield point[0] + i * direction[0], point[1] + i * direction[1]


def _get_possible_moves(field, point, delta):
    """
    Returns all possible moves for given point
    :param field: list
    :param point: [x, y]
    :param delta: int
    :return: generator
    """
    if field[point[1]][point[0]][1]:
        for move in _get_possible_queen_moves(field, point, (1, 1)):
            yield move
        for move in _get_possible_queen_moves(field, point, (1, -1)):
            yield move
        for move in _get_possible_queen_moves(field, point, (-1, 1)):
            yield move
        for move in _get_possible_queen_moves(field, point, (-1, -1)):
            yield move
    else:
        if (in_field(field, (point[0] + 1, point[1] + delta)) and
                not field[point[1] + delta][point[0] + 1]):
            yield point[0] + 1, point[1] + delta
        if (in_field(field, (point[0] - 1, point[1] + delta)) and
                not field[point[1] + delta][point[0] - 1]):
            yield point[0] - 1, point[1] + delta


def get_moves(field, point):
    """
    Returns all possible moves from on a given field from point
    :param field: list
    :param point: [x, y]
    :return: list
    """
    delta = 1 if field[point[1]][point[0]][0] == Checker.black else -1
    if len(list(get_binding_moves(field, point))) > 0:
        return list(get_binding_moves(field, point))
    return _get_possible_moves(field, point, delta)


def get_all_possible_moves(field, player):
    """
    Function that generates all possible moves on given field for a player
    :param field: list
    :param player: bool
    :return: generator
    """
    for pawn in moving_pawns(field, player):
        for move in get_moves(field, pawn):
            yield [(pawn, move)]
            temp_field = copy.deepcopy(field)
            temp_field = make_move(temp_field, pawn, move, False)
            if (pawn in binding_pawns(field, player) and
                    move in binding_pawns(temp_field, player)):
                for move2 in get_moves(temp_field, move):
                    yield [(pawn, move), (move, move2)]


def get_all_possible_moves_advanced(field, player):
    """
    Function that generates all possible moves on given field for a player
    :param field: list
    :param player: bool
    :return: generator
    """
    for pawn in moving_pawns(field, player):
        for move in get_moves(field, pawn):
            yield [(pawn, move)]
            temp_field = copy.deepcopy(field)
            temp_field = make_move(temp_field, pawn, move, False)
            if (pawn in binding_pawns(field, player) and
                    move in binding_pawns(temp_field, player)):
                for move2 in get_moves(temp_field, move):
                    yield [(pawn, move), (move, move2)]


def in_field(field, point):
    """
    Checks if point is in field
    :param field: list
    :param point: [x, y]
    :return: bool
    """
    return 0 <= point[0] < len(field[0]) and 0 <= point[1] < len(field)


def get_pawn_to_delete(field, first, second):
    """
    Function that returns coordinate of a pawn that has to be deleted
    :param field: list
    :param first: [x, y]
    :param second: [x, y]
    :return: [x, y]
    """
    direction = (int((second[0] - first[0]) / abs(second[0] - first[0])),
                 int((second[1] - first[1]) / abs(second[1] - first[1])))
    for i in range(1, abs(first[0] - second[0])):
        if field[first[1] + direction[1] * i][first[0] + direction[0] * i]:
            return first[0] + direction[0] * i, first[1] + direction[1] * i


def make_queen(field, point, sound):
    """
    Function that makes queen from checker if needed
    :param field: list
    :param point: [x, y]
    :param sound: bool
    :return: list
    """
    if (point in QUEEN_COORDINATES_BLACK and
            field[point[1]][point[0]] == (Checker.black, False)):
        field[point[1]][point[0]] = (Checker.black, True)
        if sound:
            winsound.PlaySound("cheeke.wav", winsound.SND_ASYNC)
    if (point in QUEEN_COORDINATES_WHITE and
            field[point[1]][point[0]] == (Checker.white, False)):
        field[point[1]][point[0]] = (Checker.white, True)
        if sound:
            winsound.PlaySound("breeke.wav", winsound.SND_ASYNC)
    return field


def binding_pawns(field, player):
    """
    Function that returns all binding pawns
    :param field: list
    :param player: bool
    :return: list
    """
    pawns = []
    for col in range(10):
        for row in range(10):
            if field[row][col] and field[row][col][0].value == player:
                if len(list(get_binding_moves(field, (col, row)))) > 0:
                    pawns.append((col, row))
    return pawns


def moving_pawns(field, player):
    """
    Function that returns all possible moving pawns on given field for
    a player
    :param field: list
    :param player: bool
    :return: generator
    """
    if len(binding_pawns(field, player)) > 0:
        for pawn in binding_pawns(field, player):
            yield pawn
    else:
        for j, line in enumerate(field):
            for i, pawn in enumerate(line):
                if (pawn and
                        pawn[0].value == player and
                        len(list(get_moves(field, (i, j)))) > 0):
                    yield (i, j)


def make_move(field, first, second, sound):
    """
    Function that makes move and returns new field.
    :param field: list
    :param first: [x, y]
    :param second: [x, y]
    :param sound: bool
    :return: list
    """
    field[second[1]][second[0]] = field[first[1]][first[0]]
    field[first[1]][first[0]] = None
    make_queen(field, second, sound)
    pawn_to_delete = get_pawn_to_delete(field, first, second)
    if pawn_to_delete:
        field[pawn_to_delete[1]][pawn_to_delete[0]] = None
    return field
