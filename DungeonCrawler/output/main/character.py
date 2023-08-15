import pygame as pg
import math
import constants as c

class Character():
    def __init__(self, x, y, mob_animations, char_type):
        self.char_type = char_type
        self.flip = False
        self.animation_list = mob_animations[char_type]
        self.frame_index = 0
        self.action = 0 #0:idle, 1:moving
        self.update_time = pg.time.get_ticks()
        self.running = False
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = pg.Rect(0, 0, 40, 40)
        self.rect.center = (x, y)

    def move(self, dx, dy):
         self.running = False
         if dx != 0 or dy != 0:
             self.running = True
         if dx < 0:
             self.flip = True
         if dx > 0:
             self.flip = False
         #control diag speed
         if dx != 0 and dy != 0:
             dx = dx * (math.sqrt(2)/2)
             dy = dy * (math.sqrt(2)/2)
             


         self.rect.x += dx
         self.rect.y += dy

    def update(self):
        #check what action player is performing
        if self.running == True:
            self.update_action(1)#run
        else:
            self.update_action(0)#idle

        animation_cooldown = 70
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enough time has passed
        if pg.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pg.time.get_ticks()
        #check if animation has finished
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        #check if new action if different than previous
        if new_action != self.action:
            self.action = new_action
            #update animation settings
            self.frame_index = 0
            self.update_time = pg.time.get_ticks()
            

    def draw(self, surface):
        #flip player
        flipped_image = pg.transform.flip(self.image, self.flip, False)
        #draw player
        surface.blit(flipped_image, self.rect)
        pg.draw.rect(surface, c.RED, self.rect, 1)