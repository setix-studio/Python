import pygame as pg
import csv
import constants as c
from character import Character
from weapon import Weapon
from items import Item
from world import World
import math as m

pg.init()

screen = pg.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
pg.display.set_caption("Dungeon Crawler")

#create clock for maintaining frame rate
clock = pg.time.Clock()

#define game variables
level = 1
start_intro = True
scren_scroll = [0, 0]

#define player movement variables
moving_left = False
moving_right = False
moving_up = False
moving_down = False

#define font
font = pg.font.Font("DungeonCrawler/assets/fonts/AtariClassic.ttf", 20)

#helper function to scale image
def scale_img(image, scale):
  w = image.get_width()
  h = image.get_height()
  return pg.transform.scale(image, (w * scale, h * scale))

#load heart images
heart_empty = scale_img(pg.image.load("DungeonCrawler/assets/images/items/heart_empty.png").convert_alpha(), c.ITEM_SCALE)
heart_half = scale_img(pg.image.load("DungeonCrawler/assets/images/items/heart_half.png").convert_alpha(), c.ITEM_SCALE)
heart_full = scale_img(pg.image.load("DungeonCrawler/assets/images/items/heart_full.png").convert_alpha(), c.ITEM_SCALE)

#load coin images
coin_images = []
for x in range(4):
  img = scale_img(pg.image.load(f"DungeonCrawler/assets/images/items/coin_f{x}.png").convert_alpha(), c.ITEM_SCALE)
  coin_images.append(img)

#load potion image
red_potion = scale_img(pg.image.load("DungeonCrawler/assets/images/items/potion_red.png").convert_alpha(), c.POTION_SCALE)

item_images = []
item_images.append(coin_images)
item_images.append(red_potion)

#load weapon images
bow_image = scale_img(pg.image.load("DungeonCrawler/assets/images/weapons/bow.png").convert_alpha(), c.WEAPON_SCALE)
arrow_image = scale_img(pg.image.load("DungeonCrawler/assets/images/weapons/arrow.png").convert_alpha(), c.WEAPON_SCALE)
fireball_image = scale_img(pg.image.load("DungeonCrawler/assets/images/weapons/fireball.png").convert_alpha(), c.FIREBALL_SCALE)

#load tilemap images
tile_list = []
for x in range(c.TILE_TYPES):
  tile_image = pg.image.load(f"DungeonCrawler/assets/images/tiles/{x}.png").convert_alpha()
  tile_image = pg.transform.scale(tile_image, (c.TILE_SIZE, c.TILE_SIZE))
  tile_list.append(tile_image)

#load character images
mob_animations = []
mob_types = ["elf", "imp", "skeleton", "goblin", "muddy", "tiny_zombie", "big_demon"]

animation_types = ["idle", "run"]
for mob in mob_types:
  #load images
  animation_list = []
  for animation in animation_types:
    #reset temporary list of images
    temp_list = []
    for i in range(4):
      img = pg.image.load(f"DungeonCrawler/assets/images/characters/{mob}/{animation}/{i}.png").convert_alpha()
      img = scale_img(img, c.SCALE)
      temp_list.append(img)
    animation_list.append(temp_list)
  mob_animations.append(animation_list)

#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

#function for displaying game info
def draw_info():
  pg.draw.rect(screen, c.PANEL, (0, 0, c.SCREEN_WIDTH, 50))
  pg.draw.line(screen, c.WHITE, (0, 50), (c.SCREEN_WIDTH, 50))
  #draw lives
  half_heart_drawn = False
  for i in range(5):
    if player.health >= ((i + 1) * 20):
      screen.blit(heart_full, (10 + i * 50, 0))
    elif (player.health % 20 > 0) and half_heart_drawn == False:
      screen.blit(heart_half, (10 + i * 50, 0))
      half_heart_drawn = True
    else:
      screen.blit(heart_empty, (10 + i * 50, 0))

  #level
  draw_text("LEVEL: " + str(level), font, c.WHITE, c.SCREEN_WIDTH / 2, 15)
  #show score
  draw_text(f"X{player.score}", font, c.WHITE, c.SCREEN_WIDTH - 100, 15)

#function to reset level
def reset_level():
  damage_text_group.empty()
  arrow_group.empty()
  item_group.empty()
  fireball_group.empty()

  #create empty tile list
  data = []
  for row in range(c.ROWS):
    r = [-1] * c.COLS
    data.append(r)

  return data

#damage text class
class DamageText(pg.sprite.Sprite):
  def __init__(self, x, y, damage, color):
    pg.sprite.Sprite.__init__(self)
    self.image = font.render(damage, True, color)
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
    self.counter = 0

  def update(self):
    #reposition based on screen scroll
    self.rect.x += screen_scroll[0]
    self.rect.y += screen_scroll[1]
    
    #move damage text up
    self.rect.y -= 1
    #delete the damage text after a few seconds
    self.counter += 1
    if self.counter > 30:
      self.kill()

