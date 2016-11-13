"""
Graphics module
"""
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import threading
import math
import game
import saver
import core
import time


class StatusBar(tkinter.Frame):
    """
    StatusBar class
    """
    def __init__(self, master, text=''):
        tkinter.Frame.__init__(self, master)
        self.text = tkinter.StringVar()
        self.label = tkinter.Label(self, textvariable=self.text,
                                   font=('arial', 12, 'normal'))
        self.text.set(text)
        self.label.pack(fill=tkinter.X)
        self.pack(side=tkinter.BOTTOM, anchor=tkinter.W)

    def set_text(self, text):
        """
        Sets status bar text
        """
        self.text.set(text)

    def clear(self):
        """
        Clears status bar
        """
        self.text.set('')

    def __str__(self):
        return "Status Bar with text '{}'".format(self.text.get())


class Graphics(object):
    """
    Graphics class
    """
    def __init__(self):
        self.port = None
        self.is_host = None
        self.address = None
        self.top = None
        self.side = None
        self.mult = None

        def get_cell_size(height):
            """
            Returns appropriate cell size for current screen resolution
            """
            return (height - 100) / 11
        self.waiting_for_response = False
        self.mode = core.Mode.two_players
        self.difficulty = core.Difficulty.easy
        self.player = True
        self.root = tkinter.Tk()
        self.menu = tkinter.Menu()
        self.create_menu(tkinter.DISABLED)
        self.canvas = tkinter.Canvas()
        self.game = game.Game()

        self.cell_size = get_cell_size(self.root.winfo_screenheight())
        self.selected = (False, (0, 0))
        self.root.resizable(width=False, height=False)
        self.canvas.configure(width=self.cell_size*10,
                              height=self.cell_size*10)
        self.root.bind('<Button-1>', self.on_mouse_click)
        self.root.bind('<Key>', self.on_key_down)
        self.draw_main()
        self.status_bar = None
        self.canvas.pack()
        self.root.title("Checkers")
        self.root.config(menu=self.menu)
        self.root.protocol('WM_DELETE_WINDOW', self.ask_quit)
        self.root.mainloop()

    @staticmethod
    def ask_quit():
        """
        Asking for exit
        """
        exit_query = "Are you sure you want to quit?"
        do_exit = tkinter.messagebox.askyesno("", exit_query)
        if do_exit:
            quit()

    def draw_main(self):
        """
        Draws main game menu and manages button clicks in it
        """
        def chose_color():
            """
            Redefining buttons for colors
            """
            buttons[0].configure(text="White", command=choose_white)
            buttons[1].configure(text="Black", command=choose_black)
            buttons[2].destroy()

        def choose_black():
            """
            If player chooses to play as black, AI is enabled
            :return:
            """
            self.player = False
            try:
                self.game = game.Game(self.mode, self.player, self.difficulty)
                if self.game.mode == core.Mode.computer:
                    threading.Thread(target=self.make_ai_move_async,
                                     args=(True, ), daemon=True).start()
                else:
                    threading.Thread(target=self.make_multiplayer_move_async,
                                     args=(True, ), daemon=True).start()
            except ConnectionRefusedError:
                print("Cannot connect to the server.")
                self.game = game.Game()
            redraw()

        def choose_white():
            """
            If player chooses to play as white,
            new Game is created with appropriate params
            """
            try:
                self.game = game.Game(self.mode, self.player, self.difficulty)
            except ConnectionRefusedError:
                print("Cannot connect to the server.")
                self.game = game.Game()
            redraw()

        def choose_easy():
            """
            Method for choosing difficulty
            """
            self.difficulty = core.Difficulty.easy
            chose_color()

        def choose_medium():
            """
            Method for choosing difficulty
            """
            self.difficulty = core.Difficulty.medium
            chose_color()

        def choose_hard():
            """
            Method for choosing difficulty
            """
            self.difficulty = core.Difficulty.hard
            chose_color()

        def two_players():
            """
            If two players are chosen,
            save/load gets enabled and the game starts
            """
            self.menu = tkinter.Menu()
            self.create_menu(tkinter.ACTIVE)
            self.root.config(menu=self.menu)
            redraw()

        def computer():
            """
            If computer mode is chosen, you are given the choice of difficulty
            :return:
            """
            self.mode = core.Mode.computer
            buttons[0].configure(text="Easy", command=choose_easy)
            buttons[1].configure(text="Medium", command=choose_medium)
            buttons[2].configure(text="Hard", command=choose_hard)

        def multiplayer():
            """
            If multiplayer mode is chosen,
            you are given the choice of black or white
            :return:
            """

            def on_delete():
                """
                Deleting multiplayer start window
                """
                self.mult = False
                self.top.destroy()

            def on_ok():
                """
                Trying to start multiplayer game
                """
                try:
                    if self.port.get() == '':
                        if self.address.get().find(':') != -1:
                            address = self.address.get().split(':')
                            address[1] = int(address[1])
                            threading.Thread(target=self.start_new_game_async,
                                             args=(self.side.get(), tuple(address), self.is_host.get()),
                                             daemon=True).start()
                            self.top.destroy()
                            redraw()
                    elif self.is_host:
                        address = ('0.0.0.0', int(self.port.get()))
                        threading.Thread(target=self.start_new_game_async,
                                         args=(self.side.get(), address, self.is_host.get()),
                                         daemon=True).start()
                        self.top.destroy()
                        redraw()
                except Exception as e:
                    self.top.destroy()
                    redraw()
                    self.waiting_for_response = True
                    err_msg = "Could not start multiplayer game with given parameters: {}"
                    self.status_bar.set_text(err_msg.format(e))
            if not self.mult:
                self.mult = True
                top = self.top = tkinter.Toplevel(self.root)
                self.top.protocol('WM_DELETE_WINDOW', on_delete)
                tkinter.Label(top, text="Enter address to connect to\nEx: 192.168.1.1:6002").pack()

                self.address = tkinter.Entry(top)
                self.address.pack(padx=10)

                tkinter.Label(top, text="Enter port for other players to connect to, \nif you want to be a host.").pack()

                self.port = tkinter.Entry(top)
                self.port.pack(padx=5)

                self.side = tkinter.BooleanVar()
                rb1 = tkinter.Radiobutton(top, text='White',
                                          variable=self.side, value=True)
                rb2 = tkinter.Radiobutton(top, text='Black',
                                          variable=self.side, value=False)
                rb1.pack()
                rb2.pack()

                self.is_host = tkinter.BooleanVar()
                cb = tkinter.Checkbutton(top, text='Host',
                                         variable=self.is_host)
                cb.pack()

                ok_button = tkinter.Button(top, text="OK", command=on_ok)
                ok_button.pack(pady=5)

        def redraw():
            """
            Once everything is selected, the field and pawns are drawn
            """
            self.draw_field()
            self.draw_pawns(self.game.field)
            for button in buttons:
                button.destroy()
            self.draw_statusbar()

        buttons = []
        buttons.append(tkinter.Button(text="Two players", command=two_players))
        buttons.append(tkinter.Button(text="Computer", command=computer))
        buttons.append(tkinter.Button(text="Multiplayer", command=multiplayer))
        self.mult = False
        for button in buttons:
            button.pack()

    def create_menu(self, state):
        """
        Creates menu with save/load and about sections
        :param state: tkinter.DISABLED or tkinter.ACTIVE
        """
        def file_save():
            """
            Function for saving field to file
            """
            file = tkinter.filedialog.asksaveasfile(mode='w',
                                                    defaultextension=".sav")
            if file:
                file.write(saver.save(self.game.field, self.game.player))
                file.close()

        def file_load():
            """
            Function for loading field from file
            """
            file = tkinter.filedialog.askopenfile()
            if file:
                self.game.field, self.game.player = saver.load(file.read())
                self.draw_pawns(self.game.field)
                file.close()

        def about():
            """
            Shows about message
            """
            tkinter.messagebox.showinfo('Info', 'Checkers')

        filemenu = tkinter.Menu(self.menu, tearoff=0)
        filemenu.add_command(label="New game", command=self.start_new_game)
        filemenu.add_command(label="Load", command=file_load, state=state)
        filemenu.add_command(label="Save", command=file_save, state=state)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        self.menu.add_cascade(label="File", menu=filemenu)

        helpmenu = tkinter.Menu(self.menu, tearoff=0)
        helpmenu.add_command(label="About", command=about)
        self.menu.add_cascade(label="Help", menu=helpmenu)

    def draw_field(self):
        """
        Draws field
        """
        for x in range(10):
            for y in range(10):
                self.canvas.create_rectangle(x*self.cell_size,
                                             y*self.cell_size,
                                             (x + 1) * self.cell_size,
                                             (y + 1) * self.cell_size,
                                             fill='white' if x % 2 == y % 2 else 'grey',
                                             tags=("field", "all"))

    def draw_win(self):
        """
        Once someone has won, this screen is shown
        """
        self.status_bar.destroy()
        self.canvas.delete("all")
        self.canvas.configure(background='white' if self.game.win[1] else 'black')
        self.canvas.create_text(5 * self.cell_size,
                                5 * self.cell_size,
                                font=("Impact", math.floor(self.cell_size)),
                                text='White won' if self.game.win[1] else 'Black won',
                                fill='black' if self.game.win[1] else 'white',
                                tags=("text", "all"))
        self.canvas.create_text(5 * self.cell_size,
                                6 * self.cell_size,
                                font=("Impact", int(math.floor(self.cell_size)/2)),
                                text='Press Enter to start new game',
                                fill='black' if self.game.win[1] else 'white',
                                tags=("text", "all"))

    def draw_pawns(self, field):
        """
        Function for drawing pawns in appropriate locations on the field
        :param field: list
        :return:
        """
        self.canvas.delete('pawn')
        if field:
            for j, line in enumerate(field):
                for i, pawn in enumerate(line):
                    if pawn:
                        self.canvas.create_oval(i * self.cell_size,
                                                j * self.cell_size,
                                                (i + 1) * self.cell_size,
                                                (j + 1) * self.cell_size,
                                                fill='white' if pawn[0] == core.Checker.white else 'black',
                                                tags=("pawn", "all"))
                        if pawn[1]:
                            self.canvas.create_oval(i * self.cell_size + 30 / 100 * self.cell_size,
                                                    j * self.cell_size + 30 / 100 * self.cell_size,
                                                    (i + 1) * self.cell_size - 30 / 100 * self.cell_size,
                                                    (j + 1) * self.cell_size - 30 / 100 * self.cell_size,
                                                    fill='gold',
                                                    tags=("pawn", "all"))

    def draw_hints(self, point):
        """
        Function for drawing hints for specific point
        :param point: [x, y]
        """
        self.canvas.create_oval(point[0] * self.cell_size,
                                point[1] * self.cell_size,
                                (point[0] + 1) * self.cell_size,
                                (point[1] + 1) * self.cell_size,
                                outline='orange',
                                width=math.ceil(5 / 100 * self.cell_size),
                                tags=("hint", "all"))
        for space in core.get_moves(self.game.field, (point[0], point[1])):
            if space:
                self.canvas.create_rectangle(space[0] * self.cell_size,
                                             space[1] * self.cell_size,
                                             (space[0] + 1) * self.cell_size,
                                             (space[1] + 1) * self.cell_size,
                                             outline='blue',
                                             width=math.ceil(5 / 100 * self.cell_size),
                                             tags=("hint", "all"))
                pawn_to_delete = core.get_pawn_to_delete(self.game.field, point, space)
                if pawn_to_delete:
                    self.canvas.create_oval(pawn_to_delete[0] * self.cell_size,
                                            pawn_to_delete[1] * self.cell_size,
                                            (pawn_to_delete[0] + 1) * self.cell_size,
                                            (pawn_to_delete[1] + 1) * self.cell_size,
                                            outline='red',
                                            width=math.ceil(5 / 100 * self.cell_size),
                                            tags=("hint", "all"))

    def on_mouse_click(self, event):
        """
        Manages mouse clicks
        :param event: tkinter event
        :return: None
        """

        if self.waiting_for_response:
            return
        x = math.floor(event.x / self.cell_size)
        y = math.floor(event.y / self.cell_size)
        self.canvas.delete("hint")
        if (core.in_field(self.game.field, (x, y)) and
                self.game.field[y][x] and
                self.game.field[y][x][0].value == self.game.player and
                (x, y) in core.moving_pawns(self.game.field, self.game.player)):
            self.selected = (True, (x, y))
            self.draw_hints((x, y))
        elif (self.selected[0] and
              (x, y) in core.get_moves(self.game.field, self.selected[1])):
            self.game.make_move(self.selected[1], (x, y))
            self.draw_pawns(self.game.field)
            if self.game.player == self.game.previous_player:
                self.draw_hints((x, y))
                self.selected = (True, (x, y))
            else:
                self.selected = (False, (0, 0))
                # ai workaround
                if self.game.mode == core.Mode.computer:
                    threading.Thread(target=self.make_ai_move_async,
                                     daemon=True).start()
                if self.game.mode == core.Mode.online:
                    threading.Thread(target=self.make_multiplayer_move_async,
                                     daemon=True).start()

                if self.game.field:
                    if len(list(core.get_all_possible_moves(self.game.field, self.game.player))) == 0:
                        self.game.win = (True, not self.game.player)
                if self.game.win[0]:
                    self.draw_win()
                    return
                self.draw_pawns(self.game.field)
        elif self.selected[0] and self.game.player == self.game.previous_player:
            self.game.player = not self.game.player
            self.selected = (False, (0, 0))
            if self.game.mode == core.Mode.computer:
                threading.Thread(target=self.make_ai_move_async,
                                 daemon=True).start()
            if self.game.mode == core.Mode.online:
                threading.Thread(target=self.make_multiplayer_move_async,
                                 daemon=True).start()
            self.draw_pawns(self.game.field)
        else:
            self.selected = (False, (0, 0))
        self.status_update()

    def on_key_down(self, event):
        """
        Keyboard events handler.
        :param event: tkinter event
        """
        if event.keysym == 'Return' and self.game.win[0]:
            self.start_new_game()

    def start_new_game_async(self, side, address, is_host):
        """
        Starts new async multiplayer game.
        :param side: bool
        :param address: tuple
        :param is_host: bool
        :return:
        """
        self.status_bar = StatusBar(self.root, 'Waiting for other player to connect')
        self.waiting_for_response = True
        try:

            self.game = game.Game(core.Mode.online, side, None, address, is_host)
            self.waiting_for_response = False
            threading.Thread(target=self.error_handling, daemon=True).start()
            self.status_bar.set_text('Whites move.')
            if not self.game.player:
                threading.Thread(target=self.make_multiplayer_move_async,
                                 args=(True, ), daemon=True).start()
        except Exception as e:
            self.status_bar.set_text('Could not start multiplayer game with given parameters: {}'.format(e))

    def make_ai_move_async(self, first_move=False):
        """
        Function for asynchronous AI move
        :param first_move: bool
        """
        self.waiting_for_response = True
        self.game.make_ai_move(first_move)
        self.draw_pawns(self.game.field)
        self.waiting_for_response = False
        self.status_update()

        if self.game.field and not self.game.win[0]:
            if len(list(core.get_all_possible_moves(self.game.field, self.game.player))) == 0:
                self.game.win = (True, not self.game.player)
        if self.game.win[0]:
            self.draw_win()

    def make_multiplayer_move_async(self, first_move=False):
        """
        Function for asynchronous multiplayer move
        :param first_move: bool
        """
        try:
            self.waiting_for_response = True
            self.game.make_multiplayer_move(first_move)
            self.draw_pawns(self.game.field)
            self.waiting_for_response = False
            self.status_update()

            if self.game.field and not self.game.win[0]:
                if len(list(core.get_all_possible_moves(self.game.field, self.game.player))) == 0:
                    self.game.win = (True, not self.game.player)
            if self.game.win[0]:
                self.draw_win()
        except ConnectionResetError:
            self.status_bar.set_text('Lost connection with other player.')
        except TimeoutError:
            self.status_bar.set_text('Timeout Error')

    def draw_statusbar(self):
        """
        Method that creates status bar.
        """
        self.status_bar = StatusBar(self.root)

    def status_update(self):
        """
        Method for updating status bar with current move information.
        """
        state = '{} move.'
        if self.status_bar:
            self.status_bar.set_text(state.format('Whites') if self.game.player else state.format('Blacks'))

    def start_new_game(self):
        """
        Starts new game.
        """
        self.root.destroy()
        self.__init__()

    def error_handling(self):
        """
        Thread for handling errors and changing status bar message
        """
        while True:
            time.sleep(1)
            if self.game.client.error:
                #self.status_bar.set_text(self.game.client.error)
                self.status_bar.set_text("Lost with sauce")
                break
