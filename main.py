"""Dino game from chrome"""
__author__ = "Shivam Shekhar,ShadowDancer"


import os
import random
import pygame
from pygame import RLEACCEL


pygame.init()

SCR_SIZE = (WIDTH, HEIGHT) = (600, 150)
FPS = 60
GRAVITY = 0.6

BACKGROUND_COLOR = (235, 235, 235)

HIGH_SCORE = 0

SCREEN = pygame.display.set_mode(SCR_SIZE)
CLOCK = pygame.time.Clock()
pygame.display.set_caption("T-Rex Rush")

def load_image(
        name,
        sizex=-1,
        sizey=-1,
        colorkey=None,
    ):
    """Loads image from file"""

    fullname = os.path.join('sprites', name)
    image = pygame.image.load(fullname)
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)

    if sizex != -1 or sizey != -1:
        image = pygame.transform.scale(image, (sizex, sizey))

    return (image, image.get_rect())

class SpriteSheet():
    """Batch of images that can be animatied"""
    def __init__(self, sprites):
        self.sprites = sprites
        self.rect = sprites[0].get_rect()

    def resize(self, size_x=-1, size_y=-1):
        """Returns new spritesheet with scaled images"""
        if size_x == 1 and size_y == 1:
            return self

        new_sprites = []
        for sprite in self.sprites:
            new_sprite = pygame.transform.scale(sprite, (size_x, size_y))
            new_sprites.append(new_sprite)
        return SpriteSheet(new_sprites)

def load_sprite_sheet(filename, frames_x, frames_y=1, colorkey=None):
    """Loads SpriteSheet from file"""
    fullname = os.path.join('sprites', filename)
    sheet = pygame.image.load(fullname)
    sheet = sheet.convert()
    sheet_rect = sheet.get_rect()
    sprites = []

    sizex = sheet_rect.width/frames_x
    sizey = sheet_rect.height/frames_y
    for i in range(0, frames_y):
        for j in range(0, frames_x):
            rect = pygame.Rect((j*sizex, i*sizey, sizex, sizey))
            image = pygame.Surface(rect.size)
            image = image.convert()
            image.blit(sheet, (0, 0), rect)

            if colorkey is not None:
                if colorkey is -1:
                    colorkey = image.get_at((0, 0))
                image.set_colorkey(colorkey, RLEACCEL)

            sprites.append(image)
    return SpriteSheet(sprites)

DINO_RUN_SHEET = load_sprite_sheet('dino.png', 5, colorkey=-1)
DINO_DUCK_SHEET = load_sprite_sheet('dino_ducking.png', 2, colorkey=-1)
CACTUS_SHEET = load_sprite_sheet('cacti-small.png', 3, colorkey=-1)
PTERA_SHEET = load_sprite_sheet('ptera.png', 2, colorkey=-1)
NUMBER_HEIGHT = int(11*6/5)
NUMBERS_SHEET = load_sprite_sheet('numbers.png', 12, colorkey=-1).resize(11, NUMBER_HEIGHT)

JUMP_SOUND = pygame.mixer.Sound('sprites/jump.wav')
DIE_SOUND = pygame.mixer.Sound('sprites/die.wav')
CHECKPOINT_SOUND = pygame.mixer.Sound('sprites/checkPoint.wav')

