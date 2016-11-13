"""
Module for artificial intelligence
"""
import core
import random
import copy


class AI(object):
    """
    Class for Artificial Intelligence
    """
    def __init__(self, player, difficulty):
        self.player = player
        self.difficulty = difficulty
        self.max = 10**10

    def make_move(self, field):
        """
        Makes AI move depending on current difficulty
        :param field: list
        :return list
        """
        if self.difficulty == core.Difficulty.easy:
            return self._random_turn(field)
        elif self.difficulty == core.Difficulty.medium:
            return self._one_move_prediction(field)
        else:
            return self._mini_max(field)

    def _one_move_prediction(self, field):
        """
        AI method that makes move looking one step ahead
        :param field: list
        :return list
        """
        moves = [[x, 0] for x in
                 core.get_all_possible_moves(field, self.player)]
        if len(moves) == 0:
            return
        for i in range(len(moves)):
            maximum = self.max
            temp_field = copy.deepcopy(field)
            for move in moves[i][0]:
                temp_field = core.make_move(temp_field, move[0],
                                            move[1], False)
            for move in core.get_all_possible_moves(temp_field,
                                                    not self.player):
                temp = copy.deepcopy(temp_field)
                for mov in move:
                    temp = core.make_move(temp, mov[0], mov[1], False)
                heuristics = self._simple_heuristics(temp)
                if heuristics < maximum:
                    maximum = heuristics
            moves[i][1] = maximum
        moves = sorted(moves, key=lambda x: -x[1])[0][0]
        for move in moves:
            field = core.make_move(field, move[0], move[1], True)
        return field

    def _random_turn(self, field):
        """
        Makes a completely random turn
        :param field: list
        :return list
        """
        pawns = []
        for j, line in enumerate(field):
            for i, pawn in enumerate(line):
                if pawn:
                    if pawn[0].value == self.player:
                        pawns.append((i, j))
        moves = []
        for pawn in pawns:
            if (len(core.binding_pawns(field, self.player)) > 0 and
                    (pawn[0], pawn[1]) in core.binding_pawns(field, self.player)
                    or len(list(core.get_moves(field, pawn))) > 0
                    and len(core.binding_pawns(field, self.player)) == 0):
                moves.append((pawn, list(core.get_moves(field, pawn))))
        if len(moves) == 0:
            return
        move = random.choice(moves)
        move_from = move[0]
        binding = move_from in core.binding_pawns(field, self.player)

        move_to = random.choice(list(move[1]))
        field = core.make_move(field, move_from, move_to, True)
        while move_to in core.binding_pawns(field, self.player) and binding:
            move_from = move_to
            move_to = random.choice(core.get_moves(field, move_from))
            field = core.make_move(field, move_from,
                                   random.choice(core.get_moves(field,
                                                                move_from)),
                                   True)
        return field

    def _simple_heuristics(self, field):
        """
        Computes heuristics of a given field
        :param field: list
        :return int
        """
        delta = 0
        for line in field:
            for pawn in line:
                if pawn:
                    if pawn[0].value == self.player:
                        delta += 1
                        if pawn[1]:
                            delta += 4
                    else:
                        delta -= 1
                        if pawn[1]:
                            delta -= 4
        return delta

    @staticmethod
    def _get_adjacent_fields(field, player):
        """
        Method to get all adjacent fields
        :return generator
        """
        for moves in core.get_all_possible_moves_advanced(field, player):
            for move in moves:
                temp = copy.deepcopy(field)
                temp = core.make_move(temp, move[0], move[1], False)
                yield temp

    def _mini_max_algorithm(self, field, depth, maximizing_player):
        """
        Recursive mini-max algorithm
        :param field: list
        :param depth: int
        :param maximizing_player: bool
        """
        if depth == 0:
            return self._simple_heuristics(field)
        if maximizing_player:
            best_value = -self.max
            for child in self._get_adjacent_fields(field, self.player):
                best_value = max(best_value,
                                 self._mini_max_algorithm(child,
                                                          depth - 1,
                                                          False))
            return best_value
        else:
            best_value = self.max
            for child in self._get_adjacent_fields(field, not self.player):
                best_value = min(best_value,
                                 self._mini_max_algorithm(child,
                                                          depth - 1,
                                                          True))
            return best_value

    def _mini_max(self, field):
        """
        Realization of a mini-max algorithm
        :param field: list
        """
        moves = [[x, 0] for x in
                 core.get_all_possible_moves_advanced(field, self.player)]
        if len(moves) == 0:
            return
        for i in range(len(moves)):
            temp = copy.deepcopy(field)
            for move in moves[i][0]:
                core.make_move(temp, move[0], move[1], False)
            moves[i][1] = self._mini_max_algorithm(temp, 3, self.player)
        if len(moves) > 0:
            moves = sorted(moves, key=lambda x: -x[1])[0][0]
            for move in moves:
                field = core.make_move(field, move[0], move[1], True)
        return field
