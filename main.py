__author__ = "Shivam Shekhar"

import os
import sys
import pygame
import random
from pygame import *

pygame.init()

scr_size = (width,height) = (600,150)
FPS = 60
gravity = 0.6

black = (0,0,0)
white = (255,255,255)
background_col = (235,235,235)

high_score = 0

screen = pygame.display.set_mode(scr_size)
clock = pygame.time.Clock()
pygame.display.set_caption("T-Rex Rush")

jump_sound = pygame.mixer.Sound('sprites/jump.wav')
die_sound = pygame.mixer.Sound('sprites/die.wav')
checkPoint_sound = pygame.mixer.Sound('sprites/checkPoint.wav')

def load_image(
    name,
    sizex=-1,
    sizey=-1,
    colorkey=None,
    ):

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

def load_sprite_sheet(
        sheetname,
        nx,
        ny,
        scalex = -1,
        scaley = -1,
        colorkey = None,
        ):
    fullname = os.path.join('sprites',sheetname)
    sheet = pygame.image.load(fullname)
    sheet = sheet.convert()

    sheet_rect = sheet.get_rect()

    sprites = []

    sizex = sheet_rect.width/nx
    sizey = sheet_rect.height/ny

    for i in range(0,ny):
        for j in range(0,nx):
            rect = pygame.Rect((j*sizex,i*sizey,sizex,sizey))
            image = pygame.Surface(rect.size)
            image = image.convert()
            image.blit(sheet,(0,0),rect)

            if colorkey is not None:
                if colorkey is -1:
                    colorkey = image.get_at((0,0))
                image.set_colorkey(colorkey,RLEACCEL)

            if scalex != -1 or scaley != -1:
                image = pygame.transform.scale(image,(scalex,scaley))

            sprites.append(image)

    sprite_rect = sprites[0].get_rect()

    return sprites,sprite_rect

def disp_gameOver_msg(retbutton_image,gameover_image):
    retbutton_rect = retbutton_image.get_rect()
    retbutton_rect.centerx = width / 2
    retbutton_rect.top = height*0.52

    gameover_rect = gameover_image.get_rect()
    gameover_rect.centerx = width / 2
    gameover_rect.centery = height*0.35

    screen.blit(retbutton_image, retbutton_rect)
    screen.blit(gameover_image, gameover_rect)

def extractDigits(number):
    if number > -1:
        digits = []
        i = 0
        while(number/10 != 0):
            digits.append(number%10)
            number = int(number/10)

        digits.append(number%10)
        for i in range(len(digits),5):
            digits.append(0)
        digits.reverse()
        return digits

class Dino():
    def __init__(self,sizex=-1,sizey=-1):
        self.images,self.rect = load_sprite_sheet('dino.png',5,1,sizex,sizey,-1)
        self.images1,self.rect1 = load_sprite_sheet('dino_ducking.png',2,1,59,sizey,-1)


        self.jumpSpeed = 11.5
        self.stand_pos_width = self.rect.width
        self.duck_pos_width = self.rect1.width
        self.reset();

    def reset(self):
        """Restarts state of dino if player dies"""
        self.index = 0 # frame index
        self.counter = 0 # frmae counter
        self.score = 0
        self.isJumping = False # airbone
        self.isDead = False # collision with petra or cactus
        self.isDucking = False # leans down to avoid petra
        self.isBlinking = False
        self.image = self.images[0]

        # reset dino position
        self.rect.bottom = int(0.98*height)
        self.rect.left = width/15
        self.movement = [0,0] # reset dino

    def draw(self):
        screen.blit(self.image,self.rect)

    def checkbounds(self):
        if self.rect.bottom > int(0.98*height):
            self.rect.bottom = int(0.98*height)
            self.isJumping = False

    def update(self):
        if self.isJumping:
            self.movement[1] = self.movement[1] + gravity

        if self.isJumping:
            self.index = 0
        elif self.isBlinking:
            if self.index == 0:
                if self.counter % 400 == 399:
                    self.index = (self.index + 1)%2
            else:
                if self.counter % 20 == 19:
                    self.index = (self.index + 1)%2

        elif self.isDucking:
            if self.counter % 5 == 0:
                self.index = (self.index + 1)%2
        else:
            if self.counter % 5 == 0:
                self.index = (self.index + 1)%2 + 2

        if self.isDead:
           self.index = 4

        if not self.isDucking:
            self.image = self.images[self.index]
            self.rect.width = self.stand_pos_width
        else:
            self.image = self.images1[(self.index)%2]
            self.rect.width = self.duck_pos_width

        self.rect = self.rect.move(self.movement)
        self.checkbounds()

        if not self.isDead and self.counter % 7 == 6 and self.isBlinking == False:
            self.score += 1
            if self.score % 100 == 0 and self.score != 0:
                if pygame.mixer.get_init() != None:
                    checkPoint_sound.play()

        self.counter = (self.counter + 1)

