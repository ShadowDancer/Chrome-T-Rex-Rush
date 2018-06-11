
import os
import pygame
from pygame import RLEACCEL

BACKGROUND_COLOR = (255, 255, 255)
NUMBER_HEIGHT = int(11*6/5) # wysokość znaku


class Render:
    """Responsible for rendering sprites, allows rendering to image"""

    def __init__(self, surface):
        self.surface = surface

    def begin(self):
        """Begins drawing new frame"""
        self.surface.fill(BACKGROUND_COLOR)

    def blit(self, surface, rect):
        """Blits surface on internal rect"""
        self.surface.blit(surface, rect)

    def draw(self, sprite_group):
        """Draws sprite group on render"""
        sprite_group.draw(self.surface)

def _make_image(size_x=-1, size_y=-1, colorkey=-1):
    """Craetes dictionary with image metadata"""
    return {
        'x': size_x,
        'y' : size_y,
        'colorkey': colorkey
    }
class Images:
    """Image definitions"""
    CLOUD = 'cloud'
    GROUND = 'ground'
    CALL_OUT = 'call_out'
    LOGO = 'logo'
    REPLAY_BUTTON = 'replay_button'
    GAME_OVER = 'game_over'
    data = {
        CLOUD: _make_image(int(90*30/42), 30),
        GROUND: _make_image(),
        CALL_OUT:_make_image(196, 45),
        GAME_OVER: _make_image(190, 11),
        REPLAY_BUTTON: _make_image(35, 31),
        LOGO: _make_image(240, 40)
    }

class Sounds:
    """Sound definitions"""
    JUMP = 'jump'
    DIE = 'die'
    CHECKPOINT = 'checkPoint'

class SpriteSheets:
    """Spritesheet definitions"""
    DINO_RUN = 'dino'
    DINO_DUCK = 'dino_ducking'
    CACTUS = 'cacti-small'
    PTERA = 'ptera'
    NUMBERS = 'numbers'
    GROUND = 'ground'

    data = {
        DINO_RUN: {
            'frames': 5,
            'colorkey': -1
        },
        DINO_DUCK: {
            'frames': 2,
            'colorkey': -1
        },
        CACTUS: {
            'frames': 3,
            'colorkey': -1,
            'x': 3,
            'y': 5
        },
        PTERA: {
            'frames': 2,
            'colorkey': -1
        },
        NUMBERS: {
            'frames': 12,
            'colorkey': -1,
            'x': 11,
            'y': NUMBER_HEIGHT
        },
        GROUND: {
            'colorkey': -1,
            'frames': 15
        }
    }

class DummySound():
    """Special case for sound object if there is no sound initiazlised"""

    def play(self):
        """Nooop"""
        pass

class ResourceManager():
    """Class responsible for loading and storage of resources"""

    def __init__(self):
        self.sheets = {}
        self.images = {}
        self.sounds = {}

    def get_spritesheet(self, spritesheet_id):
        """returns spritesheet from cache or disk"""
        sheet = self.sounds.get(spritesheet_id)
        if not sheet:
            sheet = load_sprite_sheet(spritesheet_id)
            self.sounds[spritesheet_id] = sheet
        return sheet

    def get_sound(self, sound_id):
        """returns sound from cache or disk"""
        if pygame.mixer.get_init() == None:
            return DummySound()

        sound = self.sounds.get(sound_id)
        if not sound:
            sound = load_sound(sound_id)
            self.sounds[sound_id] = sound
        return sound

    def get_image(self, image_id):
        """returns image from cache or disk"""
        img = self.images.get(image_id)
        if not img:
            img = load_image(image_id)
            self.images[image_id] = img
        return img

RESOURCES = ResourceManager()

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

def load_sound(sound_id):
    """Loads sound file from disk"""
    fullname = os.path.join('sprites', sound_id + '.wav')
    return pygame.mixer.Sound(fullname)

def load_sprite_sheet(spritesheet_id):
    """Loads SpriteSheet from file"""
    fullname = os.path.join('sprites', spritesheet_id + '.png')

    data = SpriteSheets.data[spritesheet_id]
    frames_x = data['frames']
    frames_y = 1
    colorkey = data.get('colorkey')

    sheet = pygame.image.load(fullname)
    sheet_rect = sheet.get_rect()
    sprites = []

    size_x = sheet_rect.width/frames_x
    size_y = sheet_rect.height/frames_y
    for i in range(0, frames_y):
        for j in range(0, frames_x):
            rect = pygame.Rect((j*size_x, i*size_y, size_x, size_y))
            image = pygame.Surface(rect.size)
            if pygame.display.get_surface():
                image = image.convert()
            image.blit(sheet, (0, 0), rect)

            if colorkey is not None:
                if colorkey is -1:
                    colorkey = image.get_at((0, 0))
                image.set_colorkey(colorkey, RLEACCEL)

            sprites.append(image)

    size_x = data.get('x', int(size_x))
    size_y = data.get('y', int(size_y))

    return SpriteSheet(sprites).resize(size_x, size_y)

def load_image(image_id):
    """Loads image from file"""
    image_data = Images.data[image_id]
    colorkey = image_data['colorkey']
    sizex = image_data['x']
    sizey = image_data['y']

    fullname = os.path.join('sprites', image_id + '.png')
    image = pygame.image.load(fullname)

    if pygame.display.get_surface():
        image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)

    if sizex != -1 or sizey != -1:
        image = pygame.transform.scale(image, (sizex, sizey))

    return image
