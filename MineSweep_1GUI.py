import tkinter as tk
import customtkinter
import random
import time


class MinesweeperGUI:
    def __init__(self):
        self.total_moves = 0
        self.num_episodes = 10
        self.move_counter = 0
        self.current_episode = 0
        self.best_score = None
        self.best_reward = None
        self.best_reward_episode = None
        self.total_reward = 0
        self.total_correct_flags = 0
        self.total_incorrect_flags = 0
        self.total_num_flags = 0
        self.best_correct_flag = 0
        self.best_flag_episode = None
        self.start_time = time.time()
        self.height = 15
        self.width = 15
        self.mines = 30
        self.buttons = []
        self._game_end = False
        self.revealed_cells = set()

        # Modes: system (default), light, dark
        customtkinter.set_appearance_mode("System")
        self.app = customtkinter.CTk()  # create CTk window like you do with the Tk window
        self.app.geometry("1040x940")
        self.app.title("MineSweeper")

        self.Mineframe = customtkinter.CTkFrame(
            master=self.app, height=600, width=940)
        self.Mineframe.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.Statframe = customtkinter.CTkFrame(
            master=self.app, height=300, width=940)
        self.Statframe.grid(row=1, column=0, padx=5, pady=5, sticky="s")
        self.button_texts = [[None for _ in range(
            self.width)] for _ in range(self.height)]

        # Create a scrollable textbox

        self.board = self.generate_board()
        self.create_minesweeper()
        self.app.mainloop()

    def generate_board(self):
        board = [[0 for _ in range(self.width)] for _ in range(self.height)]

        mines_placed = 0
        while mines_placed < self.mines:
            row = random.randint(0, self.height - 1)
            col = random.randint(0, self.width - 1)
            if board[row][col] == 0:
                board[row][col] = "*"
                mines_placed += 1

        for row in range(self.height):
            for col in range(self.width):
                if board[row][col] == "*":
                    continue

                mines_count = 0
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if 0 <= row + i < self.height and 0 <= col + j < self.width:
                            if board[row + i][col + j] == "*":
                                mines_count += 1

                board[row][col] = mines_count

        return board

    def toggle_flag(self, event, row, col):
        button = self.buttons[row][col]
        print(f'Row {row}, Col {col}')
        current_text = self.button_texts[row][col]
        if current_text == "":
            flagged = self.board[row][col]
            button.configure(text="F", text_color='red')
            self.button_texts[row][col] = "F"
            self.total_moves += 1
            self.total_num_flags += 1
            if flagged == '*':
                self.total_correct_flags += 1
            else:
                self.total_incorrect_flags += 1

        elif current_text == "F":
            button.configure(text="")
            self.button_texts[row][col] = ""
            self.total_moves -= 1
            self.total_num_flags -= 1
            if flagged == '*':
                self.total_correct_flags -= 1
            else:
                self.total_incorrect_flags -= 1

    def get_current_state(self):
        current_state = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                if (i, j) in self.revealed_cells:
                    row.append(self.board[i][j])
                else:
                    row.append(-1)
            current_state.append(row)
        return current_state

    @property
    def game_end(self):
        return self._game_end

    def reveal_cell(self, row, col):
        if not self._game_end and (row, col) not in self.revealed_cells:
            if self.board[row][col] == "*":  # Handle mine cell click
                self.reset_board()
                return
            print(self.total_moves)
            # Convert the number to a string
            self.buttons[row][col].configure(
                text=str(self.board[row][col]), width=55, height=35)
            self.buttons[row][col].configure(state=tk.DISABLED)
            self.revealed_cells.add((row, col))
            if self.board[row][col] == 0:
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if 0 <= row + i < self.height and 0 <= col + j < self.width and (row + i, col + j) not in self.revealed_cells:
                            self.reveal_cell(row + i, col + j)
                self.total_moves += 1

    def reset_board(self):
        self.board = self.generate_board()
        self._game_end = False
        self.revealed_cells.clear()

        for i in range(self.height):
            for j in range(self.width):
                button = self.buttons[i][j]
                # Change bg=None to bg="SystemButtonFace"
                button.configure(text="", state=tk.NORMAL, border_color="grey")

        self.current_episode += 1  # Increment the episode counter
        if self.current_episode < self.num_episodes:
            self.reset_board()
            self.revealed_cells.clear()
        # Update the board appearance

    def create_minesweeper(self):
        for i in range(self.height):
            row_buttons = []
            for j in range(self.width):
                button = customtkinter.CTkButton(self.Mineframe, text="", width=55, height=35, border_color='black',
                                                 border_width=5, command=lambda i=i, j=j: self.reveal_cell(i, j))
                button.bind("<Button-3>", lambda event, i=i,
                            j=j: self.toggle_flag(event, i, j))
                button.grid(row=i, column=j)
                row_buttons.append(button)
            self.buttons.append(row_buttons)
            self.button_texts[i] = [""] * self.width




app = MinesweeperGUI()
