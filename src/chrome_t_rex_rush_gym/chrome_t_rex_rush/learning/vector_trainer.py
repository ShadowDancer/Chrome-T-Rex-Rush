import numpy as np
import tensorflow as tf
import gym

from envs.t_rex_env import TRexEnvVector
from learning.trainer import run_agent
from learning.dqn_agent import QNetworkAgent



env = TRexEnvVector()
#env =  gym.make('CartPole-v0')


model = QNetworkAgent(env.observation_space, env.action_space)

run_agent(model, env, 100000, visualize='human')