import unittest
import saver
import core


class TestClass(unittest.TestCase):
    @staticmethod
    def load_identity():
        field = list()
        player = True
        for x in range(4):
            field.append([])
            for y in range(10):
                field[x].append(None if x % 2 == y % 2 else (core.Checker.black, False))
        for _ in range(2):
            field.append([None, None, None, None, None,
                          None, None, None, None, None])
        for x in range(6, 10):
            field.append([])
            for y in range(10):
                field[x].append(None if x % 2 == y % 2 else (core.Checker.white, False))
        return field, player
    
    @staticmethod
    def load_queen():
        field = list()
        for _ in range(10):
            field.append([None, None, None, None, None,
                         None, None, None, None, None])
        field[1][2] = (core.Checker.white, True)
        field[3][4] = (core.Checker.black, False)
        return field, True
    
    def test_saver(self):
        field, player = self.load_identity()
        string = saver.save(field, player)
        field2, player2 = saver.load(string)
        self.assertEqual((field, player), (field2, player2))
    
    def test_core(self):
        field, player = self.load_identity()
        self.assertEqual(list(core.moving_pawns(field, player)), 
                         [(1, 6), (3, 6), (5, 6), (7, 6), (9, 6)])
        self.assertEqual(core.binding_pawns(field, player), [])
        field, player = self.load_queen()
        self.assertEqual(core.get_moves(field, (2, 1)), [(5, 4), (6, 5), (7, 6), (8, 7), (9, 8)])
        self.assertEqual(list(core.get_moves(field, (4, 3))), [(5, 4), (3, 4)])
        core.make_move(field, (2, 1), (5, 4), False)
        field2, player2 = self.load_queen()
        field2[1][2] = None
        field2[3][4] = None
        field2[4][5] = (core.Checker.white, True)
        self.assertEqual(field, field2)


if __name__ == '__main__':
    unittest.main()
