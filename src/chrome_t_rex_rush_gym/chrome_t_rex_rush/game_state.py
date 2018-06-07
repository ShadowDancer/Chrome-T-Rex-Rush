"""Implements various game states"""
import random
import pygame

from constants import WIDTH, HEIGHT
from resources import RESOURCES, SpriteSheets, Images, Sounds, BACKGROUND_COLOR

from actors import Dino, Cactus, Ptera, Cloud, Ground, Scoreboard, Highscoreboard


HIGH_SCORE = 0

class Actions:
    """Holds collection of constants representing game actions"""
    NOOP = 0
    JUMP = 1
    DUCK = 2
    QUIT = 100

class BaseState():
    """Base class for all game states"""

    def __init__(self):
        self.finished = False # when gamestate is finished it should be swapped to next one

    def draw(self, render):
        """Prints current state to render"""
        pass

    def update(self, action):
        """Updates game reacting to player actions"""
        pass

class GameState(BaseState):
    """Manages game itself"""
    def __init__(self, show_high_score=True):
        super().__init__()
        self.show_high_score = show_high_score
        #objects
        self._cactus_group = pygame.sprite.Group()
        Cactus.containers = self._cactus_group
        self._pteras_group = pygame.sprite.Group()
        Ptera.containers = self._pteras_group
        self._clouds_group = pygame.sprite.Group()
        Cloud.containers = self._clouds_group
        self._last_obstacle = pygame.sprite.Group()
        #player unit
        self._player_dino = Dino(44, 47)

        self.jump_sound = RESOURCES.get_sound(Sounds.JUMP)
        self.die_sound = RESOURCES.get_sound(Sounds.DIE)

        self.speedup_counter = 0 # counter controlling speed increase
        #states
        self.is_game_over = False
        self.is_game_quit = False
        # scoreborads
        self._score_board = Scoreboard()
        self._highscore_board = Highscoreboard()
        self.ground = Ground()
        self.reset()

    def reset(self):
        """Resets game to initial state ie player died and we need to start over"""
        self.gamespeed = 4
        self.ground.speed = -1*self.gamespeed
        self.is_game_over = False
        self.is_game_quit = False
        self.finished = False
        self.speedup_counter = 0

        self._cactus_group.empty()
        self._clouds_group.empty()
        self._pteras_group.empty()
        self._last_obstacle.empty()
        self._player_dino.reset()

    def handle_events(self, action):
        """Reads collection of pygame input and reacts"""
        if action == Actions.JUMP:
            if self._player_dino.rect.bottom == int(0.98*HEIGHT):
                self._player_dino.is_jumping = True
                self.jump_sound.play()
                self._player_dino.movement[1] = -1*self._player_dino.jump_speed

        if action == Actions.DUCK:
            if not (self._player_dino.is_jumping and self._player_dino.is_dead):
                self._player_dino.is_ducking = True
        else:
            self._player_dino.is_ducking = False

    def kill_player(self):
        """Routine that marks players as dead, computes score, plays sounds tec."""
        global HIGH_SCORE
        if self._player_dino.is_dead:
            return
        self._player_dino.is_dead = True
        self._player_dino.is_ducking = False
        self.is_game_over = True
        self.finished = True
        if self._player_dino.score > HIGH_SCORE:
            HIGH_SCORE = self._player_dino.score
        self.die_sound.play()

    def check_collisions(self):
        """Check collisions between petras,cactuses and player dino"""
        for cactus in self._cactus_group:
            cactus.movement[0] = -1*self.gamespeed
            if pygame.sprite.collide_mask(self._player_dino, cactus):
                self.kill_player()
        for ptera in self._pteras_group:
            ptera.movement[0] = -1*self.gamespeed
            if pygame.sprite.collide_mask(self._player_dino, ptera):
                self.kill_player()
        if len(self._cactus_group) < 2:
            if not self._cactus_group:
                self._last_obstacle.empty()
                self._last_obstacle.add(Cactus(self.gamespeed, 40, 40))
            else:
                for obstacle in self._last_obstacle:
                    if obstacle.rect.right < WIDTH*0.7 and random.randrange(0, 50) == 10:
                        self._last_obstacle.empty()
                        self._last_obstacle.add(Cactus(self.gamespeed, 40, 40))

        if not self._pteras_group and random.randrange(0, 200) == 10 and self.speedup_counter > 500:
            for obstacle in self._last_obstacle:
                if obstacle.rect.right < WIDTH*0.8:
                    self._last_obstacle.empty()
                    self._last_obstacle.add(Ptera(self.gamespeed, 46, 40))

        if len(self._clouds_group) < 5 and random.randrange(0, 300) == 10:
            Cloud(WIDTH, random.randrange(HEIGHT/5, HEIGHT/2))

    def update(self, action):
        """Update game and all entities"""
        self.handle_events(action)
        self.check_collisions()

        # update entities
        self._player_dino.update()
        self._cactus_group.update()
        self._pteras_group.update()
        self._clouds_group.update()
        self.ground.update()
        self._score_board.update(self._player_dino.score)
        self._highscore_board.update(HIGH_SCORE)

        # update difficulty
        if self.speedup_counter%700 == 699:
            self.ground.speed -= 1
            self.gamespeed += 1
        self.speedup_counter = (self.speedup_counter + 1)

    def draw(self, render):
        """Draw all entities"""
        render.begin()
        self.ground.draw(render)
        render.draw(self._clouds_group)
        render.draw(self._cactus_group)
        render.draw(self._pteras_group)
        self._player_dino.draw(render)

        self._score_board.draw(render)
        if HIGH_SCORE != 0:
            self._highscore_board.draw(render)

