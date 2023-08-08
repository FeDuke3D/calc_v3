"""view module, containing gui"""

import sys
import os

import tkinter
from tkinter.messagebox import showinfo, showerror
import customtkinter as ctk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

from presenter import Presenter


class HistoryWindow(ctk.CTkToplevel):
    """pop-up window with history of operations"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.title('History')

        var = ctk.Variable(value=parent.history)
        self.history_listbox = tkinter.Listbox(self, listvariable=var, height=6,
                                               selectmode=tkinter.SINGLE)
        self.history_listbox.pack(side=tkinter.LEFT)
        self.history_listbox.bind('<<ListboxSelect>>', self.history_selected)

        scrollbar = tkinter.Scrollbar(self, orient=tkinter.VERTICAL,
                                      command=self.history_listbox.yview)
        self.history_listbox['yscrollcommand'] = scrollbar.set
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

    def history_selected(self, event):
        """handling history list selection"""
        self.parent.repeat_from_history(self.history_listbox.curselection()[0])
        self.destroy()


class App(ctk.CTk):
    """main view class"""
    def __init__(self):
        super().__init__()

        # here goes MVP
        self.presenter = Presenter()

        # history of operation
        try:
            file_path = 'history.txt'
            dir_name = os.path.dirname(sys.argv[0])
            if dir_name:
                file_path = os.sep.join([dir_name, file_path])
            with open(file_path, 'r', encoding='utf-8') as hist_file:
                self.history = hist_file.read().split('\n')
                if len(self.history) == 1 and self.history[0] == '':
                    self.history = []
        except FileNotFoundError:
            self.history = []
        self.protocol("WM_DELETE_WINDOW", self.remember)

        # setting interface
        self.title("SmartCalc_v3")
        self.geometry("640x480")
        self.minsize(640, 480)
        for i in range(3):
            self.grid_columnconfigure(i, weight=1, uniform="column")
            self.grid_rowconfigure(i, minsize=50)
        self.grid_rowconfigure(4, weight=1)

        grid_settings = {"padx": 5, "pady": 5, "sticky": "ew"}
        labels_settings = {"padx": 5, "pady": 5, "sticky": "e"}

        # menu bar
        self.menubar = tkinter.Menu(self)
        self.config(menu=self.menubar)
        self.menu_tools = tkinter.Menu(self.menubar, tearoff=False)
        self.menu_help = tkinter.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label='Tools', menu=self.menu_tools)
        self.menu_tools.add_command(label='History', command=self.open_history)
        self.menu_tools.add_command(label='Clear History',
                                    command=self.clear_history)
        self.menubar.add_cascade(label='Help', menu=self.menu_help)
        self.menu_help.add_command(label='Formula',
                                   command=self.show_help_formula)
        self.menu_help.add_command(label='Variable',
                                   command=self.show_help_variable)
        self.menu_help.add_command(label='Limits',
                                   command=self.show_help_limits)
        self.menu_help.add_command(label='Graph', command=self.show_help_graph)
        self.menu_help.add_command(label='Tools', command=self.show_help_tools)
        self.menu_help.add_command(label='Help', command=self.show_help_help)

        # formula input field
        self.formula_str = ctk.StringVar()
        self.formula_input = ctk.CTkEntry(self, justify="right",
                                          textvariable=self.formula_str)
        self.formula_input.grid(row=0, column=0, columnspan=3, **grid_settings)

        # answer
        self.answer_display = ctk.CTkLabel(self, text='=', anchor='w')
        self.answer_display.grid(row=0, column=3, **grid_settings)

        # variable x label
        self.variable_label = ctk.CTkLabel(self, text="x =")
        self.variable_label.grid(row=1, column=1, **labels_settings)

        # variable x input field
        self.variable_input = ctk.CTkEntry(self)
        self.variable_input.insert(0, '0.0')
        self.variable_input.grid(row=1, column=2, **grid_settings)

        # graph borders labels
        self.min_x_label = ctk.CTkLabel(self, text="min x =")
        self.min_x_label.grid(row=2, column=0, **labels_settings)
        self.max_x_label = ctk.CTkLabel(self, text="max x =")
        self.max_x_label.grid(row=2, column=2, **labels_settings)
        self.min_y_label = ctk.CTkLabel(self, text="min y =")
        self.min_y_label.grid(row=3, column=0, **labels_settings)
        self.max_y_label = ctk.CTkLabel(self, text="max y =")
        self.max_y_label.grid(row=3, column=2, **labels_settings)

        # graph borders input fields
        self.min_x_input = ctk.CTkEntry(self)
        self.min_x_input.insert(0, '0.0')
        self.min_x_input.grid(row=2, column=1, **grid_settings)
        self.max_x_input = ctk.CTkEntry(self)
        self.max_x_input.insert(0, '1.0')
        self.max_x_input.grid(row=2, column=3, **grid_settings)
        self.min_y_input = ctk.CTkEntry(self)
        self.min_y_input.insert(0, '0.0')
        self.min_y_input.grid(row=3, column=1, **grid_settings)
        self.max_y_input = ctk.CTkEntry(self)
        self.max_y_input.insert(0, '1.0')
        self.max_y_input.grid(row=3, column=3, **grid_settings)

        # plot area
        self.fig = plt.Figure(figsize=(5, 4), dpi=100)
        self.fig_plot = self.fig.add_subplot(1, 1, 1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=4, column=0, columnspan=4, padx=5,
                                         pady=5, sticky="nsew")
        self.canvas.draw()

        # binding signals
        self.formula_input.bind("<Return>", self.formula_entered)
        self.variable_input.bind("<Return>", self.send_param)
        self.min_x_input.bind("<Return>", self.change_scale)
        self.max_x_input.bind("<Return>", self.change_scale)
        self.min_y_input.bind("<Return>", self.change_scale)
        self.max_y_input.bind("<Return>", self.change_scale)

    # some methods
    @staticmethod
    def read_float_field(field, default_val=0.0):
        """reading float from string input field"""
        try:
            res = float(field.get())
        except ValueError:
            res = default_val
            field.delete(0, len(field.get()))
            field.insert(0, str(default_val))
        return res

    def change_answer(self):
        """calling presenter and changing ui-answer to acquired string"""
        answer_str = self.presenter.calculate()
        self.answer_display.configure(text='= ' + answer_str)

    def change_graph(self):
        """calling presenter and redrawing graph"""
        coords_x = np.linspace(self.x_min, self.x_max, 10000)
        coords_y = self.presenter.calc_graph(coords_x)
        self.fig_plot.clear()
        if coords_y:
            self.fig_plot.plot(coords_x, coords_y)
        self.fig_plot.set_xlim([self.x_min, self.x_max])
        self.fig_plot.set_ylim([self.y_min, self.y_max])
        self.fig_plot.grid(linestyle=':')
        self.canvas.draw()

    def remember(self):
        """end of application life - save history and close app"""
        file_path = 'history.txt'
        dir_name = os.path.dirname(sys.argv[0])
        if dir_name:
            file_path = os.sep.join([dir_name, file_path])
        with open(file_path, 'w', encoding='utf-8') as hist_file:
            hist_file.write('\n'.join(self.history))
        self.destroy()

    def send_formula(self) -> bool:
        """sends formula to presenter->model to parse"""
        if self.presenter.change_expression(self.formula_str.get()):
            self.change_answer()
            if self.presenter.has_var_x():
                self.change_graph()
            return True
        else:
            self.answer_display.configure(text='= syntax error')
            return False

    def open_history(self):
        """opens history pop-up window"""
        if len(self.history):
            window = HistoryWindow(self)
            window.grab_set()
        else:
            showinfo(title='Information', message='History is empty')

    def repeat_from_history(self, index):
        """sets formula from history to input field and calculates"""
        self.formula_input.delete(0, len(self.formula_input.get()))
        self.formula_input.insert(0, self.history[index])
        self.send_formula()

    def clear_history(self):
        """clears current history list"""
        self.history = []

    @staticmethod
    def show_help(page):
        """general method for showing help articles"""
        try:
            file_path = os.sep.join(['manual', page + '.txt'])
            dir_name = os.path.dirname(sys.argv[0])
            if dir_name:
                file_path = os.sep.join([dir_name, file_path])
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                showinfo(title=page.title(), message=content)
        except FileNotFoundError:
            showerror(title='Error', message='Help not found')

    def show_help_formula(self):
        """shows help about formula input"""
        self.show_help('formula')

    def show_help_graph(self):
        """shows help about graph area"""
        self.show_help('graph')

    def show_help_help(self):
        """shows help about help"""
        self.show_help('help')

    def show_help_limits(self):
        """shows help about graph limits"""
        self.show_help('limits')

    def show_help_tools(self):
        """shows help about tools menu"""
        self.show_help('tools')

    def show_help_variable(self):
        """shows help about variable input field"""
        self.show_help('variable')

    # properties for float input fields
    @property
    def x_var(self):
        """variable x in input field"""
        return self.read_float_field(self.variable_input)

    @property
    def x_min(self):
        """left x limit in input field"""
        return self.read_float_field(self.min_x_input)

    @x_min.setter
    def x_min(self, new_val):
        self.min_x_input.delete(0, len(self.min_x_input.get()))
        self.min_x_input.insert(0, str(new_val))

    @property
    def x_max(self):
        """right x limit in input field"""
        return self.read_float_field(self.max_x_input, 1.0)

    @x_max.setter
    def x_max(self, new_val):
        self.max_x_input.delete(0, len(self.max_x_input.get()))
        self.max_x_input.insert(0, str(new_val))

    @property
    def y_min(self):
        """lower y limit in input field"""
        return self.read_float_field(self.min_y_input)

    @y_min.setter
    def y_min(self, new_val):
        self.min_y_input.delete(0, len(self.min_y_input.get()))
        self.min_y_input.insert(0, str(new_val))

    @property
    def y_max(self):
        """upper y limit in input field"""
        return self.read_float_field(self.max_y_input, 1.0)

    @y_max.setter
    def y_max(self, new_val):
        self.max_y_input.delete(0, len(self.max_y_input.get()))
        self.max_y_input.insert(0, str(new_val))

    # signals handling
    def formula_entered(self, event):
        """sends formula to presenter->model and adds to history if ok"""
        if self.send_formula():
            self.history.append(self.formula_str.get())

    def send_param(self, event):
        """sends variable x to presenter and recalculates answer"""
        self.presenter.param = self.x_var
        self.change_answer()

    def change_scale(self, event):
        """handles changing of graph limits change"""
        if self.x_min > self.x_max:
            self.x_min, self.x_max = self.x_max, self.x_min
        if self.y_min > self.y_max:
            self.y_min, self.y_max = self.y_max, self.y_min
        if self.presenter.has_var_x():
            self.change_graph()
