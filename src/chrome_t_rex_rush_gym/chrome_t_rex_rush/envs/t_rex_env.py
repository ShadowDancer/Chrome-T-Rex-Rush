"""Gym packing Chrome-T-Rex-Rush to open-ai environment"""


import math
import gym
from gym import spaces, logger
from gym.utils import seeding
from constants import SCR_SIZE
import numpy as np
import pygame

from envs.game_instrumented import GameRgbInstrumented, GameVectorInstrumented

import numpy as np

class TRexEnvBase(gym.Env):
    def __init__(self, game):
        self.game = game

        self.graphics_mode = type(self.game) == GameRgbInstrumented

        self.reward = 0
        self.steps_beyond_done = None
        self.finished = False
        self.observation = None# Last observation

        self.action_space = spaces.Discrete(3)

        self.step_skip = 1 # repeat action n times

        

        # for render
        self.display = None
        self.screen = None
        pass

    def seed(self, seed=None):
        """Sets random state for game operations"""
        pass

    def _transform_observation(self, observation):
        """Converts surface to grayscale np array"""

        
        if not self.graphics_mode:
            return np.array(observation)

        array = np.array(observation)

        # rgb conversion
        array = 0.299 * array[:,:,0] + 0.587 * array[:,:,1] + 0.114 * array[:,:,2]

        # crop screen to square
        stride = 2
        array = array[:array.shape[1] * 2:stride, ::stride]
        return array

    def step(self, action):
        rewards = []
        obs, rew, done, dbg = None, None, None, {}
        for i in range(self.step_skip):
            obs, rew, done, dbg = self.single_step(action)
            rewards.append(rew)
            if done:
                return obs, np.mean(rewards), done, dbg
        return obs, np.mean(rewards), done, dbg


    def single_step(self, action):
        """Pass action to environment, execute one step and return reward"""
        return self.process_step(*self.game.step(action))

    def process_step(self, observation, done, score, screen):
        self.screen = screen
        self.observation = self._transform_observation(observation)
        self.reward = 1
        if done: # game over
            if self.steps_beyond_done == None:
                self.reward = -1 # just died
                self.steps_beyond_done = 0
            else:
                self.reward = 0
                self.steps_beyond_done += 1
                logger.warn("You are calling 'step()' even though this environment has already returned done = True. You should always call 'reset()' once you receive 'done = True' -- any further steps are undefined behavior.")

        return self.observation, self.reward, done, {}

    def reset(self):
        """Restore environemnt to original state. Returns first observations"""
        a, b, c, d = self.process_step(*self.game.reset())
        self.steps_beyond_done = None
        self.reward = 0
        return a, b, c, d

    def render(self, mode='human'):
        """Render environment"""
        
        pygame.time.Clock().tick(60)
        object = self.observation
        if mode == 'human':
            object = self.screen

        if not self.graphics_mode:
            # can't print vector
            return

        if self.observation is None or not self.observation.any():
            return

        if self.display is None:
            pygame.init()
            self.display = pygame.display.set_mode((object.shape[0], object.shape[1]))
            
        surf = pygame.surfarray.make_surface(object)
        self.display.blit(surf, (0, 0))
        pygame.display.update()
        pygame.event.get()

        pass
    
    def close(self):
        """Free resources used by environment"""
        pass


class TRexEnvRgb(TRexEnvBase):
    def __init__(self):
        self.observation_space = gym.spaces.Box(0, 255, SCR_SIZE)
        return super().__init__(GameRgbInstrumented())

    

class TRexEnvVector(TRexEnvBase):
    def __init__(self):
        self.observation_space = gym.spaces.Box(0, 1000, (2 + 2*3,))
        return super().__init__(GameVectorInstrumented())
