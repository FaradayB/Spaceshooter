from msilib.schema import Class
from pickle import TRUE
from tkinter.font import BOLD
import pygame
import os
import random
import sys

pygame.font.init()

WIDTH, HEIGHT = 1000,1000
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spacegame thingy")

# image load
MAIN_SHIP = pygame.image.load(os.path.join("assets", "mainshipog.png"))

ENEMY_SHIP1 = pygame.image.load(os.path.join("assets","Enemyship1.png"))
ENEMY_SHIP2 = pygame.image.load(os.path.join("assets","Enemyship2.png"))

LASER_MAIN_SHIP = pygame.image.load(os.path.join("assets","laserplayer.png"))
LASER_ENEMY1_SHIP = pygame.image.load(os.path.join("assets","laserenemy.png"))
LASER_ENEMY2_SHIP = pygame.image.load(os.path.join("assets","laserenemy.png"))

# image obstacles
METEOR = pygame.image.load(os.path.join("assets", "meteor-export.png"))

# image background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets","2773642.png")),(WIDTH,HEIGHT))

class Button():
	def __init__(self, image, pos, text_input, font, base_color, hovering_color):
		self.image = image
		self.x_pos = pos[0]
		self.y_pos = pos[1]
		self.font = font
		self.base_color, self.hovering_color = base_color, hovering_color
		self.text_input = text_input
		self.text = self.font.render(self.text_input, True, self.base_color)
		if self.image is None:
			self.image = self.text
		self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
		self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

	def update(self, screen):
		if self.image is not None:
			screen.blit(self.image, self.rect)
		screen.blit(self.text, self.text_rect)

	def checkForInput(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			return True
		return False

	def changeColor(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			self.text = self.font.render(self.text_input, True, self.hovering_color)
		else:
			self.text = self.font.render(self.text_input, True, self.base_color)

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class Ship:
    COOLDOWN = 10
    
    def __init__(self, x, y, health = 100):
        self.x = x 
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
        
    def draw(self,window):
        window.blit(self.ship_img, (self.x,self.y))
        for laser in self.lasers:
            laser.draw(window)
    
    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)          
    
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1
    
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser( self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
    
    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()
    
class Enemy(Ship):
    COLOR_MAP = { "red" : (ENEMY_SHIP1, LASER_ENEMY1_SHIP), "blue" : (ENEMY_SHIP2, LASER_ENEMY2_SHIP)}
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y + 70, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

class Rock:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.meteor_img = METEOR
        self.mask = pygame.mask.from_surface(self.meteor_img)
    
    def draw(self,window):
        window.blit(self.meteor_img,(self.x,self.y))
    
    def move(self,vel):
        self.y += vel
    
    def get_height(self):
        return self.meteor_img.get_height()
        
        
class Player(Ship):
    def __init__(self, x, y, health = 100):
        super().__init__(x,y, health)
        self.ship_img = MAIN_SHIP
        self.laser_img = LASER_MAIN_SHIP
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
    
    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
        
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

                

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x     
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask,(offset_x, offset_y)) != None

def main():
    run = True
    FPS = 75
    lives = 3
    level = 0
    main_font = pygame.font.SysFont("arial",50,BOLD)
    lost_font = pygame.font.SysFont("arial",80,BOLD)
    
    rocks = []
    wave_lenght_rock = 2
    rock_vel = 1
    
    enemies = []
    wave_lenght_enemy = 4
    enemy_vel = 1
    enemy_laser_vel = 2
    
    player_vel = 8
    laser_vel = 5
    
    player = Player(450,800)
    
    clock = pygame.time.Clock()
    
    lost = False
    lost_count = 0
    
    def redraw_window():
        WIN.blit(BG,(0,0))
        
        lives_label = main_font.render(f"Lives : {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        
        WIN.blit(lives_label,(10,10))
        WIN.blit(level_label,(WIDTH - level_label.get_width() - 10, 10))
        
        player.draw(WIN)
        
        for rock in rocks:
            rock.draw(WIN)
        
        for enemy in enemies:
            enemy.draw(WIN)
            
        
        
        if lost:
            lost_label = lost_font.render("GAME OVER", 1, (255,255,255))
            WIN.fill((0,0,0))
            WIN.blit(lost_label,(WIDTH/2 - lost_label.get_width()/2, 500))
        
        pygame.display.update()
    
    while run:
        clock.tick(FPS)
        redraw_window()
        
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
            
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue
        
        if len(rocks) == 0:
            wave_lenght_rock += 1
            rock_vel += 1
            for i in range(wave_lenght_rock):
                rocky = Rock(random.randrange(50, WIDTH-100), random.randrange(-1500, -100))
                rocks.append(rocky)
        
        if len(enemies) == 0:
            wave_lenght_enemy += 1
            enemy_vel += 0.5
            level += 1
            for i in range(wave_lenght_enemy):
                enemy = Enemy(random.randrange(10, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue"]))
                enemies.append(enemy)
        
        for event in pygame.event.get():
            if  event.type == pygame.QUIT:
                run = False
                
        keys = pygame.key.get_pressed()
        if keys [pygame.K_a] or keys [pygame.K_LEFT]:
            if player.x - player_vel > 0 :
                player.x -= player_vel
        if keys [pygame.K_d] or keys [pygame.K_RIGHT]:
            if player.x + player_vel  + player.get_width() < WIDTH :
                player.x += player_vel
        if keys [pygame.K_w] or keys [pygame.K_UP]:
            player.shoot()
        
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(enemy_laser_vel * 1.5 , player)
            
            if random.randrange(0, 2*60) == 1:
                enemy.shoot()
                
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
                
            elif enemy.y + enemy.get_height() > HEIGHT :
                lives -= 1
                enemies.remove(enemy)
                
        player.move_lasers(-laser_vel, enemies)
             
        for rock in rocks[:]:
            rock.move(rock_vel)
            
            if collide(rock, player):
                player.health -= 5
                rocks.remove(rock)
            elif rock.y + rock.get_height() > HEIGHT:
                rocks.remove(rock)


def get_font(size):
    return pygame.font.Font("assets_button/font.ttf", size)

def main_menu():
    while True:
        WIN.fill((0,0,0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(60).render("SPACE SHOOTER", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(500, 100))

        PLAY_BUTTON = Button(image=pygame.image.load("assets_button/Play Rect.png"), pos=(500, 350), 
                            text_input="PLAY", font=get_font(45), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("assets_button/Quit Rect.png"), pos=(500, 550), 
                            text_input="QUIT", font=get_font(45), base_color="#d7fcd4", hovering_color="White")

        WIN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(WIN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    main()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

main_menu()