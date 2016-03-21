import time
import itertools
from collections import Counter


def euler73():
    d = 12000
    a = 1 / 3
    b = 1 / 2
    fractions = set()
    for i in range(1, d + 1):
        for j in range(1, i - 1):
            if a < j / i < b:
                fractions.add(j / i)
    print(len(fractions))


def arrives_at_89(n):
    s = sum(map(lambda x: x ** 2, map(int, str(n))))

    if s == 89:
        return True
    elif s == 1:
        return False

    return arrives_at_89(s)


def euler92():
    n = 10000000
    print(len([x for x in range(1, n) if arrives_at_89(x)]))


class Generator:
    _functions = {
        3: lambda x: x * (x + 1) // 2,
        4: lambda x: x ** 2,
        5: lambda x: x * (3 * x - 1) // 2,
        6: lambda x: x * (2 * x - 1),
        7: lambda x: x * (5 * x - 3) // 2,
        8: lambda x: x * (3 * x - 2)
    }

    def __init__(self, n, left=1000, right=9999):
        self.n = n
        self.left = left
        self.right = right
        self.index = 0
        while self._functions[n](self.index) < left:
            self.index += 1

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        value = self._functions[self.n](self.index)
        if value > self.right:
            raise StopIteration
        self.index += 1
        return value


def is_cyclic(a, b):
    return str(a)[2:] == str(b)[:2]


def get_chain(perm, lists):
    e = [[[x] for x in lists[perm[0]]]]
    for i, p in enumerate(perm):
        if i == 0:
            continue
        e.append([])
        for elem in e[i - 1]:
            l = [elem + [x] for x in lists[p] if is_cyclic(elem[-1], x) and x not in elem]
            if len(l) != 0:
                e[i] += l
    res = list(filter(lambda x: is_cyclic(x[-1], x[0]), e[5]))
    if len(res) != 0:
        return res[0]


def euler61():
    lists = {}
    r = range(3, 9)
    for i in r:
        lists[i] = list(Generator(i))
    for i, perm in enumerate(itertools.permutations(r)):
        chain = get_chain(perm, lists)
        if chain:
            print(chain)
            print(sum(chain))
            break


def euler59():
    with open("p059_cipher.txt") as f:
        cipher_bytes = bytes(map(int, f.read().split(',')))

    key_length = 3
    key_chars = map(chr, range(97, 123))

    perms = itertools.permutations(key_chars, key_length)
    common_words = {" the ", "The ", " for ", "For "}
    for perm in perms:
        decoded_bytes = bytearray()
        for i, byte in enumerate(cipher_bytes):
            decoded_bytes.append(ord(perm[i % len(perm)]) ^ byte)
        try:
            decoded = decoded_bytes.decode('utf-8')
            if len(list(filter(lambda x: x in decoded, common_words))) != 0:
                print(''.join(perm))
                print(decoded)
                print(sum(map(ord, decoded)))
        except Exception:
            pass


values = {r: i for i, r in enumerate('23456789TJQKA', start=2)}
straights = [(v, v - 1, v - 2, v - 3, v - 4) for v in range(14, 5, -1)] + [(14, 5, 4, 3, 2)]
ranks = [(1, 1, 1, 1, 1), (2, 1, 1, 1), (2, 2, 1), (3, 1, 1), (), (), (3, 2), (4, 1)]


def hand_rank(hand):
    score = list(zip(*sorted(((v, values[k]) for k, v in Counter(x[0] for x in hand).items()), reverse=True)))
    score[0] = ranks.index(score[0])
    if len(set(card[1] for card in hand)) == 1:
        score[0] = 5
    if score[1] in straights: score[0] = 8 if score[0] == 5 else 4
    return score


def euler54():
    with open("p054_poker.txt") as f:
        lines = f.readlines()
    print(sum(hand_rank(hand[:5]) > hand_rank(hand[5:]) for hand in (line.split() for line in lines)))


def main():
    euler92()

if __name__ == "__main__":
    main()
