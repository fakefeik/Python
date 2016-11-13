import re
import tkinter
import tkinter.filedialog
import tkinter.messagebox


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


class Graphics:
    def __init__(self):
        self.root = tkinter.Tk()

        self.menu = tkinter.Menu()
        self.create_menu(tkinter.ACTIVE)
        self.status_bar = StatusBar(self.root, "Press space to start")

        self.started = False
        self.words = []
        self.words_on_screen = 1
        self.index = 0
        self.speed = 250

        self.init_text("Click open to load your own text")

        self.canvas = tkinter.Canvas()

        self.root.resizable(width=False, height=False)
        self.canvas.configure(width=700, height=400)
        self.root.bind('<Key>', self.on_key_down)
        self.root.title("RSVP")

        self.canvas.pack()

        self.root.config(menu=self.menu)
        self.root.mainloop()

    def init_text(self, text):
        self.status_bar.set_text("Press space to start")
        self.index = 0
        self.words = re.findall(r"\w+", text)

    def start_game(self):
        self.started = True
        if self.index >= len(self.words):
            self.index = 0
        self.timer_tick()

    def update_status(self):
        self.status_bar.set_text("Speed: {speed} wpm, Finished: {finished}%".format(
            speed=self.speed,
            finished=int(self.index/len(self.words) * 100))
        )

    def timer_tick(self):
        if self.started:
            self.update_status()
            self.canvas.delete("all")
            if self.index >= len(self.words):
                self.started = False
                return
            self.draw_text(self.words[self.index])
            self.index += 1
            self.root.after(int(60 / self.speed * 1000), self.timer_tick)

    def create_menu(self, state):
        """
        Creates menu with save/load and about sections
        :param state: tkinter.DISABLED or tkinter.ACTIVE
        """
        def file_load():
            """
            Function for loading field from file
            """
            filename = tkinter.filedialog.askopenfilename()
            with open(filename, encoding="utf8") as f:
                self.init_text(f.read())

        def about():
            """
            Shows about message
            """
            tkinter.messagebox.showinfo('Info', 'RSVP')

        filemenu = tkinter.Menu(self.menu, tearoff=0)
        filemenu.add_command(label="Load", command=file_load, state=state)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        self.menu.add_cascade(label="File", menu=filemenu)

        helpmenu = tkinter.Menu(self.menu, tearoff=0)
        helpmenu.add_command(label="About", command=about)
        self.menu.add_cascade(label="Help", menu=helpmenu)

    def draw_text(self, text):
        self.canvas.create_text(350,
                                200,
                                font=("Impact", 48),
                                text=text,
                                fill="black",
                                tags=("text", "all"))

    def on_key_down(self, event):
        if event.keysym == "space":
            if not self.started:
                self.start_game()
            else:
                self.started = False
        elif event.keysym == "Up":
            self.speed += 10
        elif event.keysym == "Down":
            if self.speed < 100:
                return
            self.speed -= 10
        elif event.keysym == "Left":
            if not self.started and self.index > 0:
                self.index -= 1
                self.canvas.delete("all")
                self.draw_text(self.words[self.index])
        elif event.keysym == "Right":
            if not self.started and self.index < len(self.words) - 1:
                self.index += 1
                self.canvas.delete("all")
                self.draw_text(self.words[self.index])
        self.update_status()

if __name__ == "__main__":
    Graphics()
