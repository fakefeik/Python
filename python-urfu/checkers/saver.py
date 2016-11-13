"""
Serialization module
"""
import math
import core


def save(field, player):
    """
    Saves field and current player to string
    :param field: list
    :param player: bool
    :return: str
    """
    string = ''
    for line in field:
        for pawn in line:
            if pawn:
                color = '1' if pawn[0] == core.Checker.white else '0'
                is_queen = '1' if pawn[1] else '0'
                pwn = '1' + color + is_queen
            else:
                pwn = '000'
            string += pwn
    string += '1' if player else '0'
    return string


def load(string_to_decode):
    """
    Method to load field and current player from string
    :param string_to_decode: str
    :return: (list, bool)
    """
    field = []
    for i in range(10):
        field.append([])
        for _ in range(10):
            field[i].append(None)
    string = ''

    for i, bit in enumerate(string_to_decode):
        string += bit
        if (i + 1) % 3 == 0:
            j = (i + 1) / 3 - 1
            if string[0] == '1':
                color = core.Checker.white if string[1] == '1' else core.Checker.black
                is_queen = True if string[2] == '1' else False
                field[math.floor(j / 10)][math.floor(j % 10)] = (color, is_queen)
            string = ''
    player = True if string == '1' else False
    return field, player
