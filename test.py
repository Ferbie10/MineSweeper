    def get_statistics_text(self):
        elapsed_time = int(time.time() - self.start_time)
        best_score = self.best_score if self.best_score is not None else "N/A"
        best_reward = self.best_reward if self.best_reward is not None else "N/A"
        best_reward_episode = self.best_reward_episode if self.best_reward_episode is not None else "N/A"

        return f"Elapsed time: {elapsed_time}s\nTotal Moves: {self.current_episode}\nTotal moves: {self.total_moves}\nBest Number of flags: {self.best_correct_flag}\nBest Number of flags episode : {self.best_flag_episode}\nBest score: {self.best_score}\nBest reward: {self.best_reward}\nBest reward episode: {self.best_reward_episode}"

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
