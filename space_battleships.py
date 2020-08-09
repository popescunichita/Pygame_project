import pygame
import os
import time
import random

pygame.font.init()

Black = (0, 0, 0)
White = (255, 255, 255)
Medium_Gray = (128, 128, 128)
Aqua = (0, 128, 128)
Navy_Blue = (0, 0, 128)
Green = (0, 255, 0)
Red = (255, 0, 0)
Orange = (255, 165, 0)
Yellow = (255, 255, 0)

colors_list = [Black, White, Medium_Gray, Aqua, Navy_Blue, Green, Red, Orange, Yellow]

HEIGHT = 1080
WIDTH = 1920

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Battleships")

# Load images

# Enemy ships

ENEMY_NO1 = pygame.image.load(os.path.join("models", "foe1.png"))
ENEMY_NO2 = pygame.image.load(os.path.join("models", "foe2.png"))
ENEMY_NO3 = pygame.image.load(os.path.join("models", "foe3.png"))
BOSS = pygame.image.load(os.path.join("models", "boss1.png"))

# Player ship

MAIN_SHIP = pygame.image.load(os.path.join("models", "my_space_ship.png"))

# Lasers

BLUE_LASER = pygame.image.load(os.path.join("models", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("models", "pixel_laser_yellow.png"))
RED_LASER = pygame.image.load(os.path.join("models", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("models", "pixel_laser_green.png"))

# Background image

BG_1 = pygame.image.load(os.path.join("models", "bg1.jpg"))
BG_2 = pygame.image.load(os.path.join("models", "bg2.jpg"))
BG_3 = pygame.image.load(os.path.join("models", "bg3.jpg"))
BG_4 = pygame.image.load(os.path.join("models", "bg4.jpg"))
MAIN_MENU_IMAGE = pygame.image.load(os.path.join("models", "main_menu.jpg"))
GAME_OVER_IMAGE = pygame.image.load(os.path.join("models", "game_over.jpg"))

backgrounds_list = [BG_1, BG_2, BG_3, BG_4]


# If it's not monitor size use pygame.transform.scale(image,width,height)

class Laser:
    def __init__(self, x_pos, y_pos, img):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x_pos, self.y_pos))

    def move(self, velocity):
        self.y_pos += velocity

    def off_screen(self, height):
        return not (height >= self.y_pos >= 0)

    def collision(self, object):
        return collide(self, object)


class Ship:
    COOLDOWN = 30

    def __init__(self, x_pos, y_pos, health=100):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.health = health
        self.ship_image = None
        self.laser_image = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_image, (self.x_pos, self.y_pos))
        for laser in self.lasers:
            laser.draw(window)

    def get_width(self):
        return self.ship_image.get_width()

    def get_height(self):
        return self.ship_image.get_height()

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def move_lasers(self, velocity, object):
        self.cooldown()
        for laser in self.lasers:
            laser.move(velocity)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(object):
                object.health -= 10
                self.lasers.remove(laser)

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x_pos + 40, self.y_pos - 40, self.laser_image)
            self.lasers.append(laser)
            self.cool_down_counter = 1


class Player(Ship):
    def __init__(self, x_pos, y_pos, health=100):
        super().__init__(x_pos, y_pos, health)
        self.ship_image = MAIN_SHIP
        self.laser_image = BLUE_LASER
        self.mask = pygame.mask.from_surface(self.ship_image)
        self.max_health = health

    def move_lasers(self, velocity, objects):
        self.cooldown()
        for laser in self.lasers:
            laser.move(velocity)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for object in objects:
                    if laser.collision(object):
                        objects.remove(object)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def health_bar(self, window):
        pygame.draw.rect(window, Red,
                         (self.x_pos, self.y_pos + self.ship_image.get_height() + 10, self.ship_image.get_width(), 10))
        pygame.draw.rect(window, Green,
                         (self.x_pos, self.y_pos + self.ship_image.get_height() + 10,
                          self.ship_image.get_width() * (self.health / self.max_health), 10))

    def draw(self, window):
        super().draw(window)
        self.health_bar(window)