class Cactus(pygame.sprite.Sprite):
    def __init__(self,speed=5,sizex=-1,sizey=-1):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.images,self.rect = load_sprite_sheet('cacti-small.png',3,1,sizex,sizey,-1)
        self.rect.bottom = int(0.98*height)
        self.rect.left = width + self.rect.width
        self.image = self.images[random.randrange(0,3)]
        self.movement = [-1*speed,0]

    def draw(self):
        screen.blit(self.image,self.rect)

    def update(self):
        self.rect = self.rect.move(self.movement)

        if self.rect.right < 0:
            self.kill()

class Ptera(pygame.sprite.Sprite):
    def __init__(self,speed=5,sizex=-1,sizey=-1):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.images,self.rect = load_sprite_sheet('ptera.png',2,1,sizex,sizey,-1)
        self.ptera_height = [height*0.82,height*0.75,height*0.60]
        self.rect.centery = self.ptera_height[random.randrange(0,3)]
        self.rect.left = width + self.rect.width
        self.image = self.images[0]
        self.movement = [-1*speed,0]
        self.index = 0
        self.counter = 0

    def draw(self):
        screen.blit(self.image,self.rect)

    def update(self):
        if self.counter % 10 == 0:
            self.index = (self.index+1)%2
        self.image = self.images[self.index]
        self.rect = self.rect.move(self.movement)
        self.counter = (self.counter + 1)
        if self.rect.right < 0:
            self.kill()


class Ground():
    def __init__(self,speed=-5):
        self.image,self.rect = load_image('ground.png',-1,-1,-1)
        self.image1,self.rect1 = load_image('ground.png',-1,-1,-1)
        self.rect.bottom = height
        self.rect1.bottom = height
        self.rect1.left = self.rect.right
        self.speed = speed

    def draw(self):
        screen.blit(self.image,self.rect)
        screen.blit(self.image1,self.rect1)

    def update(self):
        self.rect.left += self.speed
        self.rect1.left += self.speed

        if self.rect.right < 0:
            self.rect.left = self.rect1.right

        if self.rect1.right < 0:
            self.rect1.left = self.rect.right

