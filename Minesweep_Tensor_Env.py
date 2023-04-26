import numpy as np
from tf_agents.environments import py_environment
from tf_agents.specs import array_spec
from tf_agents.trajectories import time_step as ts
import MineSweep_GUI


class MinesweeperPyEnvironment(py_environment.PyEnvironment):
    def __init__(self, height, width, mines):
        self._height = height
        self._width = width
        self._mines = mines
        self._minesweeper = MineSweep_GUI.MinesweeperGUI(height, width, mines)
        self._action_spec = array_spec.BoundedArraySpec(
            shape=(), dtype=np.int32, minimum=0, maximum=height * width - 1, name='action')
        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(height, width), dtype=np.int32, minimum=-1, maximum=8, name='observation')
        self._state = np.full((height, width), -1)
        self._episode_ended = False

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset(self):
        self._minesweeper.reset()
        self._state.fill(-1)
        self._episode_ended = False
        return ts.restart(self._state)

    def _step(self, action):
        if self._episode_ended:
            return self.reset()

        row = action // self._width
        col = action % self._width
        reward = self._minesweeper.step(row, col)

        if self._minesweeper.game_end:
            self._episode_ended = True
            return ts.termination(self._state, reward)

        self._state = np.array(self._minesweeper.get_current_state())
        return ts.transition(self._state, reward=reward)
