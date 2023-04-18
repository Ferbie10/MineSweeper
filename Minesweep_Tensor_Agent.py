import tkinter as tk
import numpy as np
import tensorflow as tf
from Minesweep_Tensor_Env import MinesweeperEnv
from Minesweep_Tensor_GUI import MinesweeperGUI
from tf_agents.agents.dqn import dqn_agent
from tf_agents.drivers import dynamic_step_driver
from tf_agents.environments import tf_py_environment
from tf_agents.eval import metric_utils
from tf_agents.metrics import tf_metrics
from tf_agents.networks import q_network
from tf_agents.replay_buffers import tf_uniform_replay_buffer
from tf_agents.trajectories import trajectory
from tf_agents.utils import common
from tf_agents.environments import gym_wrapper


def compute_avg_return(eval_env, policy, num_episodes):
    total_return = 0
    for _ in range(num_episodes):
        time_step = eval_env.reset()
        episode_return = 0
        while not time_step.is_last():
            action_step = policy.action(time_step)
            time_step = eval_env.step(action_step.action)
            episode_return += time_step.reward.numpy().sum()
        total_return += episode_return
    return total_return / num_episodes


class MinesweeperAgent:
    def __init__(self, num_iterations, initial_collect_steps, collect_steps_per_iteration, replay_buffer_max_length, batch_size, learning_rate, log_interval, num_eval_episodes, eval_interval):
        self.learning_rate = learning_rate
        self.num_iterations = num_iterations
        self.initial_collect_steps = initial_collect_steps
        self.collect_steps_per_iteration = collect_steps_per_iteration
        self.replay_buffer_max_length = replay_buffer_max_length
        self.batch_size = batch_size
        self.log_interval = log_interval
        self.num_eval_episodes = num_eval_episodes
        self.eval_interval = eval_interval
        self.num_test_episodes = 1000

        self.env, self.train_env, self.eval_env = self.create_minesweeper_env()
        self.agent, self.optimizer = self.create_agent_and_optimizer()
        self.replay_buffer, self.collect_driver = self.create_replay_buffer_and_collect_driver()

    def get_available_gpus(self):
        return len(tf.config.list_physical_devices('GPU'))

    def create_minesweeper_env(self):
        env = MinesweeperEnv(15, 15, 80)
        train_env = tf_py_environment.TFPyEnvironment(env)
        eval_env = tf_py_environment.TFPyEnvironment(env)
        return env, train_env, eval_env

    def create_agent_and_optimizer(self):
        fc_layer_params = (100, 50)
        q_net = q_network.QNetwork(self.train_env.observation_spec(),
                                   self.train_env.action_spec(),
                                   fc_layer_params=fc_layer_params)
        optimizer = tf.keras.optimizers.Adam(learning_rate=self.learning_rate)
        train_step_counter = tf.Variable(0)
        agent = dqn_agent.DqnAgent(self.train_env.time_step_spec(),
                                   self.train_env.action_spec(),
                                   q_network=q_net,
                                   optimizer=optimizer,
                                   td_errors_loss_fn=common.element_wise_squared_loss,
                                   train_step_counter=train_step_counter)
        agent.initialize()
        return agent, optimizer

    def create_replay_buffer_and_collect_driver(self):
        replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(
            data_spec=self.agent.collect_data_spec,
            batch_size=self.train_env.batch_size,
            max_length=self.replay_buffer_max_length)
        collect_driver = dynamic_step_driver.DynamicStepDriver(
            self.train_env,
            self.agent.collect_policy,
            observers=[replay_buffer.add_batch],
            num_steps=self.collect_steps_per_iteration)

        # Create the iterator from the replay buffer dataset
        dataset = replay_buffer.as_dataset(
            num_parallel_calls=3,
            sample_batch_size=self.batch_size,
            num_steps=2
        ).prefetch(3)
        self.iterator = iter(dataset)

        return replay_buffer, collect_driver

    def test_agent(self, num_episodes, render=True):
        total_reward = 0

        for episode in range(num_episodes):
            time_step = self.eval_env.reset()
            policy_state = self.agent.policy.get_initial_state(
                self.eval_env.batch_size)
            episode_reward = 0

            if render:
                # Create a new Tkinter root and GUI for the test environment
                test_root = tk.Tk()
                test_root.title("Test Environment")
                test_gui = MinesweeperGUI(self.eval_env.pyenv.envs[0])
                test_gui.update()
                test_root.update()

            while not time_step.is_last():
                action_step = self.agent.policy.action(time_step, policy_state)
                action = action_step.action.numpy()[0]

                if render:
                    test_gui.update(action)
                    test_root.update()

                time_step = self.eval_env.step(action_step.action)
                episode_reward += time_step.reward.numpy().sum()

            total_reward += episode_reward

            if render:
                # Close the Tkinter root after the episode
                test_root.destroy()

        return total_reward / num_episodes

    def initial_data_collection(self):
        time_step = self.train_env.current_time_step()
        policy_state = self.agent.collect_policy.get_initial_state(
            self.train_env.batch_size)

        for _ in range(self.initial_collect_steps):
            action_step = self.agent.collect_policy.action(
                time_step, policy_state)
            next_time_step = self.train_env.step(action_step.action)
            traj = trajectory.from_transition(
                time_step, action_step, next_time_step)
            self.replay_buffer.add_batch(traj)
            time_step = next_time_step
            policy_state = action_step.state

    def train(self, root=None, gui=None, render=True):
        if render:
            if root is None and gui is None:
                root = tk.Tk()
                root.title("Testing Window")

                gui = MinesweeperGUI(self.train_env.pyenv.envs[0])
            gui.update()
            root.update()

        # Check if the replay buffer has enough data
        if self.replay_buffer.num_frames() < 1000:  # Replace 100 with the desired minimum number of experiences
            return None

        # Get the next experience from the iterator
        experience, _ = next(self.iterator)

        # Train the agent
        train_loss = self.agent.train(experience)

        # Return the loss_info object
        return train_loss

    def run(self):
        print("Num GPUs Available: ", self.get_available_gpus())

        # Initial data collection
        print("Initial data collection")
        self.initial_data_collection()

        # Initialize root and gui variables
        root = None
        gui = None

        if True:  # Set to True if you want to render the GUI during training
            root = tk.Tk()
            root.title("Testing Window")
            gui = MinesweeperGUI(self.train_env.pyenv.envs[0])

        # Main loop
        print("Main loop")
        self.num_iterations = 1000
        for iteration in range(self.num_iterations):
            print(f"Iteration: {iteration}")
            initial_time_step = self.train_env.current_time_step()
            initial_policy_state = self.agent.collect_policy.get_initial_state(
                self.train_env.batch_size)
            max_iterations = self.collect_steps_per_iteration
            self.collect_driver.run(time_step=initial_time_step,
                                    policy_state=initial_policy_state, maximum_iterations=max_iterations)

            experience, _ = next(iter(self.replay_buffer.as_dataset(
                num_parallel_calls=3, sample_batch_size=self.batch_size, num_steps=2).take(1)))

            train_loss = self.train(root=root, gui=gui).loss

            step = self.agent.train_step_counter.numpy()

            if step % self.log_interval == 0:
                print('step = {0}: loss = {1}'.format(step, train_loss))

            if step % self.eval_interval == 0:
                avg_return = compute_avg_return(
                    self.eval_env, self.agent.policy, self.num_eval_episodes)

                print('step = {0}: Average Return = {1}'.format(
                    step, avg_return))

        # Testing the agent
        avg_test_reward = self.test_agent(self.num_test_episodes)
        print(
            f'Average reward over {self.num_test_episodes} episodes: {avg_test_reward}')


def main():
    # Hyperparameters
    num_iterations = 50000
    initial_collect_steps = 1000
    collect_steps_per_iteration = 100
    replay_buffer_max_length = 10000
    batch_size = 64
    learning_rate = 1e-3
    log_interval = 200
    num_eval_episodes = 120
    eval_interval = 100
    num_test_episodes = 1000

    # Create an instance of the MinesweeperAgent class
    minesweeper_agent = MinesweeperAgent(num_iterations,
                                         initial_collect_steps,
                                         collect_steps_per_iteration,
                                         replay_buffer_max_length,
                                         batch_size,
                                         learning_rate,
                                         log_interval,
                                         num_eval_episodes,
                                         eval_interval)

    # Run the agent
    minesweeper_agent.run()


if __name__ == "__main__":
    main()
