"""Dino game from chrome"""
__author__ = "Shivam Shekhar,ShadowDancer"

import pygame

import game_state as gs
from game_state import Actions

pygame.init()
SCR_SIZE = (WIDTH, HEIGHT) = (600, 150)
SCREEN = pygame.display.set_mode(SCR_SIZE)

import actors
actors.WIDTH = WIDTH
actors.HEIGHT = HEIGHT
actors.SCREEN = SCREEN

gs.WIDTH = WIDTH
gs.HEIGHT = HEIGHT
gs.SCREEN = SCREEN

FPS = 60

CLOCK = pygame.time.Clock()
pygame.display.set_caption("T-Rex Rush")

class KeyboardController:
    """Translates input from keyboard into game actions"""\

    def get_action(self):
        """Returns action for game to execute"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            return Actions.QUIT
        if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_RETURN] or keys[pygame.K_w]:
            return Actions.JUMP
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            return Actions.DUCK
        return Actions.NOOP

class Game:
    """Responsible for managing game states and game loop"""
    def __init__(self, instrumented=False):

        if not instrumented:
            self.controller = KeyboardController()

        self.state = gs.IntroState()
        self.is_game_quit = False

    def run(self):
        """Game loop"""
        if pygame.display.get_surface() is None:
            print("Couldn't load display surface")
            self.is_game_quit = True

        while not self.is_game_quit:
                CLOCK.tick_busy_loop(FPS)

            self.handle_pygame_evens()
            action = self.get_action()

            if not self.is_game_quit:
                self.state.update(action)
                self.state.draw()
                if self.state.finished:
                    if isinstance(self.state, gs.GameState):
                        self.state = gs.GameOverState()
                    else:
                        self.state = gs.GameState()
        pygame.quit()
        quit()

    def get_action(self):
        """Reads action from controller and returns it"""
        action = self.controller.get_action()
        if action == Actions.QUIT:
            self.is_game_quit = True
        return action

    def handle_pygame_evens(self):
        """Handle gamequit event (ie. someone closed window)"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_game_quit = True
if __name__ == '__main__':
    Game().run()
