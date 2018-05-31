"""Module defining actions in game and their behavior"""

import random
import pygame

from resources import NUMBER_HEIGHT, BACKGROUND_COLOR
from resources import RESOURCES, SpriteSheets, Images, Sounds

GRAVITY = 0.6

WIDTH, HEIGHT, SCREEN = 0, 0, None

class Dino():
    """Defines dino and its behiavior"""
    def __init__(self, size_x=-1, size_y=-1):
        dino_sheet = RESOURCES.get_spritesheet(SpriteSheets.DINO_RUN)
        dino_duck_sheet = RESOURCES.get_spritesheet(SpriteSheets.DINO_DUCK)
        self.dino_run = dino_sheet.resize(size_x, size_y)
        self.dino_duck = dino_duck_sheet.resize(59, size_y)
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
        self.checkpoint_sound = RESOURCES.get_sound(Sounds.CHECKPOINT)
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
                    self.checkpoint_sound.play()

        self.counter = (self.counter + 1)

class Cactus(pygame.sprite.Sprite):
    """Deadly cactus"""
    def __init__(self, speed=5, size_x=-1, size_y=-1):
        pygame.sprite.Sprite.__init__(self, self.containers)

        cactus_sheet = RESOURCES.get_spritesheet(SpriteSheets.CACTUS)
        self.cactus_sheet = cactus_sheet.resize(size_x, size_y)
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
        ptera_sheet = RESOURCES.get_spritesheet(SpriteSheets.PTERA)
        self.ptera_sheet = ptera_sheet.resize(size_x, size_y)
        self.rect = self.ptera_sheet.rect.copy()
        self.ptera_height = [HEIGHT*0.20, HEIGHT*0.82, HEIGHT*0.75, HEIGHT*0.60]
        self.rect.centery = self.ptera_height[random.randrange(0, len(self.ptera_height))]
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
        self.image = RESOURCES.get_image('ground')
        self.rect = self.image.get_rect()
        self.rect1 = self.image.get_rect()
        self.rect.bottom = HEIGHT
        self.rect1.bottom = HEIGHT
        self.rect1.left = self.rect.right
        self.speed = speed

    def draw(self):
        """Draw"""
        SCREEN.blit(self.image, self.rect)
        SCREEN.blit(self.image, self.rect1)

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
        self.image = RESOURCES.get_image(Images.CLOUD)
        self.rect = self.image.get_rect()
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
        numbers_sheet = RESOURCES.get_spritesheet(SpriteSheets.NUMBERS)
        self.numbers_sheet = numbers_sheet
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

class Highscoreboard(Scoreboard):
    """Draws highscore caption"""
    def __init__(self, ):
        numbers_sheet = RESOURCES.get_spritesheet(SpriteSheets.NUMBERS)
        Scoreboard.__init__(self, WIDTH*0.78)
        self.hi_image = pygame.Surface((22, NUMBER_HEIGHT))
        self.hi_rect = self.hi_image.get_rect()
        self.hi_rect.top = HEIGHT*0.1
        self.hi_rect.left = WIDTH*0.73
        self.hi_image.fill(BACKGROUND_COLOR)

        # blit images on screen
        letter_rect = numbers_sheet.rect.copy()
        self.hi_image.blit(numbers_sheet.sprites[10], letter_rect)
        letter_rect.left += numbers_sheet.rect.width
        self.hi_image.blit(numbers_sheet.sprites[11], letter_rect)

    def draw(self):
        """Draw HI letters on screen for highscore"""
        SCREEN.blit(self.hi_image, self.hi_rect)
        super().draw()
