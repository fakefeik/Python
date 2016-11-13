"""
Module for checkers game
"""
import core
import ai
import saver
from client import Client


class Game(object):
    """
    Main game class
    """
    def __init__(self, mode=core.Mode.two_players, this_player=True,
                 difficulty=core.Difficulty.medium, address=None,
                 is_server=False):
        self.field = self.get_default_field()
        self.mode = mode
        self.difficulty = difficulty
        self.player = this_player
        self.previous_player = not this_player
        self.win = (False, False)
        if self.mode == core.Mode.computer:
            self.ai = ai.AI(not this_player, self.difficulty)
        if self.mode == core.Mode.online:
            self.client = Client(address, is_server, this_player)
            if self.client.forced_player:
                self.player = self.client.bool_player
                self.previous_player = not self.player

    @staticmethod
    def get_default_field():
        """
        Method for initializing field
        :return: list
        """
        field = list()
        for col in range(4):
            field.append([])
            for row in range(10):
                field[col].append(None if col % 2 == row % 2 else
                                  (core.Checker.black, False))
        for col in range(2):
            field.append([None, None, None, None, None,
                          None, None, None, None, None])
        for col in range(6, 10):
            field.append([])
            for row in range(10):
                field[col].append(None if col % 2 == row % 2 else
                                  (core.Checker.white, False))
        return field

    def make_ai_move(self, first_player):
        """
        Method for making AI move
        :param first_player: bool
        """
        if first_player:
            self.ai.make_move(self.field)
        else:
            self.field = self.ai.make_move(self.field)
            if not self.field:
                self.win = (True, not self.ai.player)
            self.player = not self.player
            self.previous_player = not self.player

    def make_multiplayer_move(self, first_player):
        """
        Method for making multiplayer move
        :param first_player: bool
        """
        if first_player:
            while not self.client.received:
                pass
            self.field, self.player = saver.load(self.client.recv_str)
        else:
            data = saver.save(self.field, self.player)
            self.client.send(data)
            while not self.client.received:
                pass
            self.field, self.player = saver.load(self.client.recv_str)
            self.previous_player = not self.player
        self.client.recv_str = ''
        self.client.received = False

    def make_move(self, first, second):
        """
        Main method for making moves
        :param first: [x, y]
        :param second: [x, y]
        """
        binding = len(list(core.get_binding_moves(self.field, first)))
        self.field[second[1]][second[0]] = self.field[first[1]][first[0]]
        self.field[first[1]][first[0]] = None
        pawn_to_delete = core.get_pawn_to_delete(self.field, first, second)
        if pawn_to_delete:
            self.field[pawn_to_delete[1]][pawn_to_delete[0]] = None
        if (binding == 0 or
                len(list(core.get_binding_moves(self.field, second))) == 0):
            self.player = not self.player
            self.previous_player = not self.player
        else:
            self.previous_player = self.player
        core.make_queen(self.field, second, True)
