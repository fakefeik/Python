import tkinter
import game
import os
from PIL import Image, ImageTk


class Graphics:
    def __init__(self, map_file, config, images, animated, speed, leaderboard):
        self.main_menu = True
        self.help = False
        self.animated = animated
        self.speed = speed
        self.leaderboard = leaderboard
        self.player_choice = False
        self.root = tkinter.Tk()
        self.canvas = tkinter.Canvas()
        self.images = self.initialize_textures(images)
        self.image_size = self.images["wall"].width()
        self.tick_counter = 0
        self.game = game.Game(map_file, config, leaderboard)
        self.map = self.game.initialize_map()
        self.root.resizable(width=False, height=False)
        self.canvas.configure(width=len(self.map[0])*self.image_size,
                              height=len(self.map)*self.image_size+50,
                              background='black')
        self.root.bind('<Key>', self.on_key_down)
        self.draw_main_menu()
        self.canvas.pack()
        self.root.title('Pacman')
        self.root.wm_iconbitmap('Pacman.ico')
        self.root.mainloop()

    @staticmethod
    def path_to_texture(path, images):
        image = Image.open(images + "/" + path)
        return ImageTk.PhotoImage(image)

    def initialize_textures(self, images):
        files = [f for f in os.listdir(images)]
        dictionary = {file[:-4]: self.path_to_texture(file, images) for file in files}
        return dictionary

    def draw_player_choice(self):
        self.player_choice = True
        self.canvas.delete("all")
        self.canvas.create_text(len(self.map[0])*self.image_size/2 - 100,
                                len(self.map)*self.image_size/2 + 50,
                                font=("Impact", 28),
                                text="Choose player number [1 or 2].",
                                fill="white",
                                tags=("text", "all"))

    def draw_main_menu(self):
        if self.main_menu:
            self.canvas.create_image(len(self.map[0])*self.image_size/2,
                                     250,
                                     image=self.images["pacman_logo"],
                                     tags=("all", ))
            self.canvas.create_text(len(self.map[0])*self.image_size/2 - 100,
                                    len(self.map)*self.image_size/2 + 50,
                                    font=("Impact", 28),
                                    text="T for two players.",
                                    fill="white",
                                    tags=("text", "all"))
            self.canvas.create_text(len(self.map[0])*self.image_size/2 - 100,
                                    len(self.map)*self.image_size/2 + 100,
                                    font=("Impact", 28),
                                    text="M for multiplayer.",
                                    fill="white",
                                    tags=("text", "all"))
            self.canvas.create_text(len(self.map[0])*self.image_size/2,
                                    len(self.map)*self.image_size/2,
                                    font=("Impact", 36),
                                    text="Press Enter for new game.",
                                    fill="white",
                                    tags=("text", "all"))
            if self.leaderboard != "":
                self.canvas.create_text(len(self.map[0])*self.image_size/2,
                                        len(self.map)*self.image_size/2 + 170,
                                        font=("Impact", 24),
                                        text="High Score: {}".format(self.game.max_score),
                                        fill="white",
                                        tags=("text", "all"))

    def draw_help(self):
        text = """
            This is a Pac-Man game.
            You can move Pac-Man using arrow keys.
            Press Escape to pause the game.
            Press Backspace to spawn more monsters :D
        """
        self.canvas.create_text(len(self.map[0])*self.image_size/2,
                                len(self.map)*self.image_size/2 + 100,
                                font=("Impact", 24),
                                text=text,
                                fill="white",
                                tags=("text", "all"))

    def redraw(self):
        self.canvas.delete("all")
        if self.help:
            self.draw_help()
            return
        if self.game.end_game_loose:
            self.canvas.create_text(len(self.map[0])*self.image_size/2,
                                    len(self.map)*self.image_size/2,
                                    font=("Impact", 72),
                                    text="ПОТРАЧЕНО",
                                    fill="white",
                                    tags=("text", "all"))
            self.canvas.create_text(len(self.map[0])*self.image_size/2,
                                    len(self.map)*self.image_size/2 + 100,
                                    font=("Impact", 24),
                                    text="Press Enter for new game.",
                                    fill="white",
                                    tags=("text", "all"))
            self.game.pause = False
            return

        if self.game.end_game_win:
            if max(self.game.scores) > self.game.max_score and self.leaderboard != "":
                with open(self.leaderboard, 'w') as f:
                    f.write(str(self.game.scores))
            self.canvas.create_text(len(self.map[0])*self.image_size/2,
                                    len(self.map)*self.image_size/2,
                                    font=("Impact", 72),
                                    text="WIN",
                                    fill="white",
                                    tags=("text", "all"))
            self.canvas.create_text(len(self.map[0])*self.image_size/2,
                                    len(self.map)*self.image_size/2 + 100,
                                    font=("Impact", 24),
                                    text="Press Enter for new game.",
                                    fill="white",
                                    tags=("text", "all"))
            self.canvas.create_text(len(self.map[0])*self.image_size/2,
                                    len(self.map)*self.image_size/2 + 150,
                                    font=("Impact", 36),
                                    text="Score: {}".format(self.game.scores),
                                    fill="white",
                                    tags=("text", "all"))
            if self.leaderboard != "":
                self.canvas.create_text(len(self.map[0])*self.image_size/2,
                                        len(self.map)*self.image_size/2 + 200,
                                        font=("Impact", 36),
                                        text="High score: {}".format(self.game.max_score),
                                        fill="white",
                                        tags=("text", "all"))
            self.game.pause = False
            return

        for y in range(len(self.map)):
            for x in range(len(self.map[0])):
                if not self.animated:
                    self.canvas.create_image(x * self.image_size + self.image_size/2,
                                             y * self.image_size + self.image_size/2,
                                             image=self.images[self.map[y][x].texture],
                                             tags=("all", ))
                elif not self.map[y][x].animated:
                    self.canvas.create_image(x * self.image_size + self.image_size/2,
                                             y * self.image_size + self.image_size/2,
                                             image=self.images[self.map[y][x].texture],
                                             tags=("all", ))
        if self.animated:
            for y in range(len(self.map)):
                for x in range(len(self.map[0])):
                    if self.map[y][x].animated:
                        location = self.map[y][x].location
                        delta = self.map[y][x].delta
                        next_texture = self.map[y][x].texture + str(self.tick_counter % self.map[y][x].texture_count)
                        if next_texture in self.images.keys():
                            image = self.images[next_texture]
                        else:
                            image = self.images[self.map[y][x].texture]

                        if 0 < x + delta.x < len(self.map[0]):
                            if not self.map[y + delta.y][x + delta.x].animated:
                                self.canvas.create_image(self.image_size*(location.x + delta.x + 1/2),
                                                         self.image_size*(location.y + delta.y + 1/2),
                                                         image=self.images[self.map[y][x].previous_texture],
                                                         tags=("all", ))
                        self.canvas.create_image(self.image_size * (location.x + 1/2) + self.tick_counter * delta.x * 4,
                                                 self.image_size * (location.y + 1/2) + self.tick_counter * delta.y * 4,
                                                 image=image,
                                                 tags=("all", ))

        self.canvas.create_text(self.image_size/2,
                                len(self.map)*self.image_size+20,
                                anchor=tkinter.W,
                                font=("Impact", 36),
                                text="Score: {}".format(self.game.scores[0]),
                                fill="white",
                                tags=("text", "all"))
        if len(self.game.scores) > 1:
            self.canvas.create_text(self.image_size * len(self.map[0]) - 20,
                                    len(self.map)*self.image_size+20,
                                    anchor=tkinter.E,
                                    font=("Impact", 36),
                                    text="Score: {}".format(self.game.scores[1]),
                                    fill="white",
                                    tags=("text", "all"))
        if self.game.pause:
            self.canvas.create_text(len(self.map[0])*self.image_size/2,
                                    len(self.map)*self.image_size/2,
                                    font=("Impact", 72),
                                    text="PAUSE",
                                    fill="white",
                                    tags=("text", "all"))

    def timer_tick(self):
        if not self.game.pause and not self.help:
            self.tick_counter += 1
        self.redraw()
        if not self.game.end_game_loose and not self.game.end_game_win and \
           not self.game.pause and not self.help and self.tick_counter > self.speed:
            self.map = self.game.move()
            self.tick_counter = 0
        self.root.after(10, self.timer_tick)

    def on_key_down(self, event):
        if not self.game.pause:
            if self.game.pacman_objects[self.game.player_id]:
                if event.keysym == "a":
                    self.game.change_direction(0, self.game.player_id)
                if event.keysym == "d":
                    self.game.change_direction(1, self.game.player_id)
                if event.keysym == "w":
                    self.game.change_direction(2, self.game.player_id)
                if event.keysym == "s":
                    self.game.change_direction(3, self.game.player_id)

            if self.game.mode == game.Mode.TwoPlayers and self.game.pacman_objects[1]:
                if event.keysym == "Left":
                    self.game.change_direction(0, 1)
                if event.keysym == "Right":
                    self.game.change_direction(1, 1)
                if event.keysym == "Up":
                    self.game.change_direction(2, 1)
                if event.keysym == "Down":
                    self.game.change_direction(3, 1)

        if event.keysym == "Return" and (self.game.end_game_win or self.game.end_game_loose):
            self.map = self.game.initialize_map()
            self.game.end_game_loose = False
            self.game.end_game_win = False
        if self.main_menu:
            if self.player_choice:
                if event.keysym == "1":
                    self.game = game.Game("configs/mapmult.txt",
                                          "configs/mapconfig.txt",
                                          self.game.leaderboard,
                                          game.Mode.Multiplayer, 0)
                    self.map = self.game.initialize_map()
                    self.timer_tick()
                    self.main_menu = not self.main_menu
                if event.keysym == "2":
                    self.game = game.Game("configs/mapmult.txt",
                                          "configs/mapconfig.txt",
                                          self.game.leaderboard,
                                          game.Mode.Multiplayer, 1)
                    self.map = self.game.initialize_map()
                    self.timer_tick()
                    self.main_menu = not self.main_menu
            if event.keysym == "Return":
                self.timer_tick()
                self.main_menu = not self.main_menu
            if event.keysym == "t":
                self.game = game.Game("configs/mapmult.txt",
                                      "configs/mapconfig.txt",
                                      self.game.leaderboard,
                                      game.Mode.TwoPlayers)
                self.map = self.game.initialize_map()
                self.timer_tick()
                self.main_menu = not self.main_menu
            if event.keysym == "m":
                self.draw_player_choice()
        if event.keysym == "BackSpace":
            self.map = self.game.spawn_more_monsters()
        if event.keysym == "Escape" and not self.game.end_game_loose and not self.game.end_game_win:
            self.game.pause = not self.game.pause
        if event.keysym == "F1":
            self.help = not self.help
