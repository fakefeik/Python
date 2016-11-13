"""
Graphics module.
"""
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import parse
import threading
from country import Country
from coloring import Colorer


COUNTRIES = """10, 10; 200, 10; 200, 150; 10, 200
200, 100; 300, 60; 250, 10; 200, 10
200, 100; 300, 60; 200, 200
"""


class Graphics:
    """
    Graphics begins here.
    """
    def __init__(self):
        self.root = tkinter.Tk()
        self.canvas = tkinter.Canvas()
        self.menu = tkinter.Menu()
        self.create_menu(tkinter.ACTIVE)
        self.locked = False
        self.root.config(menu=self.menu)
        self.canvas.configure(width=1024, height=768)
        self.edit = True
        self.temp_points = []
        try:
            with open('maps/default.txt') as country_file:
                countries = parse.load(country_file)
        except (FileNotFoundError, ValueError, IndexError):
            countries = parse.load(COUNTRIES.splitlines())
        self.colorer = Colorer(countries)

        self.draw_countries()
        self.canvas.pack()
        self.root.bind('<Button-1>', self.on_mouse_click)
        self.root.bind('<Key>', self.on_key_down)
        self.root.title('mapcoloring')
        self.root.mainloop()

    def create_menu(self, state):
        """
        Creates menu.
        :param state: tkinter.DISABLED or tkinter.ACTIVE
        :return: None
        """
        def file_save():
            """
            Saves current countries to file.
            """
            file = tkinter.filedialog.asksaveasfile(mode='w', defaultextension='.txt')
            if file:
                file.write(parse.save(self.colorer.countries))
                file.close()

        def file_load():
            """
            Loads countries from file.
            """
            file = tkinter.filedialog.askopenfile()
            if file:
                try:
                    self.colorer.countries = parse.load(file)
                except (FileNotFoundError, ValueError, IndexError):
                    self.colorer.countries = parse.load(COUNTRIES.splitlines())
                file.close()
                self.colorer.set_colors()
                self.draw_countries()

        def set_algorithm(number):
            """
            Sets number of the algorithm used.
            :param number: int
            """
            if not self.locked:
                self.colorer.algorithm = number
                for country in self.colorer.countries.items:
                    country[1] = None
                threading.Thread(target=self.set_colors_async, daemon=True).start()

        def about():
            """
            Shows info about this program
            """
            tkinter.messagebox.showinfo('Info', 'Map coloring')

        file_menu = tkinter.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="Load", command=file_load, state=state)
        file_menu.add_command(label="Save", command=file_save, state=state)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        self.menu.add_cascade(label="File", menu=file_menu)

        algorithm_menu = tkinter.Menu(self.menu, tearoff=0)
        algorithm_menu.add_radiobutton(label="algo0",
                                       command=lambda: set_algorithm(0),
                                       state=state)
        algorithm_menu.add_radiobutton(label="algo1",
                                       command=lambda: set_algorithm(1),
                                       state=state)
        self.menu.add_cascade(label="Algorithms", menu=algorithm_menu)

        help_menu = tkinter.Menu(self.menu, tearoff=0)
        help_menu.add_command(label="About", command=about)
        self.menu.add_cascade(label="Help", menu=help_menu)

    def draw_countries(self):
        """
        Draws countries to canvas.
        """
        self.canvas.delete("all")
        for country in self.colorer.countries.items:
            self.canvas.create_polygon(country[0].coordinates,
                                       outline='black',
                                       fill=country[1],
                                       tags=("all", ))
        self.canvas.create_text(50, 50, font=("Impact", 72),
                                text=self.colorer.number_of_colors_used + 1,
                                fill='white', tags=("text", "all"))

    def on_mouse_click(self, event):
        """
        Handles mouse clicks and drawing.
        :param event: tkinter event
        """
        if self.edit and not self.locked:
            self.canvas.delete("editable")
            self.temp_points.append([event.x, event.y])
            self.canvas.create_oval(event.x - 1, event.y - 1,
                                    event.x + 1, event.y + 1,
                                    fill='black', tags=("all", ))
            for i in range(len(self.temp_points)):
                self.canvas.create_line(self.temp_points[i % len(self.temp_points)],
                                        self.temp_points[(i + 1) % len(self.temp_points)],
                                        fill='black', dash=(2, 4), tags=("all", "editable"))

    def on_key_down(self, event):
        """
        Handles keyboard events and drawing.
        :param event: tkinter event.
        """
        if (event.keysym == 'Return' and self.edit
                and not self.locked and len(self.temp_points) > 0):
            self.colorer.countries.items.append([Country(self.temp_points), None])
            self.temp_points = []
            for country in self.colorer.countries.items:
                country[1] = None

            threading.Thread(target=self.set_colors_async, daemon=True).start()

    def set_colors_async(self):
        """
        Asynchronous colors set function.
        """
        self.locked = True
        self.menu = tkinter.Menu()
        self.create_menu(tkinter.DISABLED)
        self.root.config(menu=self.menu)
        self.colorer.set_colors()
        self.draw_countries()
        self.locked = False
        self.menu = tkinter.Menu()
        self.create_menu(tkinter.ACTIVE)
        self.root.config(menu=self.menu)
