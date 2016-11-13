import random
import winsound
import enum
import threading


class Mode(enum.Enum):
    Single = 1,
    TwoPlayers = 2,
    Multiplayer = 3


class Animation:
    def __init__(self, animated, delta, location, texture, previous_texture="empty", texture_count=2):
        self.texture = texture
        self.previous_texture = previous_texture
        self.animated = animated
        self.delta = delta
        self.location = location
        self.texture_count = texture_count


class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return "Point ({}, {})".format(self.x, self.y)


class Monster:
    def __init__(self, location, name, current_name, direction=2, previous="empty"):
        self.location = location
        self.name = name
        self.current_name = current_name
        self.direction = direction
        self.previous = previous


class Pacman:
    def __init__(self, location, direction=0, next_direction=0, previous="empty"):
        self.location = location
        self.direction = direction
        self.next_direction = next_direction
        self.previous = previous


class Game:
    def __init__(self, map_file, config, leaderboard, mode=Mode.Single, player_id=0):
        self.player_id = player_id
        self.mode = mode
        self.leaderboard = leaderboard
        if self.mode == Mode.Multiplayer:
            threading.Thread(target=self.messages_thread).start()
        if self.leaderboard != "":
            with open(self.leaderboard, encoding='cp1251') as f:
                self.max_score = int(f.read())
        with open(map_file, encoding='cp1251') as f:
            self.map_lines = f.read().split('\n')
        with open(config, encoding='cp1251') as f:
            self.char_to_string = {line[0]: line[2:-1] for line in f.readlines()}
        self.map = []
        self.monsters = []
        self.fruits = []
        self.pacman_objects = []
        self.scores = [0]
        self.pacmans_dead = 0
        self.pacmans_num = 1
        self.end_game_loose = False
        self.end_game_win = False
        self.pause = False
        self.tick_counter = 0
        self.client = None
        self.global_timer = 0
        self.multiplyers = [1, 1]
        self.ghosts = False
        self.monster_types = ("blinky", "pinky", "inky", "clyde")
        self.directions = (Point(-1, 0), Point(1, 0), Point(0, -1), Point(0, 1))

    def messages_thread(self):
        self.client = __import__("client")
        while True:
            self.change_direction(int(self.client.receive()), 1 if self.player_id == 0 else 0)

    def in_field(self, x, y):
        return 0 <= x < len(self.map[0]) and 0 <= y < len(self.map)

    def can_move_monster(self, x, y):
        return (self.in_field(x, y) and "wall" not in self.map[y][x].texture and
                self.map[y][x].texture not in self.monster_types)

    def can_move(self, x, y):
        return (self.in_field(x, y) and "pacman" not in self.map[y][x].texture and
                "wall" not in self.map[y][x].texture and self.map[y][x].texture not in self.monster_types)

    def initialize_map(self):
        self.map = []
        self.monsters = []
        self.pacman_objects = []
        self.global_timer = 0
        self.pacmans_dead = 0
        self.scores = [0]
        for i, line in enumerate(self.map_lines):
            map_line = []
            for j, char in enumerate(line):
                if char == 'P':
                    self.pacman_objects.append(Pacman(Point(j, i), 1, 1))
                    map_line.append(Animation(True, Point(0, 0), Point(j, i),
                                              self.char_to_string[char],
                                              texture_count=4))
                elif char == 'p':
                    self.pacman_objects.append(Pacman(Point(j, i), 0, 0))
                    map_line.append(Animation(True, Point(0, 0), Point(j, i),
                                              self.char_to_string[char],
                                              texture_count=4))
                elif self.char_to_string[char] in self.monster_types:
                    self.monsters.append(Monster(Point(j, i),
                                                 self.char_to_string[char],
                                                 self.char_to_string[char]))
                    map_line.append(Animation(True, Point(0, 0), Point(j, i),
                                              self.char_to_string[char]))
                else:
                    map_line.append(Animation(False, Point(0, 0), Point(j, i),
                                              self.char_to_string[char]))
            self.map.append(map_line)
        if len(self.pacman_objects) > 1:
            self.pacman_objects[1].is_alive = False

        if len(self.pacman_objects) > 1:
            self.scores.append(0)
            self.pacmans_num = len(self.pacman_objects)
        return self.map

    def remove_kebab(self, point):
        for i, pacman in enumerate(self.pacman_objects):
            if pacman:
                if pacman.location == point:
                    self.map[point.y][point.x] = Animation(False, Point(0, 0), Point(0, 0), "empty")
                    self.pacman_objects[i] = None
                for direct in self.directions:
                    if pacman.location == Point(point.x + direct.x, point.y + direct.y):
                        self.map[point.y + direct.y][point.x + direct.x] = Animation(False,
                                                                                     Point(0, 0),
                                                                                     Point(0, 0),
                                                                                     "empty")
                        self.pacman_objects[i] = None

    def spawn_more_monsters(self):
        for i, line in enumerate(self.map_lines):
            for j, char in enumerate(line):
                if self.char_to_string[char] in self.monster_types:
                    self.monsters.append(Monster(Point(j, i),
                                                 self.char_to_string[char],
                                                 self.char_to_string[char]))
                    self.map[i][j] = Animation(True, Point(0, 0), Point(j, i),
                                               self.char_to_string[char])
        return self.map

    def change_direction(self, direction, number):
        if self.player_id == number and self.mode == Mode.Multiplayer:
            self.client.send(str(direction))
        self.pacman_objects[number].next_direction = direction

    def try_move_monster(self, monster, dx, dy):
        if monster.location.x + dx == -1:
            self.map[monster.location.y][monster.location.x] = Animation(False,
                                                                         Point(0, 0),
                                                                         Point(0, 0),
                                                                         monster.previous)
            monster.location.x = len(self.map[0]) - 1

        if monster.location.x + dx == len(self.map[0]):
            self.map[monster.location.y][monster.location.x] = Animation(False,
                                                                         Point(0, 0),
                                                                         Point(0, 0),
                                                                         monster.previous)
            monster.location.x = 0

        if (self.can_move_monster(monster.location.x + dx, monster.location.y + dy) and
            self.map[monster.location.y + dy][monster.location.x + dx].texture != "ghost" and
                (monster.current_name != "ghost" or monster.current_name == "ghost" and
                    "pacman" not in self.map[monster.location.y + dy][monster.location.x + dx].texture)):
            if "pacman" in monster.previous and monster.current_name != "ghost":
                self.remove_kebab(monster.location)
                monster.previous = "empty"
                self.pacmans_dead += 1
                if self.pacmans_num == self.pacmans_dead:
                    self.end_game_loose = True

            self.map[monster.location.y][monster.location.x] = Animation(False,
                                                                         Point(0, 0),
                                                                         Point(0, 0),
                                                                         monster.previous)

            monster.previous = self.map[monster.location.y + dy][monster.location.x + dx].texture

            self.map[monster.location.y + dy][monster.location.x + dx] = \
                Animation(True, Point(dx, dy),
                          Point(monster.location.x, monster.location.y),
                          monster.current_name, monster.previous)

            monster.location = Point(monster.location.x + dx, monster.location.y + dy)
        else:
            monster.direction = random.randrange(0, 4)
            self.map[monster.location.y][monster.location.x].animated = False

    def move_monster(self, monster):
        self.try_move_monster(monster,
                              self.directions[monster.direction].x,
                              self.directions[monster.direction].y)

    def move_monsters(self):
        for monster in self.monsters:
            self.move_monster(monster)

    def monsters_to_ghosts(self):
        for monster in self.monsters:
            monster.current_name = "ghost"

    def try_move_pacman(self, pacman, dx, dy, i):
        contains_dots = False
        for line in self.map:
            for animation in line:
                if animation.texture == "dot":
                    contains_dots = True
        self.end_game_win = not contains_dots
        if pacman.location.x + dx == -1:
            self.map[pacman.location.y][pacman.location.x] = Animation(False,
                                                                       Point(0, 0),
                                                                       Point(0, 0),
                                                                       pacman.previous)
            pacman.location.x = len(self.map[0]) - 1

        if pacman.location.x + dx == len(self.map[0]):
            self.map[pacman.location.y][pacman.location.x] = Animation(False,
                                                                       Point(0, 0),
                                                                       Point(0, 0),
                                                                       pacman.previous)
            pacman.location.x = 0

        if self.can_move(pacman.location.x + dx, pacman.location.y + dy):
            delta_x = pacman.location.x + dx
            delta_y = pacman.location.y + dy
            if self.map[delta_y][delta_x].texture == "dot":
                self.scores[i] += 10
                winsound.PlaySound("sounds/loop.wav", winsound.SND_ASYNC)
            if self.map[delta_y][delta_x].texture == "fruit":
                self.scores[i] += 25
            if self.map[delta_y][delta_x].texture == "big_dot":
                self.scores[i] += 50
                self.monsters_to_ghosts()
                self.ghosts = True
                self.tick_counter = 0
            if self.map[delta_y][delta_x].texture == "ghost":
                self.scores[i] += 200 * self.multiplyers[i]
                self.multiplyers[i] *= 2
                for monster in self.monsters:
                    if monster.location.x == delta_x and monster.location.y == delta_y:
                        monster.location = Point(14, 14)
                        monster.current_name = monster.name
                        monster.previous = "empty"
                        monster.direction = 2

            if pacman.previous != "line":
                pacman.previous = "empty"

            self.map[pacman.location.y][pacman.location.x] = Animation(False,
                                                                       Point(0, 0),
                                                                       Point(0, 0),
                                                                       pacman.previous)

            pacman.previous = self.map[delta_y][delta_x].texture

            self.map[delta_y][delta_x].animated = True
            self.map[delta_y][delta_x].delta = Point(dx, dy)
            self.map[delta_y][delta_x].texture_count = 4
            self.map[delta_y][delta_x].previous_texture = pacman.previous

            self.map[delta_y][delta_x].location = Point(pacman.location.x, pacman.location.y)

            if dx == -1:
                self.map[delta_y][delta_x].texture = "pacman_left"
            if dx == 1:
                self.map[delta_y][delta_x].texture = "pacman_right"
            if dy == -1:
                self.map[delta_y][delta_x].texture = "pacman_up"
            if dy == 1:
                self.map[delta_y][delta_x].texture = "pacman_down"

            pacman.location.x += dx
            pacman.location.y += dy
        else:
            self.map[pacman.location.y][pacman.location.x].animated = False

    def move_pacman(self):
        for i, pacman_object in enumerate(self.pacman_objects):
            if pacman_object:
                if self.can_move(pacman_object.location.x + self.directions[pacman_object.next_direction].x,
                                 pacman_object.location.y + self.directions[pacman_object.next_direction].y):
                    pacman_object.direction = pacman_object.next_direction
                self.try_move_pacman(pacman_object, self.directions[pacman_object.direction].x,
                                     self.directions[pacman_object.direction].y, i)

    def check_ghosts(self):
        if self.ghosts:
            self.tick_counter += 1
        if self.tick_counter > 100:
            self.tick_counter = 0
            self.multiplyers = [1, 1]
            self.ghosts = False
            for monster in self.monsters:
                monster.current_name = monster.name

    def check_fruits(self):
        for fruit in self.fruits:
            if (self.global_timer - fruit[1] >= 100 and
                    not "pacman" in self.map[fruit[0].y][fruit[0].x].texture):
                self.map[fruit[0].y][fruit[0].x].texture = "empty"
                self.fruits.pop()

    def spawn_fruit(self):
        empty = []
        for y in range(len(self.map)):
            for x in range(len(self.map[0])):
                if self.map[y][x].texture == "empty":
                    empty.append(Point(x, y))
        if len(empty) != 0:
            spawn_point = empty[random.randrange(0, len(empty))]
            self.map[spawn_point.y][spawn_point.x].texture = "fruit"
            self.fruits.append((Point(spawn_point.x, spawn_point.y), self.global_timer))

    def move(self):
        self.global_timer += 1
        self.move_pacman()
        self.move_monsters()
        self.check_ghosts()
        self.check_fruits()
        if self.global_timer % 500 == 0:
            self.spawn_fruit()
        return self.map