class Dino():
    """Defines dino and its behiavior"""
    def __init__(self, size_x=-1, size_y=-1):
        self.dino_run = DINO_RUN_SHEET.resize(size_x, size_y)
        self.dino_duck = DINO_DUCK_SHEET.resize(59, size_y)
        self.rect = self.dino_run.rect.copy()
        self.counter = 0 # frame counter
        self.image = None # current frame
        self.index = 0 # frame index
        self.is_jumping = False # airbone
        self.is_dead = False # collision with petra or cactus
        self.is_ducking = False # leans down to avoid petra
        self.is_blinking = False
        self.jump_speed = 11.5
        self.stand_pos_width = self.dino_run.rect.width
        self.duck_pos_width = self.dino_duck.rect.width
        self.reset()

    def reset(self):
        """Restarts state of dino if player dies"""
        self.index = 0
        self.counter = 0
        self.score = 0
        self.is_jumping = False
        self.is_dead = False
        self.is_ducking = False
        self.is_blinking = False
        self.image = self.dino_run.sprites[0]

        # reset dino position
        self.rect.bottom = int(0.98*HEIGHT)
        self.rect.left = WIDTH/15
        self.movement = [0, 0] # reset dino

    def draw(self):
        """Draw itself"""
        SCREEN.blit(self.image, self.rect)

    def checkbounds(self):
        """Check collision with ground"""
        if self.rect.bottom > int(0.98*HEIGHT):
            self.rect.bottom = int(0.98*HEIGHT)
            self.is_jumping = False

    def update(self):
        """Update dino controls"""
        if self.is_jumping:
            self.movement[1] = self.movement[1] + GRAVITY

        if self.is_jumping:
            self.index = 0
        elif self.is_blinking:
            if self.index == 0:
                if self.counter % 400 == 399:
                    self.index = (self.index + 1)%2
            else:
                if self.counter % 20 == 19:
                    self.index = (self.index + 1)%2

        elif self.is_ducking:
            if self.counter % 5 == 0:
                self.index = (self.index + 1)%2
        else:
            if self.counter % 5 == 0:
                self.index = (self.index + 1)%2 + 2

        if self.is_dead:
            self.index = 4

        if not self.is_ducking:
            self.image = self.dino_run.sprites[self.index]
            self.rect.width = self.stand_pos_width
        else:
            self.image = self.dino_duck.sprites[(self.index)%2]
            self.rect.width = self.duck_pos_width

        self.rect = self.rect.move(self.movement)
        self.checkbounds()

        if not self.is_dead and self.counter % 7 == 6 and not self.is_blinking:
            self.score += 1
            if self.score % 100 == 0 and self.score != 0:
                if pygame.mixer.get_init() != None:
                    CHECKPOINT_SOUND.play()

        self.counter = (self.counter + 1)

class Cactus(pygame.sprite.Sprite):
    """Deadly cactus"""
    def __init__(self, speed=5, size_x=-1, size_y=-1):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.cactus_sheet = CACTUS_SHEET.resize(size_x, size_y)
        self.rect = self.cactus_sheet.rect
        self.rect.bottom = int(0.98*HEIGHT)
        self.rect.left = WIDTH + self.rect.width
        self.image = self.cactus_sheet.sprites[random.randrange(0, 3)]
        self.movement = [-1*speed, 0]

    def draw(self):
        """Draw"""
        SCREEN.blit(self.image, self.rect)

    def update(self):
        """Update"""
        self.rect = self.rect.move(self.movement)

        if self.rect.right < 0:
            self.kill()

class Ptera(pygame.sprite.Sprite):
    """Deadly Pterodactylus"""
    def __init__(self, speed=5, size_x=-1, size_y=-1):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.ptera_sheet = PTERA_SHEET.resize(size_x, size_y)
        self.rect = self.ptera_sheet.rect.copy()
        self.ptera_height = [HEIGHT*0.82, HEIGHT*0.75, HEIGHT*0.60]
        self.rect.centery = self.ptera_height[random.randrange(0, 3)]
        self.rect.left = WIDTH + self.rect.width
        self.image = self.ptera_sheet.sprites[0]
        self.movement = [-1*speed, 0]
        self.index = 0
        self.counter = 0

    def draw(self):
        """Draw"""
        SCREEN.blit(self.image, self.rect)

    def update(self):
        """Update"""
        if self.counter % 10 == 0:
            self.index = (self.index+1)%2
        self.image = self.ptera_sheet.sprites[self.index]
        self.rect = self.rect.move(self.movement)
        self.counter = (self.counter + 1)
        if self.rect.right < 0:
            self.kill()


class Ground():
    """Ground stomped by dino"""
    def __init__(self, speed=-5):
        self.image, self.rect = load_image('ground.png', -1, -1, -1)
        self.image1, self.rect1 = load_image('ground.png', -1, -1, -1)
        self.rect.bottom = HEIGHT
        self.rect1.bottom = HEIGHT
        self.rect1.left = self.rect.right
        self.speed = speed

    def draw(self):
        """Draw"""
        SCREEN.blit(self.image, self.rect)
        SCREEN.blit(self.image1, self.rect1)

    def update(self):
        """Update"""
        self.rect.left += self.speed
        self.rect1.left += self.speed

        if self.rect.right < 0:
            self.rect.left = self.rect1.right

        if self.rect1.right < 0:
            self.rect1.left = self.rect.right

