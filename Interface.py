import tkinter as tk
from tkinter import ttk

from webbrowser import open_new_tab
from tkinter.messagebox import showinfo
from core import Contour
from colors import themes
from math import sin, cos, tan, sqrt
from CAS import Parser, Errors


ALLOWED_FUNCTIONS = {
    "sin": sin, "cos": cos, "tan": tan, "sqrt": sqrt, "pow": pow, "min": min, "max": max, "abs": abs
}


numerical_parser = Parser(ALLOWED_FUNCTIONS)
expression_parser = Parser(ALLOWED_FUNCTIONS, ["x", "y"])

instructions = """Left arrow key / down arrow key to decrease resolution.
Right arrow key / up arrow key to increase resolution.
i to zoom in, o to zoom out."""


class Interface(tk.Frame):

    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.master = master
        self.master.title("ContourMG3")
        self.master.grid_columnconfigure(2, weight=1)
        self.master.grid_columnconfigure(3, weight=1)
        self.sfont = ("Arial", 15)

    def set_plot(self, plot):
        self.plot = plot
        self.create_widgets()

    def on_theme_change(self, *args):
        self.plot.set_theme(args[0])

    def show_instructions(self, *args):
        showinfo("Instructions", instructions)

    def open_website(self, *args):
        open_new_tab("http://sambrunacini.com/")

    def update_function(self, *args):
        text = self.function_text.get()
        try:
            tree = expression_parser.parse(text)
            func = lambda x, y: tree.evaluate(x=x, y=y)
            contour = Contour(self.plot, func, 50, themes[self.contour_theme.get()])
            self.plot.set_function(contour)
            self.master.focus()
        except Errors.UserError as e:
            showinfo("Error", "Error: Invalid Function.\nDetails:{}".format(e))
        except Exception:
            raise
            showinfo("Error", "Error: Invalid Function.")

    def create_widgets(self):
        title = tk.Label(self.master, text="ContourMG3", font=("Arial", 20), padx=100)
        title.grid(row=0, column=1, columnspan=7)
        f = tk.font.Font(title, title.cget("font"))
        f.configure(underline=True)
        title.configure(font=f)
        
        ttk.Separator(self.master, orient="horizontal").grid(row=1, column=1, columnspan=5)

        function_frame = tk.Frame(self.master)
        tk.Label(function_frame, text="f(x,y) = ", font=self.sfont).grid(row=0, column=0)
        self.function_text = tk.StringVar(self)
        self.function_box = tk.Entry(function_frame, textvariable=self.function_text)
        self.function_box.grid(row=0, column=1)
        self.function_box.bind("<Return>", self.update_function)
        tk.Button(function_frame, text="Update", command=self.update_function).grid(row=0, column=2)
        function_frame.grid(row=2,column=2)

        theme_frame = tk.Frame(self.master)
        self.contour_theme = tk.StringVar(self, value=tuple(themes.keys())[0])
        tk.Label(theme_frame, text="Theme: ", font=self.sfont).grid(row=0, column=0)
        theme_menu = tk.OptionMenu(theme_frame, self.contour_theme, *themes.keys(), command=self.on_theme_change)
        theme_menu.grid(row=0, column=1)
        theme_frame.grid(row=3, column=2)

        window_frame = tk.Frame(self.master, borderwidth=3, relief="groove")
        window_label = tk.Label(window_frame, text="Window", font=("Arial", 18))
        window_label.grid(row=0, column=0, sticky="w")
        f = tk.font.Font(window_label, window_label.cget("font"))
        f.configure(underline=True)
        window_label.configure(font=f)
        tk.Label(window_frame, text="x range: ", font=self.sfont).grid(row=1, column=0)
        self.x_range = tk.StringVar(self)
        tk.Label(window_frame, textvariable=self.x_range, font=self.sfont).grid(row=1, column=1) # x range
        tk.Label(window_frame, text="y range: ", font=self.sfont).grid(row=2, column=0)
        self.y_range = tk.StringVar(self)
        tk.Label(window_frame, textvariable=self.y_range, font=self.sfont).grid(row=2, column=1) # y range
        tk.Label(window_frame, text="Mouse position: ", font=self.sfont).grid(row=3, column=0, columnspan=2)
        self.mouse_pos = tk.StringVar(self)
        tk.Label(window_frame, textvariable=self.mouse_pos, font=self.sfont).grid(row=3, column=2) # mouse pos
        window_frame.grid(row=5, column=1, columnspan=7, sticky="ew")
        
        ttk.Separator(self.master, orient="horizontal").grid(row=6, column=1, columnspan=5)

        bottom_frame = tk.Frame(self.master, borderwidth=3, relief="groove")
        tk.Button(bottom_frame, text="Instructions", command=self.show_instructions).grid(row=0, column=0, sticky="ew")
        tk.Button(bottom_frame, text="Visit Site", command=self.open_website).grid(row=0, column=1, sticky="ew")
        tk.Label(bottom_frame, text="Copyright (c) 2020 Sam Brunacini. Source available under MIT License.", font=("Arial", 12)).grid(row=1, column=0, columnspan=2)
        bottom_frame.grid(row=13, column=2)

    def update_data(self):
        data = self.plot.get_window_data()
        self.x_range.set(data[0])
        self.y_range.set(data[1])
        self.mouse_pos.set(data[2])
