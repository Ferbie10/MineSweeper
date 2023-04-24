import tkinter as tk
import random
import time


class MinesweeperGUI:
    def __init__(self,height,width,mines,num_episodes):
        self.height = height
        self.width = width
        self.mines = mines
        self.num_episodes = num_episodes
        self.total_moves = 0
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

        self.buttons = []
        self._game_end = False
        self.revealed_cells = set()
        self.max_spaces = self.height+self.width - self.mines

        # Modes: system (default), light, dark
        self.app = tk.Tk()  # create CTk window like you do with the Tk window
        self.app.geometry("1040x940")
        self.app.title("MineSweeper")

        self.Mineframe = tk.Frame(
            master=self.app, height=600, width=940)
        self.Mineframe.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.Statframe = tk.Frame(
            master=self.app, height=300, width=940)
        self.Statframe.grid(row=1, column=0, padx=5, pady=5, sticky="s")
        self.button_texts = [[None for _ in range(
            self.width)] for _ in range(self.height)]

        # Create a scrollable textbox

        self.board = self.generate_board()
        self.create_minesweeper()
        self.create_statistics()
        self.app.mainloop()

    def update_statistics(self):
        self.stats_label.configure(text=self.generate_stats())
        # Schedule the next update in 1000ms (1s)
        self.app.after(1000, self.update_statistics)

    def create_statistics(self):
        self.stats_label = tk.Label(
            self.Statframe, text=self.generate_stats(), justify=tk.LEFT)
        self.stats_label.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        self.update_statistics()

    def generate_stats(self):
        elapsed_time = int(time.time() - self.start_time)
        best_score = self.best_score if self.best_score is not None else "N/A"
        best_reward = self.best_reward if self.best_reward is not None else "N/A"
        best_reward_episode = self.best_reward_episode if self.best_reward_episode is not None else "N/A"
        best_correct_flag = self.best_correct_flag if self.best_correct_flag is not None else "N/A"
        best_flag_episode = self.best_flag_episode if self.best_flag_episode is not None else "N/A"

        stats = f"Elapsed time: {elapsed_time}s\n" \
                f"Total games: {self.current_episode}\n" \
                f"Total moves: {self.total_moves}\n" \
                f"Best Number of flags: {best_correct_flag}\n" \
                f"Best Number of flags episode: {best_flag_episode}\n" \
                f"Best score: {best_score}\n" \
                f"Best reward: {best_reward}\n" \
                f"Best reward episode: {best_reward_episode}"

        return stats

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
        current_text = self.button_texts[row][col]
        flagged = self.board[row][col]

        if current_text == "":
            button.configure(text="F", fg='red')
            self.button_texts[row][col] = "F"
            self.total_moves += 1
            self.total_num_flags += 1
            if flagged == '*':
                self.total_correct_flags += 1
                print(f'total_correct_flags {self.total_correct_flags}')
            else:
                self.total_incorrect_flags += 1

                print(f' total_incorrect_flags {self.total_incorrect_flags}')

        elif current_text == "F":
            button.configure(text="")
            self.button_texts[row][col] = ""
            self.total_moves -= 1
            self.total_num_flags -= 1
            if flagged == '*':
                self.total_correct_flags -= 1

            else:
                self.total_incorrect_flags -= 1

        # Call max_moves to check if the game should end
        self.max_moves()

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
                text=str(self.board[row][col]), width=4, height=2)
            self.buttons[row][col].configure(state=tk.DISABLED)
            self.revealed_cells.add((row, col))
            if self.board[row][col] == 0:
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if 0 <= row + i < self.height and 0 <= col + j < self.width and (row + i, col + j) not in self.revealed_cells:
                            self.reveal_cell(row + i, col + j)
            self.total_moves += 1
            self.max_moves()

    def max_moves(self):
        if len(self.revealed_cells) + self.total_num_flags == (self.height * self.width):
            self.reset_board()

    def reset_board(self):
        self.sum_flags = self.total_correct_flags - self.total_incorrect_flags
        if self.current_episode < self.num_episodes:
            if self.best_correct_flag < self.sum_flags:
                self.best_correct_flag = self.sum_flags
                self.best_flag_episode = self.current_episode

            self.board = self.generate_board()
            self._game_end = False
            self.revealed_cells.clear()
            self.total_moves = 0
            self.total_num_flags = 0
            self.current_episode += 1
            for i in range(self.height):
                for j in range(self.width):
                    button = self.buttons[i][j]
                    button.configure(text="", state=tk.NORMAL)

    def create_minesweeper(self):
        for i in range(self.height):
            row_buttons = []
            for j in range(self.width):
                button = tk.Button(self.Mineframe, text="", width=4, height=2, fg='black',
                                   command=lambda i=i, j=j: self.reveal_cell(i, j))

                button.bind("<Button-3>", lambda event, i=i,
                            j=j: self.toggle_flag(event, i, j))
                button.grid(row=i, column=j)
                row_buttons.append(button)
            self.buttons.append(row_buttons)
            self.button_texts[i] = [""] * self.width


app = MinesweeperGUI()
