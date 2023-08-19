import pygame as pg
import math as m
import weapon as w
import constants as c

class Character():
    def __init__(self, x, y, health, mob_animations, char_type, boss, size):
        self.char_type = char_type
        self.boss = boss
        self.score = 0
        self.flip = False
        self.animation_list = mob_animations[char_type]
        self.frame_index = 0
        self.action = 0 #0:idle, 1:moving
        self.update_time = pg.time.get_ticks()
        self.running = False
        self.health = health
        self.alive = True
        self.hit = False
        self.poison = False
        self.last_hit = pg.time.get_ticks()
        self.last_attack = pg.time.get_ticks()
        self.stunned = False

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = pg.Rect(0, 0, c.TILESIZE * size, c.TILESIZE * size)
        self.rect.center = (x, y)

    def move(self, dx, dy, obstacle_tiles, exit_tile = None):
         screen_scroll = [0, 0]
         level_complete = False
         self.running = False
         
         if dx != 0 or dy != 0:
             self.running = True
         if dx < 0:
             self.flip = True
         if dx > 0:
             self.flip = False
         #control diag speed
         if dx != 0 and dy != 0:
             dx = dx * (m.sqrt(2)/2)
             dy = dy * (m.sqrt(2)/2)
        
         #check for collision with map in x direction
         self.rect.x += dx
         for obstacle in obstacle_tiles:
            if obstacle[1].colliderect(self.rect):
                #check which side collision is from
                if dx > 0:
                    self.rect.right = obstacle[1].left
                if dx < 0:
                    self.rect.left = obstacle[1].right   
         #check for collision with map in y direction
         self.rect.y += dy
         for obstacle in obstacle_tiles:
            if obstacle[1].colliderect(self.rect):
                #check which side collision is from
                if dy > 0:
                    self.rect.bottom = obstacle[1].top
                if dy < 0:
                    self.rect.top = obstacle[1].bottom  
         
         #logic for player
         if self.char_type == 0:
             if exit_tile[1].colliderect(self.rect):
                exit_dist = m.sqrt(((self.rect.centerx - exit_tile[1].centerx) ** 2) + ((self.rect.centery - exit_tile[1].centery) ** 2)) 
                if exit_dist < 20:
                    level_complete = True
                
             #update scroll based on player pos
             #move camera left and right
             if self.rect.right > (c.SCREEN_WIDTH - c.SCROLL_THRESH):
                 screen_scroll[0] = (c.SCREEN_WIDTH - c.SCROLL_THRESH) - self.rect.right
                 self.rect.right = c.SCREEN_WIDTH - c.SCROLL_THRESH
             if self.rect.left < c.SCROLL_THRESH:
                 screen_scroll[0] = c.SCROLL_THRESH - self.rect.left
                 self.rect.left = c.SCROLL_THRESH
             #move camera up and down
             if self.rect.bottom > (c.SCREEN_HEIGHT - c.SCROLL_THRESH):
                 screen_scroll[1] = (c.SCREEN_HEIGHT - c.SCROLL_THRESH) - self.rect.bottom
                 self.rect.bottom = c.SCREEN_HEIGHT - c.SCROLL_THRESH
             if self.rect.top < c.SCROLL_THRESH:
                 screen_scroll[1] = c.SCROLL_THRESH - self.rect.top
                 self.rect.top = c.SCROLL_THRESH
        
         return screen_scroll, level_complete

    def ai(self, player, obstacle_tiles, screen_scroll, fireball_image):
        clipped_line = ()
        stun_cooldown = 500
        fireball = None
        ai_dx = 0
        ai_dy = 0
        #reposition mobs based on screen scroll
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]

        #line of site
        line_of_site = ((self.rect.centerx, self.rect.centery)), ((player.rect.centerx, player.rect.centery))
        #check if line of site passes obstacle tile
        for obstacle in obstacle_tiles:
            if obstacle[1].clipline(line_of_site):
                clipped_line = obstacle[1].clipline(line_of_site)

        #check dist to player
        dist = m.sqrt(((self.rect.centerx - player.rect.centerx) ** 2) + ((self.rect.centery - player.rect.centery) ** 2))
        if not clipped_line and dist > c.RANGE:
            if self.rect.centerx >= player.rect.centerx:
                ai_dx = -c.ENEMY_SPEED
            if self.rect.centerx <= player.rect.centerx:
                ai_dx = c.ENEMY_SPEED
            if self.rect.centery >= player.rect.centery:
                ai_dy = -c.ENEMY_SPEED
            if self.rect.centery <= player.rect.centery:
                ai_dy = c.ENEMY_SPEED
        if self.alive:    
            if not self.stunned:
                self.move(ai_dx, ai_dy, obstacle_tiles)

                #attack player
                if player.hit == False:
                    if dist < c.ATTACK_RANGE:
                        player.health -= 10
                        player.hit = True
                        player.last_hit = pg.time.get_ticks()
                #boss fireballs
                fireball_cooldown = 700
                if self.boss:
                    if dist < 500:
                        if pg.time.get_ticks() - self.last_attack >= fireball_cooldown:
                            fireball = w.Poisonsling(fireball_image, self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery)
                            self.last_attack = pg.time.get_ticks()
                
                
            #check if hit
            if self.hit == True:
                self.hit = False
                self.last_hit = pg.time.get_ticks()
                self.stunned = True
                self.running = False
                self.update_action(0)

            if (pg.time.get_ticks() - self.last_hit) > stun_cooldown:
                self.stunned = False
        return fireball
    
    def update(self):
        if self.health <= 0:
            self.health = 0
            self.update_action(2)#dead
            self.alive = False
        else:
             #check what action player is performing
            if self.running == True:
                self.update_action(1)#run
            else:
                self.update_action(0)#idle
        #timer to reset player taking hit
        hit_cooldown = 1000
        if self.char_type == 0:
            if self.hit == True and (pg.time.get_ticks() - self.last_hit) > hit_cooldown:
                self.hit = False

       

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
        if self.char_type == 0:
            surface.blit(flipped_image, (self.rect.x, self.rect.y - c.SCALE * c.OFFSET))
        else:
            surface.blit(flipped_image, self.rect)
       
        ## draw box ## pg.draw.rect(surface, c.RED, self.rect, 1)