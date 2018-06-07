"""Gym packing Chrome-T-Rex-Rush to open-ai environment"""


import math
import gym
from gym import spaces, logger
from gym.utils import seeding

import chrome_t_rex_rush.game_instrumented import GameInstrumented
#from Chrome_T_Rex_Rush.game_instrumented import GameInstrumented

import numpy as np

class TRexEnv(gym.Env):
    def __init__(self):
        pass

    def seed(self, seed=None):
        """Sets random state for game operations"""
        pass

    def step(self, action):
        """Pass action to environment, execute one step and return reward"""
        pass

    def reset(self):
        """Restore environemnt to original state. Returns first observations"""
        pass

    def render(self, mode='human'):
        """Render environment"""
        pass
    
    def close(self):
        """Free resources used by environment"""
        pass