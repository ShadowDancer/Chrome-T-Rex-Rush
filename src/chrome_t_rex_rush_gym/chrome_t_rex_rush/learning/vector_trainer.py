import numpy as np
import tensorflow as tf
import gym

from envs.t_rex_env import TRexEnvVector
from learning.trainer import run_agent
from learning.dqn_agent import QNetworkAgent



#env = TRexEnvVector()


name = 'CartPole-v0'

env =  gym.make(name)


model = QNetworkAgent(name, env.observation_space, env.action_space)

run_agent(model, env, 100000)
#run_agent(model, env, 100000, visualize='human', learn=False)