class Cloud(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.image,self.rect = load_image('cloud.png',int(90*30/42),30,-1)
        self.speed = 1
        self.rect.left = x
        self.rect.top = y
        self.movement = [-1*self.speed,0]

    def draw(self):
        screen.blit(self.image,self.rect)

    def update(self):
        self.rect = self.rect.move(self.movement)
        if self.rect.right < 0:
            self.kill()

class Scoreboard():
    def __init__(self,x=-1,y=-1):
        self.score = 0
        self.tempimages,self.temprect = load_sprite_sheet('numbers.png',12,1,11,int(11*6/5),-1)
        self.image = pygame.Surface((55,int(11*6/5)))
        self.rect = self.image.get_rect()
        if x == -1:
            self.rect.left = width*0.89
        else:
            self.rect.left = x
        if y == -1:
            self.rect.top = height*0.1
        else:
            self.rect.top = y

    def draw(self):
        screen.blit(self.image,self.rect)

    def update(self,score):
        score_digits = extractDigits(score)
        self.image.fill(background_col)
        for s in score_digits:
            self.image.blit(self.tempimages[s],self.temprect)
            self.temprect.left += self.temprect.width
        self.temprect.left = 0


def introscreen():
    temp_dino = Dino(44,47)
    temp_dino.isBlinking = True
    gameStart = False

    callout,callout_rect = load_image('call_out.png',196,45,-1)
    callout_rect.left = width*0.05
    callout_rect.top = height*0.4

    temp_ground,temp_ground_rect = load_sprite_sheet('ground.png',15,1,-1,-1,-1)
    temp_ground_rect.left = width/20
    temp_ground_rect.bottom = height

    logo,logo_rect = load_image('logo.png',240,40,-1)
    logo_rect.centerx = width*0.6
    logo_rect.centery = height*0.6
    while not gameStart:
        if pygame.display.get_surface() == None:
            print("Couldn't load display surface")
            return True
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP and temp_dino.isJumping == False:
                        temp_dino.isJumping = True
                        temp_dino.isBlinking = False
                        temp_dino.movement[1] = -1*temp_dino.jumpSpeed

        temp_dino.update()

        if pygame.display.get_surface() != None:
            screen.fill(background_col)
            screen.blit(temp_ground[0],temp_ground_rect)
            if temp_dino.isBlinking:
                screen.blit(logo,logo_rect)
                screen.blit(callout,callout_rect)
            temp_dino.draw()

            pygame.display.update()

        clock.tick(FPS)
        if temp_dino.isJumping == False and temp_dino.isBlinking == False:
            gameStart = True

#load textures
retbutton_image, retbutton_rect = load_image('replay_button.png',35,31,-1)
gameover_image, gameover_rect = load_image('game_over.png',190,11,-1)
temp_images,temp_rect = load_sprite_sheet('numbers.png',12,1,11,int(11*6/5),-1)
HI_image = pygame.Surface((22,int(11*6/5)))
HI_rect = HI_image.get_rect()
HI_image.fill(background_col)
HI_image.blit(temp_images[10],temp_rect)
temp_rect.left += temp_rect.width
HI_image.blit(temp_images[11],temp_rect)
HI_rect.top = height*0.1
HI_rect.left = width*0.73

class game:
    def __init__(self):
        self.cactus_group = pygame.sprite.Group()
        Cactus.containers = self.cactus_group
        self.pteras_group = pygame.sprite.Group()
        Ptera.containers = self.pteras_group
        self.clouds_group = pygame.sprite.Group()
        Cloud.containers = self.clouds_group
        self.last_obstacle = pygame.sprite.Group()
        #player unit
        self.player_dino = Dino(44,47)

        # scoreborads
        self.scb = Scoreboard()
        self.highsc = Scoreboard(width*0.78)
        self.ground = Ground()
        self.reset()

    def reset(self):
        """Resets game to initial state ie player died and we need to start over"""
        self.gamespeed = 4
        self.ground.speed = -1*self.gamespeed
        self.is_game_over = False
        self.is_game_quit = False
        self.speedup_counter = 0

        self.cactus_group.empty()
        self.clouds_group.empty()
        self.pteras_group.empty()
        self.last_obstacle.empty()
        self.player_dino.reset()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_game_quit = True
                self.is_game_over = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.player_dino.rect.bottom == int(0.98*height):
                        self.player_dino.isJumping = True
                        if pygame.mixer.get_init() != None:
                            jump_sound.play()
                        self.player_dino.movement[1] = -1*self.player_dino.jumpSpeed

                if event.key == pygame.K_DOWN:
                    if not (self.player_dino.isJumping and self.player_dino.isDead):
                        self.player_dino.isDucking = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    self.player_dino.isDucking = False

    def kill_player(self):
        global high_score
        """Routine that marks players as dead, computes score, plays sounds tec."""
        if self.is_game_over:
            return
        self.player_dino.isDead = True
        self.player_dino.isDucking = False
        self.is_game_over = True
        if self.player_dino.score > high_score:
            high_score = self.player_dino.score
        if pygame.mixer.get_init() != None:
            die_sound.play()

    def check_collisions(self):
        for c in self.cactus_group:
            c.movement[0] = -1*self.gamespeed
            if pygame.sprite.collide_mask(self.player_dino,c):
               self.kill_player()
        for p in self.pteras_group:
            p.movement[0] = -1*self.gamespeed
            if pygame.sprite.collide_mask(self.player_dino,p):
                self.kill_player()
        if len(self.cactus_group) < 2:
            if len(self.cactus_group) == 0:
                self.last_obstacle.empty()
                self.last_obstacle.add(Cactus(self.gamespeed,40,40))
            else:
                for l in self.last_obstacle:
                    if l.rect.right < width*0.7 and random.randrange(0,50) == 10:
                        self.last_obstacle.empty()
                        self.last_obstacle.add(Cactus(self.gamespeed, 40, 40))

        if len(self.pteras_group) == 0 and random.randrange(0,200) == 10 and self.speedup_counter > 500:
            for l in self.last_obstacle:
                if l.rect.right < width*0.8:
                    self.last_obstacle.empty()
                    self.last_obstacle.add(Ptera(self.gamespeed, 46, 40))

        if len(self.clouds_group) < 5 and random.randrange(0,300) == 10:
            Cloud(width,random.randrange(height/5,height/2))

    def update(self):
        self.player_dino.update()
        self.cactus_group.update()
        self.pteras_group.update()
        self.clouds_group.update()
        self.ground.update()
        self.scb.update(self.player_dino.score)
        self.highsc.update(high_score)

        if self.speedup_counter%700 == 699:
            self.ground.speed -= 1
            self.gamespeed += 1
        self.speedup_counter = (self.speedup_counter + 1)

    def draw(self):
        if pygame.display.get_surface() != None:
            screen.fill(background_col)
            self.ground.draw()
            self.clouds_group.draw(screen)
            self.scb.draw()
            if high_score != 0:
                self.highsc.draw()
                screen.blit(HI_image,HI_rect)
            self.cactus_group.draw(screen)
            self.pteras_group.draw(screen)
            self.player_dino.draw()

            pygame.display.update()

    def display_game_over(self):
        if pygame.display.get_surface() == None:
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
                        self.reset();
        self.highsc.update(high_score)
        if pygame.display.get_surface() != None:
            disp_gameOver_msg(retbutton_image,gameover_image)
            if high_score != 0:
                self.highsc.draw()
                screen.blit(HI_image,HI_rect)
            pygame.display.update()

    def run(self):
        global high_score
        while not self.is_game_quit:
            clock.tick(FPS)
            if self.is_game_over:
                self.display_game_over()

            else:
                if pygame.display.get_surface() == None:
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
    isGameQuit = introscreen()
    if not isGameQuit:
        game().run()

if __name__ == '__main__':
	main()