class IntroState(BaseState):
    """State displaying intro for game"""

    def __init__(self):
        super().__init__()
        self.temp_dino = Dino(44, 47)
        self.temp_dino.is_blinking = True

        self.callout = RESOURCES.get_image(Images.CALL_OUT)
        self.callout_rect = self.callout.get_rect()
        self.callout_rect.left = WIDTH*0.05
        self.callout_rect.top = HEIGHT*0.4

        self.ground_sheet = RESOURCES.get_spritesheet(SpriteSheets.GROUND)
        self.ground_sheet.rect.left = WIDTH/20
        self.ground_sheet.rect.bottom = HEIGHT

        self.logo = RESOURCES.get_image(Images.LOGO)
        self.logo_rect = self.logo.get_rect()
        self.logo_rect.centerx = WIDTH*0.6
        self.logo_rect.centery = HEIGHT*0.6

    def update(self, action):
        """Display dino till player jumps, then finish"""
        if not self.temp_dino.is_jumping and action == Actions.JUMP:
            self.temp_dino.is_jumping = True
            self.temp_dino.is_blinking = False
            self.temp_dino.movement[1] = -1*self.temp_dino.jump_speed

        self.temp_dino.update()
        if not self.temp_dino.is_jumping and not self.temp_dino.is_blinking:
            self.finished = True

    def draw(self, render):
        render.begin()
        render.blit(self.ground_sheet.sprites[0], self.ground_sheet.rect)
        if self.temp_dino.is_blinking:
            render.blit(self.logo, self.logo_rect)
            render.blit(self.callout, self.callout_rect)
        self.temp_dino.draw(render)

class GameOverState(BaseState):
    """State displayed when player dies with restart prompt"""
    def __init__(self):
        super().__init__()
        self._highscore_board = Highscoreboard()
        self.retbutton_image = RESOURCES.get_image(Images.REPLAY_BUTTON)
        self.gameover_image = RESOURCES.get_image(Images.GAME_OVER)

        self.retbutton_rect = self.retbutton_image.get_rect()
        self.retbutton_rect.centerx = WIDTH / 2
        self.retbutton_rect.top = HEIGHT*0.52
        self.gameover_rect = self.gameover_image.get_rect()
        self.gameover_rect.centerx = WIDTH / 2
        self.gameover_rect.centery = HEIGHT*0.35

    def update(self, action):
        """Look for restart button"""
        if action == Actions.JUMP:
            self.finished = True

        self._highscore_board.update(HIGH_SCORE)

    def draw(self, render):
        """game over message"""
        render.blit(self.retbutton_image, self.retbutton_rect)
        render.blit(self.gameover_image, self.gameover_rect)
        if HIGH_SCORE != 0:
            self._highscore_board.draw(render)