class Cloud(pygame.sprite.Sprite):
    """Harmless cloud"""
    def __init__(self, pos_x, pos_y):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image, self.rect = load_image('cloud.png', int(90*30/42), 30, -1)
        self.speed = 1
        self.rect.left = pos_x
        self.rect.top = pos_y
        self.movement = [-1*self.speed, 0]

    def draw(self):
        """Draw"""
        SCREEN.blit(self.image, self.rect)

    def update(self):
        """Update"""
        self.rect = self.rect.move(self.movement)
        if self.rect.right < 0:
            self.kill()

class Scoreboard():
    """Scoreboard displaying player score"""
    def __init__(self, x=-1, y=-1):
        self.score = 0
        self.numbers_sheet = NUMBERS_SHEET
        self.image = pygame.Surface((55, NUMBER_HEIGHT))
        self.rect = self.image.get_rect()
        if x == -1:
            self.rect.left = WIDTH*0.89
        else:
            self.rect.left = x
        if y == -1:
            self.rect.top = HEIGHT*0.1
        else:
            self.rect.top = y

    def extract_digits(self, number):
        """Int to array of ints representing that number"""
        if number > -1:
            digits = []
            while number/10 != 0:
                digits.append(number%10)
                number = int(number/10)

            digits.append(number%10)
            for _ in range(len(digits), 5):
                digits.append(0)
            digits.reverse()
            return digits
        return []

    def draw(self):
        """Draw"""
        SCREEN.blit(self.image, self.rect)

    def update(self, score):
        """Update"""
        score_digits = self.extract_digits(score)
        self.image.fill(BACKGROUND_COLOR)
        for digit in score_digits:
            self.image.blit(self.numbers_sheet.sprites[digit], self.numbers_sheet.rect)
            self.numbers_sheet.rect.left += self.numbers_sheet.rect.width
        self.numbers_sheet.rect.left = 0


def introscreen():
    """Display introscreen and allow player to jump before starting"""
    temp_dino = Dino(44, 47)
    temp_dino.is_blinking = True
    game_start = False

    callout, callout_rect = load_image('call_out.png', 196, 45, -1)
    callout_rect.left = WIDTH*0.05
    callout_rect.top = HEIGHT*0.4

    ground_sheet = load_sprite_sheet('ground.png', 15, colorkey=-1)
    ground_sheet.rect.left = WIDTH/20
    ground_sheet.rect.bottom = HEIGHT

    logo, logo_rect = load_image('logo.png', 240, 40, -1)
    logo_rect.centerx = WIDTH*0.6
    logo_rect.centery = HEIGHT*0.6
    while not game_start:
        if pygame.display.get_surface() is None:
            print("Couldn't load display surface")
            return
        else:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP\
                        and not temp_dino.is_jumping:
                        temp_dino.is_jumping = True
                        temp_dino.is_blinking = False
                        temp_dino.movement[1] = -1*temp_dino.jump_speed

        temp_dino.update()

        if pygame.display.get_surface() != None:
            SCREEN.fill(BACKGROUND_COLOR)
            SCREEN.blit(ground_sheet.sprites[0], ground_sheet.rect)
            if temp_dino.is_blinking:
                SCREEN.blit(logo, logo_rect)
                SCREEN.blit(callout, callout_rect)
            temp_dino.draw()

            pygame.display.update()

        CLOCK.tick(FPS)
        if not temp_dino.is_jumping and not temp_dino.is_blinking:
            game_start = True

#game over message
RETBUTTON_IMAGE, RETBUTTON_RECT = load_image('replay_button.png', 35, 31, -1)
GAMEOVER_IMAGE, GAMEOVER_RECT = load_image('game_over.png', 190, 11, -1)
RETBUTTON_RECT = RETBUTTON_IMAGE.get_rect()
RETBUTTON_RECT.centerx = WIDTH / 2
RETBUTTON_RECT.top = HEIGHT*0.52
GAMEOVER_RECT = GAMEOVER_IMAGE.get_rect()
GAMEOVER_RECT.centerx = WIDTH / 2
GAMEOVER_RECT.centery = HEIGHT*0.35

class HighscoreCaption(Scoreboard):
    """Draws highscore caption"""
    def __init__(self, ):
        Scoreboard.__init__(self, WIDTH*0.78)
        self.hi_image = pygame.Surface((22, NUMBER_HEIGHT))
        self.hi_rect = self.hi_image.get_rect()
        self.hi_rect.top = HEIGHT*0.1
        self.hi_rect.left = WIDTH*0.73
        self.hi_image.fill(BACKGROUND_COLOR)

        # blit images on screen
        letter_rect = NUMBERS_SHEET.rect.copy()
        self.hi_image.blit(NUMBERS_SHEET.sprites[10], letter_rect)
        letter_rect.left += NUMBERS_SHEET.rect.width
        self.hi_image.blit(NUMBERS_SHEET.sprites[11], letter_rect)

    def draw(self):
        """Draw HI letters on screen for highscore"""
        SCREEN.blit(self.hi_image, self.hi_rect)
        super().draw()

