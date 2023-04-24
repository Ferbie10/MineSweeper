from tf_agents.agents.dqn import dqn_agent
from tf_agents.networks import q_network
from tf_agents.environments import tf_py_environment
from tf_agents.utils import common
import tensorflow as tf

# Hyperparameters
num_iterations = 20000
initial_collect_steps = 1000
collect_steps_per_iteration = 1
replay_buffer_capacity = 100000
batch_size = 64
learning_rate = 1e-3
log_interval = 200
num_eval_episodes = 10
eval_interval = 1000

# Environment
train_env = tf_py_environment.TFPyEnvironment(MinesweeperPyEnvironment(4, 4, 1))
eval_env = tf_py_environment.TFPyEnvironment(MinesweeperPyEnvironment(4, 4, 1))

# QNetwork
fc_layer_params = (100,)
q_net = q_network.QNetwork(
    train_env.observation_spec(),
    train_env.action_spec(),
    fc_layer_params=fc_layer_params)

# DQNAgent
global_step = tf.Variable(0)
optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
epsilon_fn = tf.keras.optimizers.schedules.PolynomialDecay(
    initial_learning_rate=1.0,  # initial ε
    decay_steps=num_iterations // 2,
    end_learning_rate=0.01)  # final ε

agent = dqn_agent.DqnAgent(
    train_env.time_step_spec(),
    train_env.action_spec(),
    q_network=q_net,
    optimizer=optimizer,
    td_errors_loss_fn=common.element_wise_squared_loss,
    gamma=0.99,  # discount factor
    train_step_counter=global_step,
    epsilon_greedy=lambda: epsilon_fn(global_step))

agent.initialize()