#class for handling screen fade
class ScreenFade():
  def __init__(self, direction, colour, speed):
    self.direction = direction
    self.colour = colour
    self.speed = speed
    self.fade_counter = 0

  def fade(self):
    fade_complete = False
    self.fade_counter += self.speed
    if self.direction == 1:#whole screen fade
      pg.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, c.SCREEN_WIDTH // 2, c.SCREEN_HEIGHT))
      pg.draw.rect(screen, self.colour, (c.SCREEN_WIDTH // 2 + self.fade_counter, 0, c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
      pg.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, c.SCREEN_WIDTH, c.SCREEN_HEIGHT // 2))
      pg.draw.rect(screen, self.colour, (0, c.SCREEN_HEIGHT // 2 + self.fade_counter, c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
    elif self.direction == 2:#vertical screen fade down
      pg.draw.rect(screen, self.colour, (0, 0, c.SCREEN_WIDTH, 0 + self.fade_counter))

    if self.fade_counter >= c.SCREEN_WIDTH:
      fade_complete = True

    return fade_complete


#create empty tile list
world_data = []
for row in range(c.ROWS):
  r = [-1] * c.COLS
  world_data.append(r)
#load in level data and create world
with open(f"levels/level{level}_data.csv", newline="") as csvfile:
  reader = csv.reader(csvfile, delimiter = ",")
  for x, row in enumerate(reader):
    for y, tile in enumerate(row):
      world_data[x][y] = int(tile)

world = World()
world.process_data(world_data, tile_list, item_images, mob_animations)

#create player
player = world.player
#create player's weapon
bow = Weapon(bow_image, arrow_image)

#extract enemies from world data
enemy_list = world.character_list

#create sprite groups
damage_text_group = pg.sprite.Group()
arrow_group = pg.sprite.Group()
item_group = pg.sprite.Group()
fireball_group = pg.sprite.Group()

score_coin = Item(c.SCREEN_WIDTH - 115, 23, 0, coin_images, True)
item_group.add(score_coin)
#add the items from the level data
for item in world.item_list:
  item_group.add(item)

#create screen fades
intro_fade = ScreenFade(1, c.BLACK, 4)
death_fade = ScreenFade(2, c.PINK, 4)

#main game loop
run = True
while run:

  #control frame rate
  clock.tick(c.FPS)

  screen.fill(c.BG)

  if player.alive:
    #calculate player movement
    dx = 0
    dy = 0
    if moving_right == True:
      dx = c.SPEED
    if moving_left == True:
      dx = -c.SPEED
    if moving_up == True:
      dy = -c.SPEED
    if moving_down == True:
      dy = c.SPEED

    #move player
    screen_scroll, level_complete = player.move(dx, dy, world.obstacle_tiles, world.exit_tile)

    #update all objects
    world.update(screen_scroll)
    for enemy in enemy_list:
      fireball = enemy.ai(player, world.obstacle_tiles, screen_scroll, fireball_image)
      if fireball:
        fireball_group.add(fireball)
      if enemy.alive:
        enemy.update()
    player.update()
    arrow = bow.update(player)
    if arrow:
      arrow_group.add(arrow)
    for arrow in arrow_group:
      damage, damage_pos = arrow.update(screen_scroll, world.obstacle_tiles, enemy_list)
      if damage:
        damage_text = DamageText(damage_pos.centerx, damage_pos.y, str(damage), c.RED)
        damage_text_group.add(damage_text)
    damage_text_group.update()
    fireball_group.update(screen_scroll, player)
    item_group.update(screen_scroll, player)

  #draw player on screen
  world.draw(screen)
  for enemy in enemy_list:
    enemy.draw(screen)
  player.draw(screen)
  bow.draw(screen)
  for arrow in arrow_group:
    arrow.draw(screen)
  for fireball in fireball_group:
    fireball.draw(screen)
  damage_text_group.draw(screen)
  item_group.draw(screen)
  draw_info()
  score_coin.draw(screen)

  #check level complete
  if level_complete == True:
    start_intro = True
    level += 1
    world_data = reset_level()
    #load in level data and create world
    with open(f"levels/level{level}_data.csv", newline="") as csvfile:
      reader = csv.reader(csvfile, delimiter = ",")
      for x, row in enumerate(reader):
        for y, tile in enumerate(row):
          world_data[x][y] = int(tile)
    world = World()
    world.process_data(world_data, tile_list, item_images, mob_animations)
    temp_hp = player.health
    temp_score = player.score
    player = world.player
    player.health = temp_hp
    player.score = temp_score
    enemy_list = world.character_list
    score_coin = Item(c.SCREEN_WIDTH - 115, 23, 0, coin_images, True)
    item_group.add(score_coin)
    #add the items from the level data
    for item in world.item_list:
      item_group.add(item)

  #show intro
  if start_intro == True:
    if intro_fade.fade():
      start_intro = False
      intro_fade.fade_counter = 0

  #show death screen
  if player.alive == False:
    if death_fade.fade():
      death_fade.fade_counter = 0
      start_intro = True
      world_data = reset_level()
      #load in level data and create world
      with open(f"levels/level{level}_data.csv", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter = ",")
        for x, row in enumerate(reader):
          for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
      world = World()
      world.process_data(world_data, tile_list, item_images, mob_animations)
      temp_score = player.score
      player = world.player
      player.score = temp_score
      enemy_list = world.character_list
      score_coin = Item(c.SCREEN_WIDTH - 115, 23, 0, coin_images, True)
      item_group.add(score_coin)
      #add the items from the level data
      for item in world.item_list:
        item_group.add(item)

  #event handler
  for event in pg.event.get():
    if event.type == pg.QUIT:
      run = False
    #take keyboard presses
    if event.type == pg.KEYDOWN:
      if event.key == pg.K_a:
        moving_left = True
      if event.key == pg.K_d:
        moving_right = True
      if event.key == pg.K_w:
        moving_up = True
      if event.key == pg.K_s:
        moving_down = True

    #keyboard button released
    if event.type == pg.KEYUP:
      if event.key == pg.K_a:
        moving_left = False
      if event.key == pg.K_d:
        moving_right = False
      if event.key == pg.K_w:
        moving_up = False
      if event.key == pg.K_s:
        moving_down = False

  pg.display.update()

pg.quit()