class GameState:
    """Manages game"""
    def __init__(self, show_high_score=True):
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


        self.speedup_counter = 0 # counter controlling speed increase
        #states
        self.is_game_over = False
        self.is_game_quit = False
        # scoreborads
        self._score_board = Scoreboard()
        self._highscore_board = HighscoreCaption()
        self.ground = Ground()
        self.reset()

    def reset(self):
        """Resets game to initial state ie player died and we need to start over"""
        self.gamespeed = 4
        self.ground.speed = -1*self.gamespeed
        self.is_game_over = False
        self.is_game_quit = False
        self.speedup_counter = 0

        self._cactus_group.empty()
        self._clouds_group.empty()
        self._pteras_group.empty()
        self._last_obstacle.empty()
        self._player_dino.reset()

    def handle_events(self):
        """Reads collection of pygame input and reacts"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_game_quit = True
                self.is_game_over = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if self._player_dino.rect.bottom == int(0.98*HEIGHT):
                        self._player_dino.is_jumping = True
                        if pygame.mixer.get_init() != None:
                            JUMP_SOUND.play()
                        self._player_dino.movement[1] = -1*self._player_dino.jump_speed

                if event.key == pygame.K_DOWN:
                    if not (self._player_dino.is_jumping and self._player_dino.is_dead):
                        self._player_dino.is_ducking = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    self._player_dino.is_ducking = False

    def kill_player(self):
        """Routine that marks players as dead, computes score, plays sounds tec."""
        global HIGH_SCORE
        if self.is_game_over:
            return
        self._player_dino.is_dead = True
        self._player_dino.is_ducking = False
        self.is_game_over = True
        if self._player_dino.score > HIGH_SCORE:
            HIGH_SCORE = self._player_dino.score
        if pygame.mixer.get_init() != None:
            DIE_SOUND.play()

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

    def update(self):
        """Update game and all entities"""
        self._player_dino.update()
        self._cactus_group.update()
        self._pteras_group.update()
        self._clouds_group.update()
        self.ground.update()
        self._score_board.update(self._player_dino.score)
        self._highscore_board.update(HIGH_SCORE)

        if self.speedup_counter%700 == 699:
            self.ground.speed -= 1
            self.gamespeed += 1
        self.speedup_counter = (self.speedup_counter + 1)

    def draw(self):
        """Draw all entities"""
        if pygame.display.get_surface() != None:
            SCREEN.fill(BACKGROUND_COLOR)
            self.ground.draw()
            self._clouds_group.draw(SCREEN)
            self._score_board.draw()
            if HIGH_SCORE != 0:
                self._highscore_board.draw()
            self._cactus_group.draw(SCREEN)
            self._pteras_group.draw(SCREEN)
            self._player_dino.draw()

            pygame.display.update()

    def display_game_over(self):
        """Display restart prompt"""
        if pygame.display.get_surface() is None:
            print("Couldn't load display surface")
            self.is_game_quit = True
            self.is_game_over = False
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_game_quit = True
                    self.is_game_over = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.is_game_quit = True
                        self.is_game_over = False
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.is_game_over = False
                        self.reset()
        self._highscore_board.update(HIGH_SCORE)
        if pygame.display.get_surface() != None:
            # game over message
            SCREEN.blit(RETBUTTON_IMAGE, RETBUTTON_RECT)
            SCREEN.blit(GAMEOVER_IMAGE, GAMEOVER_RECT)
            if HIGH_SCORE != 0:
                self._highscore_board.draw()
            pygame.display.update()

    def run(self):
        """Game loop"""
        global HIGH_SCORE
        while not self.is_game_quit:
            CLOCK.tick(FPS)
            if self.is_game_over:
                self.display_game_over()

            else:
                if pygame.display.get_surface() is None:
                    print("Couldn't load display surface")
                    self.is_game_quit = True
                    self.is_game_over = True
                else:
                    self.handle_events()
                self.check_collisions()
                self.update()
                self.draw()

        pygame.quit()
        quit()

def main():
    """Runs intro, then game"""
    introscreen()
    GameState().run()

if __name__ == '__main__':
    main()