class Enemy(Ship):
    COLOR_MAP = {
        "red": (ENEMY_NO1, RED_LASER),
        "yellow": (ENEMY_NO2, YELLOW_LASER),
        "green": (ENEMY_NO3, GREEN_LASER)
    }

    def __init__(self, x_pos, y_pos, color, health=100):
        super().__init__(x_pos, y_pos, health)
        self.ship_image, self.laser_image = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_image)

    def move(self, velocity):
        self.y_pos += velocity

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x_pos, self.y_pos, self.laser_image)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(object1, object2):
    offset_x = object2.x_pos - object1.x_pos
    offset_y = object2.y_pos - object1.y_pos
    return object1.mask.overlap(object2.mask, (offset_x, offset_y)) is not None


def main():
    background = random.choice(backgrounds_list)

    game_over = False
    FPS = 60
    level = 0
    lives = 3

    player_velocity = 15
    player = Player(300, 600)
    enemies = []
    wave_len = 4
    enemy_velocity = 2
    laser_velocity = 4

    main_font = pygame.font.SysFont("comicsans", 50, bold=True)

    clock = pygame.time.Clock()

    lost = False

    def Level():
        WINDOW.blit(background, (0, 0))
        # draw text
        level_label = main_font.render(f"Level: {level}", 1, White)
        lives_label = main_font.render(f"Lives: {lives}", 1, White)

        WINDOW.blit(level_label, (0, 0))
        WINDOW.blit(lives_label, (0, 50))

        player.draw(WINDOW)

        if lost:
            font = pygame.font.SysFont("comicsans", 50, bold=True)
            title_label = font.render('Press ESC to exit !                              Press ENTER to start again !',
                                      1, random.choice(colors_list))
            WINDOW.blit(GAME_OVER_IMAGE, (0, 0))
            WINDOW.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, HEIGHT / 1.2))
            pygame.display.update()
            enemies.clear()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # K_RETURN = carriage return = enter key
                        main()
                    if event.key == pygame.K_ESCAPE:
                        quit()



        for enemy in enemies:
            enemy.draw(WINDOW)

        pygame.display.update()

    while not game_over:
        clock.tick(FPS)
        Level()

        if lives <= 0:
            lost = True
        if lost:
            continue
        if player.health <= 0:
            lives -= 1
            player.health = player.max_health
            Level()

        if player.health <= 0:
            lives -= 1
            Level()

        if len(enemies) == 0:
            level += 1
            wave_len += 2
            for i in range(wave_len):
                enemy = Enemy(random.randrange(50, WIDTH - 50), random.randrange(-HEIGHT - 450, -300),
                              random.choice(["red", "yellow", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            main_menu()

        if keys[pygame.K_LEFT] and player.x_pos - player_velocity > 0:
            player.x_pos -= player_velocity
        if keys[pygame.K_RIGHT] and player.x_pos + player_velocity + player.get_width() < WIDTH:
            player.x_pos += player_velocity
        if keys[pygame.K_UP] and player.y_pos - player_velocity > 0:
            player.y_pos -= player_velocity
        if keys[pygame.K_DOWN] and player.y_pos + player_velocity + player.get_height() + 70 < HEIGHT:
            player.y_pos += player_velocity
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_velocity)
            enemy.move_lasers(laser_velocity, player)

            if random.randrange(0, 6 * FPS) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 25
                enemies.remove(enemy)

            elif enemy.y_pos + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_velocity, enemies)


def main_menu():
    font = pygame.font.SysFont('comicsans', 70, bold=True)

    game_over = False
    while not game_over:
        WINDOW.blit(MAIN_MENU_IMAGE, (0, 0))
        title_label = font.render(f'Press ENTER to begin !', 1, random.choice(colors_list))
        WINDOW.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, HEIGHT / 2.3))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # K_RETURN = carriage return = enter key
                    main()
                if event.key == pygame.K_ESCAPE:
                    quit()


main_menu()
