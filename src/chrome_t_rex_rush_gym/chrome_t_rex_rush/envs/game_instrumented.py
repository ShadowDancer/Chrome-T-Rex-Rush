"""Defines instrumented game class"""

import game_state
import pygame

from constants import SCR_SIZE
from resources import Render

pygame.display.init()

class GameInstrumented:
    """Base class for instrumented games"""
    
    def __init__(self):
        self.state = game_state.GameState()
        self.screen = pygame.Surface(SCR_SIZE)
        self.render = Render(self.screen)
        
    def reset(self):
        self.state.reset()

class GameRgbInstrumented(GameInstrumented):
    """Chrome-T-Rex-Game instrumented for RGB display"""

    def __init__(self):
        super().__init__()

    def step(self, action=game_state.Actions.NOOP):
        """Perform action on game, and get picture of game screen, information if game is finished, and current score"""

        if not self.state.finished:
            self.render.begin()
            self.state.update(action)
            self.state.draw(self.render)
            
        screen = pygame.surfarray.array3d(self.render.surface)
        screen.swapaxes(0,1)
        finished = self.state.finished
        score = self.state._player_dino.score

        return (screen, finished, score, screen)


class GameVectorInstrumented(GameInstrumented):
    """Chrome-T-Rex-Game instrumented for vector with closest obstacles"""
    
    def __init__(self):
        super().__init__()
    def step(self, action=game_state.Actions.NOOP):
        """Perform action on game, and get picture of game screen, information if game is finished, and current score"""

        if not self.state.finished:
            self.render.begin()
            self.state.update(action)
            self.state.draw(self.render)
            
        
        state = self.state
        speed = state.gamespeed
        dino_y = state._player_dino.rect.bottom

        
        actors = []
        for cactus in state._cactus_group:
            actors.append(cactus)
        for ptera in state._pteras_group:
            actors.append(ptera)
        actors.sort(key=lambda x: x.rect.left)

        actor_positions = []
        for actor in actors[:3]:
            actor_positions.append(actor.rect.left)
            actor_positions.append(actor.rect.top)

        while len(actor_positions) < 6:
            actor_positions.append(0)

        observation = [speed, dino_y]
        observation.extend(actor_positions)
        screen = pygame.surfarray.array3d(self.render.surface)
        screen.swapaxes(0,1)
        finished = self.state.finished
        score = self.state._player_dino.score

        return (observation, finished, score, screen)
