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
        self.mines = 10
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

        # Create a scrollable textbox

        self.board = self.generate_board()
        self.create_minesweeper()
        self.create_statistics()
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
        if button.cget("label_text") == "":
            button.config(label_text="F", background_color="yellow")
        elif button.cget("label_text") == "F":
            button.config(label_text="", background_color=None)

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

            # Convert the number to a string
            self.buttons[row][col].configure(
                text=str(self.board[row][col]), width=55, height=35)  # Set the width to 3
            self.buttons[row][col].configure(state=tk.DISABLED)
            self.revealed_cells.add((row, col))
            if self.board[row][col] == 0:
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if 0 <= row + i < self.height and 0 <= col + j < self.width and (row + i, col + j) not in self.revealed_cells:
                            self.reveal_cell(row + i, col + j)
            self.total_moves += 1

    def get_statistics_text(self):
        elapsed_time = int(time.time() - self.start_time)
        best_score = self.best_score if self.best_score is not None else "N/A"
        best_reward = self.best_reward if self.best_reward is not None else "N/A"
        best_reward_episode = self.best_reward_episode if self.best_reward_episode is not None else "N/A"

        return f"Elapsed time: {elapsed_time}s\n Total games: {self.current_episode}\nTotal moves: {self.total_moves}\nBest Number of flags: {self.best_correct_flag}\nBest Number of flags episode : {self.best_flag_episode}\nBest score: {self.best_score}\nBest reward: {self.best_reward}\nBest reward episode: {self.best_reward_episode}"

    def create_statistics(self):
        self.stats_label = customtkinter.CTkLabel(
            self.Statframe, text=self.get_statistics_text(), justify=tk.LEFT)
        self.stats_label.pack(fill=tk.BOTH, side=tk.TOP, expand=True)

    def reset_board(self):
        self.board = self.generate_board()
        self._game_end = False
        self.revealed_cells.clear()

        for i in range(self.height):
            for j in range(self.width):
                button = self.buttons[i][j]
                # Change bg=None to bg="SystemButtonFace"
                button.configure(text="", state=tk.NORMAL, border_color="grey")

        # Update the statistics label
        elapsed_time = int(time.time() - self.start_time)
        if self.best_score is None or self.total_moves > self.best_score:
            self.best_score = self.total_moves
        if self.best_reward is None or self.total_reward > self.best_reward:
            self.best_reward = self.total_reward
            self.best_reward_episode = self.current_episode
        if self.best_correct_flag is None or self.total_correct_flags > self.best_correct_flag:
            self.best_correct_flag = self.total_correct_flags
            self.best_flag_episode = self.current_episode
        self.total_reward = 0
        self.total_moves = 0
        self.total_correct_flags = 0
        self.total_incorrect_flags = 0
        self.total_num_flags = 0
        self.stats_label.configure(text=self.get_statistics_text())

        self.current_episode += 1  # Increment the episode counter
        if self.current_episode < self.num_episodes:
            self.reset_board()
            self.revealed_cells.clear()
        # Update the board appearance

    def create_minesweeper(self):
        for i in range(self.height):
            row_buttons = []
            for j in range(self.width):
                button = customtkinter.CTkButton(self.Mineframe, text="", width=55, height=35, border_color='grey',
                                                 border_width=5, command=lambda i=i, j=j: self.reveal_cell(i, j))  # Add highlightthickness option
                button.bind("<Button-3>", lambda event, i=i,
                            j=j: self.toggle_flag(event, i, j))
                button.grid(row=i, column=j)
                row_buttons.append(button)
            self.buttons.append(row_buttons)


app = MinesweeperGUI()
