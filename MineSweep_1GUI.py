import tk
import tkinter
import customtkinter
import os


class MinesweeperGUI:
    def __init__(self):
        # Modes: system (default), light, dark
        customtkinter.set_appearance_mode("System")
        self.app = customtkinter.CTk()  # create CTk window like you do with the Tk window
        self.app.geometry("840x840")

        self.Mineframe = customtkinter.CTkFrame(
            master=self.app, width=400, height=400)
        self.Statframe = customtkinter.CTkScrollableFrame(
            master=self.app, width=400, height=400)
        self.Mineframe.grid(row=0, column=0, padx=20, pady=20, sticky="e")
        self.Statframe.grid(row=1, column=1, padx=20, pady=20, sticky="w")
        self.Minelabel = customtkinter.CTkLabel(
            master=self.Mineframe, text='MineSweeper').grid(row=0, column=1)


app = MinesweeperGUI()
