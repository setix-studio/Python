from typing import Any
import pygame as pg
import math as m
import constants as c
import random as r

class Weapon():
    def __init__(self, image, arrow_image):
        self.original_image = image
        self.angle = 0
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.arrow_image = arrow_image
        self.rect = self.image.get_rect()
        self.fired = False
        self.last_shot = pg.time.get_ticks()

    def update(self, player):
        shot_cooldown = 300
        arrow = None

        self.rect.center = player.rect.center

        pos = pg.mouse.get_pos()
        x_dist = pos[0] - self.rect.centerx
        y_dist = -(pos[1] - self.rect.centery)
        self.angle = m.degrees(m.atan2(y_dist, x_dist))

        #get mouse clicks
        if pg.mouse.get_pressed()[0] and self.fired == False and (pg.time.get_ticks() - self.last_shot) >= shot_cooldown:
            arrow = Arrow(self.arrow_image, self.rect.centerx, self.rect.centery, self.angle)
            self.fired = True
            self.last_shot = pg.time.get_ticks()
        #reset mouseclick
        if pg.mouse.get_pressed()[0] == False:
            self.fired = False
        return arrow
    
    def draw(self, surface):
        self.image = pg.transform.rotate(self.original_image, self.angle)
        surface.blit(self.image, ((self.rect.centerx - int(self.image.get_width()/2)), (self.rect.centery - int(self.image.get_height()/2))))


class Arrow(pg.sprite.Sprite):
    def __init__(self, image, x, y, angle):
        pg.sprite.Sprite.__init__(self)
        self.original_image = image
        self.angle = angle
        self.image = pg.transform.rotate(self.original_image, self.angle - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        #calculate h and v speed based on angle
        self.dx  = m.cos(m.radians(self.angle)) * c.ARROW_SPEED
        self.dy = -(m.sin(m.radians(self.angle)) * c.ARROW_SPEED) # negative because y increases down the screen

    def update(self, screen_scroll, obstacle_tiles, enemy_list):
        #reset vars
        damage = 0
        damage_pos = None

        #reposition based on angle
        self.rect.x += screen_scroll[0] + self.dx
        self.rect.y += screen_scroll[1] + self.dy

        #check collision with arrow and tile walls
        for obstacle in obstacle_tiles:
            if obstacle[1].colliderect(self.rect):
                self.kill()

        #check if arrow is off screen
        if self.rect.right < 0  or self.rect.left > c.SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > c.SCREEN_HEIGHT:
            self.kill()

        #check arrow collision with enemy
        for enemy in enemy_list:
            if enemy.rect.colliderect(self.rect) and enemy.alive:
                damage = 10 + r.randint(-5, 5)
                damage_pos = enemy.rect
                enemy.health -= damage
                enemy.hit = True
                self.kill()
                break

        return damage, damage_pos

    def draw(self, surface):
        surface.blit(self.image, ((self.rect.centerx - int(self.image.get_width()/2)), (self.rect.centery - int(self.image.get_height()/2))))

class Fireball(pg.sprite.Sprite):
    def __init__(self, image, x, y, target_x, target_y):
        pg.sprite.Sprite.__init__(self)
        self.original_image = image
        x_dist = (target_x - x)
        y_dist = -(target_y - y)
        self.angle = (m.degrees(m.atan2(y_dist, x_dist)))
        self.image = pg.transform.rotate(self.original_image, self.angle - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        #calculate h and v speed based on angle
        self.dx  = m.cos(m.radians(self.angle)) * c.FIREBALL_SPEED
        self.dy = -(m.sin(m.radians(self.angle)) * c.FIREBALL_SPEED) # negative because y increases down the screen

    def update(self, screen_scroll, player):
        #reposition based on angle
        self.rect.x += screen_scroll[0] + self.dx
        self.rect.y += screen_scroll[1] + self.dy

        #check if fireball is off screen
        if self.rect.right < 0  or self.rect.left > c.SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > c.SCREEN_HEIGHT:
            self.kill()

        #check collision with player
        if player.rect.colliderect(self.rect) and player.hit == False:
            player.hit = True
            player.last_hit = pg.time.get_ticks()
            player.health -= 10
            self.kill()
    def draw(self, surface):
        surface.blit(self.image, ((self.rect.centerx - int(self.image.get_width()/2)), (self.rect.centery - int(self.image.get_height()/2))))
