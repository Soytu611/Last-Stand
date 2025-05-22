import pygame as py
import os
import math
import random

py.init()
py.mixer.init()

width, height = 1600, 900

WIN = py.display.set_mode((width, height))
py.display.set_caption("Last Stand")
clock = py.time.Clock()

# Images
directory = os.path.dirname(os.path.abspath(__file__))
player_img = py.image.load(directory + r'\\Assets\\player.png')
player_grenade_img = py.image.load(directory + r'\\Assets\\player_grenade.png')
enemy_img = py.image.load(directory + r'\\Assets\\enemy_1.png')
shadow_img = py.image.load(directory + r'\\Assets\\shadow.png')
global player_shoot_img, grenade_image
player_shoot_img = py.image.load(directory + r'\\Assets\player_shoot.png')  # Load once globally
bullet_image = py.transform.scale(py.image.load(directory + r'\\Assets\\bullet.png'), (10, 5))
grenade_image = py.transform.scale(py.image.load(directory + r'\\Assets\\grenade.png'), (20, 20))
corpse_img = py.image.load(directory + r'\\Assets\\corpse.png')
corpse_flipped_img = py.image.load(directory + r'\\Assets\\corpse_flipped.png')

# Health Images
health_1_img = py.image.load(directory + r'\\Assets\\health_1.png')
health_2_img = py.image.load(directory + r'\\Assets\\health_2.png')
health_3_img = py.image.load(directory + r'\\Assets\\health_3.png')
global player_health_img, player_stamina_img
player_health_img = py.image.load(directory + r'\\Assets\\player_health.png')
player_stamina_img = py.image.load(directory + r'\\Assets\\player_stamina.png')
player_shield_img = py.image.load(directory + r'\\Assets\\player_shield.png')

# Graphics & GUI
cursor_image = py.image.load(directory + r'\\Assets\\target.png')
ground_img = py.image.load(directory + r'\\Assets\\ground.png')
HUD_img = py.image.load(directory + r'\\Assets\\HUD.png')
HUD_paused_img = py.image.load(directory + r'\\Assets\\game_paused.png')
HUD_M3_img = py.image.load(directory + r'\\Assets\\gun_1.png')
HUD_grenade_img = py.image.load(directory + r'\\Assets\\gun_2.png')
HUD_ammo_img = py.image.load(directory + r'\\Assets\\ammo.png')
HUD_grenade_ammo_img = py.image.load(directory + r'\\Assets\\grenade.png')
HUD_heal_img = py.image.load(directory + r'\\Assets\\heal.png')
HUD_shield_img = py.image.load(directory + r'\\Assets\\shield.png')
HUD_income_img = py.image.load(directory + r'\\Assets\\income.png')
HUD_grenade_button_img = py.image.load(directory + r'\\Assets\\grenade_button.png')

# Explosion
explosions = [py.image.load(directory + fr'\\Assets\\Explosions\\explosion_{i}.png') for i in range(1, 8)]

# Sounds
shot_sound = py.mixer.Sound(directory + r'\\Sounds\\shot.mp3')
reload_sound = py.mixer.Sound(directory + r'\\Sounds\\reload.mp3')
shot_bolt_sound = py.mixer.Sound(directory + r'\\Sounds\\shot_bolt.mp3')
step_sound_1 = py.mixer.Sound(directory + r'\\Sounds\\step_1.mp3')
step_sound_2 = py.mixer.Sound(directory + r'\\Sounds\\step_2.mp3')
step_channel = py.mixer.Channel(0)
reload_channel = py.mixer.Channel(1)

py.mouse.set_visible(False)
cursor_imgage_rect = cursor_image.get_rect()

class Game:
    def __init__(self):
        self.enemies = []
        self.corpses = []
        self.explosions = []
        self.button_time = 0

    def handle_shooting(self):
        current_time = py.time.get_ticks()

        if player.bullet_count <=0:
                player.can_shoot = False
                player.is_shooting = False

        if player.is_shooting and player.can_shoot:
                if current_time - player.last_shot_time > player.fire_rate:
                    shot_sound.play()
                    bullet = Bullet(player.rect, player.angle, "PLAYER_BULLET")
                    player_bullets.append(bullet)
                    player.bullet_count -= 1
                    player.last_shot_time = current_time
            
        if player.reloading:
            player.is_shooting = False
            player.can_shoot = False
            if current_time - reloading_time > player.reload_rate/1.5 and player.bullet_count < 30:
                player.bullet_count += 1
            if current_time - reloading_time > player.reload_rate:
                player.reloading = False
                player.can_shoot = True


    def handle_enemies_and_corpses(self):
            
            global enemies, corpses
            global wave_time, enemies_can_spawn, num_enemies, corpse_delay, wave_delay
            current_time = py.time.get_ticks()

            if len(self.enemies) == 0 and current_time - wave_time > wave_delay:
                if player.kills > 50:
                    assault_chance = random.randint(0, 100)
                    if assault_chance < 25:
                        num_enemies = 7
                    else:
                        num_enemies = random.randint(1, 4)
                else:
                    num_enemies = random.randint(1, 4)
                enemies_can_spawn = True

            if len(self.enemies) < num_enemies and enemies_can_spawn:
                spawn_x = random.choice([-35, 1580])
                spawn_y = random.choice([random.randint(150, 300), random.randint(450, 600)])
                spawn_ys = []
                while len(self.enemies) < num_enemies: 
                    enemy = Enemy(spawn_x, spawn_y)
                    self.enemies.append(enemy)
                    spawn_ys.append(spawn_y)
                    if spawn_y < 450:
                        spawn_y += 50
                        while (spawn_y in spawn_ys):
                            spawn_y += 50
                    else:
                        while (spawn_y in spawn_ys):
                            spawn_y -= 50
                enemies_can_spawn = False

            for corpse in self.corpses:
                corpse.draw_corpse()
                if current_time - corpse.time > corpse_delay:
                    self.corpses.remove(corpse)

            for enemy in self.enemies[:]:
                if enemy.check_state():
                    self.draw_shadow(enemy)
                    for bullet in enemy.bullets[:]:
                        if not bullet.move():
                            enemy.bullets.remove(bullet)
                        else:
                            bullet.draw_bullet()
                    enemy.shoot()
                    enemy.move()
                else:
                    if len(self.enemies) == 1:
                        wave_time = py.time.get_ticks()
                    self.enemies.remove(enemy)
                    player.money += player.money_reward
                    player.kills += 1
                    self.corpses.append(Corpse(enemy.angle, enemy.rect.x, enemy.rect.y, py.time.get_ticks()))
    def reset(self):
        global player, player_bullets
        player = Player()
        self.enemies = []
        self.corpses = []
        player_bullets = []

    def pause(self):
        global paused
        paused = True
        while paused:
            for event in py.event.get():
                if event.type == py.QUIT:
                    py.quit()
                    return
                if event.type == py.KEYDOWN and event.key == py.K_ESCAPE:
                    paused = False  # Resume game when ESC is pressed
                    escape_time = py.time.get_ticks()
                    return
            self.draw_screen()
            for corpse in self.corpses:
                corpse.draw_corpse()
            for enemy in self.enemies:
                self.draw_shadow(enemy)
                enemy.draw_enemy()
            player.draw_player()
            WIN.blit(HUD_paused_img, (700, 351))
            mouse_x, mouse_y = py.mouse.get_pos()
            WIN.blit(cursor_image, (mouse_x - 7.5, mouse_y - 7.5))

            mouse_pos = py.mouse.get_pos()
            mouse_pressed = py.mouse.get_pressed()
            resume_button_rect = py.Rect(725, 425, 150, 40)
            reset_button_rect = py.Rect(725, 468, 150, 40)
            quit_button_rect = py.Rect(725, 511, 150, 40)
            if resume_button_rect.collidepoint(mouse_pos):
                if mouse_pressed[0]:  # mouse_pressed[0] -> LMB
                    paused = False
                    return
            if reset_button_rect.collidepoint(mouse_pos):
                if mouse_pressed[0]:  # mouse_pressed[0] -> LMB
                    self.reset()
                    return
            if quit_button_rect.collidepoint(mouse_pos):
                if mouse_pressed[0]:  # mouse_pressed[0] -> LMB
                    py.quit()
                    return

            py.display.update()
            clock.tick(60)
            
    def handle_buttons(self):
        command = None
        current_time = py.time.get_ticks()

        mouse_pos = py.mouse.get_pos()
        mouse_pressed = py.mouse.get_pressed()
        health_button_rect = py.Rect(606, 805, 44, 44)
        shield_button_rect = py.Rect(606, 851, 44, 44)
        income_button_rect = py.Rect(653, 805, 44, 44)
        grenade_purchase_button_rect = py.Rect(653, 851, 44, 44)
        
        
        M3_button_rect = py.Rect(711, 0, 88, 88)
        grenade_button_rect = py.Rect(802, 0, 88, 88)
        
        global buttons
        buttons = [health_button_rect, shield_button_rect, income_button_rect, grenade_purchase_button_rect, M3_button_rect, grenade_button_rect]

        if health_button_rect.collidepoint(mouse_pos):
            if mouse_pressed[0] and current_time - self.button_time > button_delay:  # mouse_pressed[0] -> LMB
                command = "HEALTH"
                self.button_time = py.time.get_ticks()
        if shield_button_rect.collidepoint(mouse_pos):
            if mouse_pressed[0] and current_time - self.button_time > button_delay:
                command = "SHIELD"
                self.button_time = py.time.get_ticks()
        if income_button_rect.collidepoint(mouse_pos):
            if mouse_pressed[0] and current_time - self.button_time > button_delay: 
                command = "INCOME"
                self.button_time = py.time.get_ticks()
        if grenade_purchase_button_rect.collidepoint(mouse_pos):
            if mouse_pressed[0] and current_time - self.button_time > button_delay: 
                command = "GRENADE"
                self.button_time = py.time.get_ticks()

        if M3_button_rect.collidepoint(mouse_pos):
            if mouse_pressed[0] and current_time - self.button_time > button_delay: 
                player.current_weapon = "M3"
                player.original_image = player_img.copy()
                self.button_time = py.time.get_ticks()
                return
        if grenade_button_rect.collidepoint(mouse_pos):
            if mouse_pressed[0] and current_time - self.button_time > button_delay: 
                player.current_weapon = "GRENADE"
                player.original_image = player_grenade_img.copy()
                self.button_time = py.time.get_ticks()
                return

        global player_health_img, player_shield_img

        if command == "HEALTH" and player.money >= 100:
            player.health = player.max_health
            player.money -= 100
            scaled_image = py.transform.scale(player_health_img, (player.health , player_health_img.get_height()))
            player_health_img = scaled_image.copy()
        elif command == "SHIELD"and player.money >= 85:
            player.shield = player.max_shield
            player.money -= 85
            player_shield_img = py.image.load(directory + r'\\Assets\\player_shield.png')
        elif command == "INCOME"and player.money >= 100:
            player.money -= 100
            player.money_reward += 1
        elif command == "GRENADE" and player.money >= 50 and player.grenade_count < 3:
            player.money -= 50
            player.grenade_count += 1

    def draw_screen(self):
        mouse_x, mouse_y = py.mouse.get_pos()
        WIN.blit(ground_img, (0, 0))
        WIN.blit(HUD_img, (600, 800))
        WIN.blit(player_health_img, (900, 865))
        WIN.blit(player_stamina_img, (900, 848))
        WIN.blit(player_shield_img, (861, 804))

        if player.current_weapon == "M3":
            for i in range(0, player.bullet_count):
                WIN.blit(HUD_ammo_img, (901+i*3, 883))
        elif player.current_weapon == "GRENADE":
            for i in range(0, player.grenade_count):
                WIN.blit(HUD_grenade_ammo_img, (901+i*30, 883))

        self.draw_buttons()
        self.draw_text()
        if player.current_weapon == "GRENADE": # Dotted line For Grenade
            center_x, center_y = player.player_x, player.player_y
            dx, dy = mouse_x - center_x, mouse_y - center_y
            distance = math.hypot(dx, dy)

            if distance > 0:
                dx /= distance 
                dy /= distance

            for i in range(0, int(distance), 10):
                dot_x = int(center_x + i * dx)
                dot_y = int(center_y + i * dy)
                py.draw.circle(WIN, (255, 0, 0), (dot_x, dot_y), 3)

    def draw_shadow(self, object):
        if object.angle > 300:
            WIN.blit(shadow_img, (object.rect.centerx-20, object.rect.centery-5))
            return
        if object.angle > 135:
            WIN.blit(shadow_img, (object.rect.centerx, object.rect.centery-5))
            return
        if object.angle < -45 and object.angle > -135:
            WIN.blit(shadow_img, (object.rect.centerx-10, object.rect.centery-20))
            return
        if object.angle < -135:
            WIN.blit(shadow_img, (object.rect.centerx, object.rect.centery-15))
            return
        if object.angle < 135 and object.angle > 45:
            WIN.blit(shadow_img, (object.rect.centerx-10, object.rect.centery))
            return
        if object.angle < 45 and object.angle > -45:
            WIN.blit(shadow_img, (object.rect.centerx-20, object.rect.centery-10))
            return
               
    def draw_buttons(self):
        WIN.blit(HUD_M3_img, (711, 0))
        WIN.blit(HUD_grenade_img, (802, 0))

        WIN.blit(HUD_heal_img, (606, 805))
        WIN.blit(HUD_shield_img, (606, 851))
        WIN.blit(HUD_income_img, (653, 805))
        WIN.blit(HUD_grenade_button_img, (653, 851))

    def draw_text(self):
        money_text_surface = font.render(f"{player.money} $", True, (255, 255, 255))
        money_text_rect = money_text_surface.get_rect(center=(950, 814))
        WIN.blit(money_text_surface, money_text_rect)
        kills_text_surface = font.render(f"{player.kills}", True, (255, 255, 255))
        kills_text_rect = kills_text_surface.get_rect(center=(950, 834))
        WIN.blit(kills_text_surface, kills_text_rect)
    
    def handle_bullets(self):
        for bullet in player_bullets[:]:
            if not bullet.move():
                player_bullets.remove(bullet)
            else:
                if type(bullet) is Bullet:
                    bullet.draw_bullet()
                elif type(bullet) is Grenade:
                    bullet.draw_grenade()

    def check_inputs(self):
        global escape_time
        current_time = py.time.get_ticks()
        for event in py.event.get():
            if event.type == py.QUIT:
                py.quit()
                return
            if event.type == py.MOUSEBUTTONDOWN:
                
                mouse_x, mouse_y = py.mouse.get_pos()
                rect = py.Rect(mouse_x, mouse_y, 5, 5)
                for button in buttons:
                    if rect.colliderect(button):
                        return
                if player.current_weapon == "M3":
                    if event.button == 1 and player.can_shoot:
                        player.is_shooting = True
                elif player.current_weapon == "GRENADE" and player.grenade_count > 0:
                    if current_time - player.last_shot_time > player.fire_rate:
                        grenade = Grenade(player.rect, player.angle, "PLAYER_GRENADE")
                        player_bullets.append(grenade)
                        player.grenade_count -= 1
                        player.last_shot_time = current_time
            if event.type == py.MOUSEBUTTONUP:
                if event.button == 1:
                    player.is_shooting = False  
                
        key_pressed = py.key.get_pressed()
        if key_pressed[py.K_w]:
            player.move_player("W")
        if key_pressed[py.K_a]:
            player.move_player("A")
        if key_pressed[py.K_s]:
            player.move_player("S")
        if key_pressed[py.K_d]:
            player.move_player("D")
        if key_pressed[py.K_LSHIFT]:
            player.move_player("LS")
        if key_pressed[py.K_1]:
            player.current_weapon = "M3"
            player.image = player_img.copy()
            player.original_image = player_img.copy()
        if key_pressed[py.K_2]:
            player.current_weapon = "GRENADE"
            player.image = player_grenade_img.copy()
            player.original_image = player_grenade_img.copy()
        if key_pressed[py.K_ESCAPE] and current_time - escape_time > escape_delay:
            escape_time = py.time.get_ticks()
            game.pause()
        if key_pressed[py.K_r] and not player.reloading:
            global reloading_time
            reloading_time = py.time.get_ticks()
            player.reloading = True
            reload_channel.play(reload_sound)
game = Game()

# Button Checks
global button_pressed
button_pressed = False
button_delay = 100

def rotate(image, angle, pos):
    rotated_image = py.transform.rotate(image, angle)
    rotated_rect = rotated_image.get_rect(center=pos)
    return rotated_image, rotated_rect

class Player:
    def __init__(self):
        self.name = "PLAYER"
        self.original_image = player_img.copy()
        self.image = self.original_image
        self.is_shooting = False
        self.can_shoot = True
        self.reloading = False
        self.angle = 0
        self.player_x = width // 2
        self.player_y = height // 2
        self.rect = self.image.get_rect(topleft=(self.player_x, self.player_y))
        self.last_shot_time = 0
        self.bullet_count = 30
        self.grenade_count = 3
        self.health = 91
        self.shield = 71
        
        self.can_run = True
        self.current_weapon = "M3"

        self.money = 0
        self.kills = 0

        # Upgradeable
        self.money_reward = 13
        self.max_shield = self.shield
        self.max_health = self.health
        self.stamina = 91
        self.reload_rate = 4000
        self.player_speed = 1.75
        self.accuracy = 2
        self.buffer = 300
        self.fire_rate = 200

    def draw_player(self):
        mouse_x, mouse_y = py.mouse.get_pos()
        rel_x, rel_y = mouse_x - self.player_x, mouse_y - self.player_y
        self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)

        # Use the shooting image if the player is shooting
        if self.is_shooting:
            rotated_image = py.transform.rotate(player_shoot_img, self.angle)
        else:
            rotated_image = py.transform.rotate(self.original_image, self.angle)

        full_rect = rotated_image.get_rect(center=(self.player_x, self.player_y))
        WIN.blit(rotated_image, full_rect.topleft)

        self.image = rotated_image
        self.rect = full_rect

    def move_player(self, command):
        global player_stamina_img
        if command == "W":
            self.player_y -= self.player_speed
            if not step_channel.get_busy():
                step_channel.play(step_sound_1)
        if command == "S":
            self.player_y += self.player_speed
            if not step_channel.get_busy():
                step_channel.play(step_sound_2)
        if command == "A":
            self.player_x -= self.player_speed
            if not step_channel.get_busy():
                step_channel.play(step_sound_1)
        if command == "D":
            self.player_x += self.player_speed
            if not step_channel.get_busy():
                step_channel.play(step_sound_2)
        if command == "LS" and player.stamina > 1 and player.can_run:
                player.player_speed = 2.75
                player.stamina -= 1
                if player_stamina_img.get_width() > 1:
                    scaled_image = py.transform.scale(player_stamina_img, (player.stamina, player_stamina_img.get_height()))
                    player_stamina_img = scaled_image.copy()
                if player.stamina < 1:
                    player.can_run = False
        else:
                player.player_speed = 1.75
                if player.stamina <= 91:
                    player.stamina += 0.2
                    scaled_image = py.transform.scale(player_stamina_img, (player.stamina, player_stamina_img.get_height()))
                    player_stamina_img = scaled_image.copy()
                if player.stamina > 30:
                    player.can_run = True

        self.image, self.rect = rotate(self.original_image, self.angle, (self.player_x, self.player_y))
        self.rect.center = (self.player_x, self.player_y)
        self.draw_player()
        self.check_collision()
    
    def check_collision(self):
        if self.rect.colliderect(wall_1):
            self.player_y += self.player_speed + 1
        if self.rect.colliderect(wall_2):
            self.player_y -= self.player_speed + 1
        if self.rect.colliderect(wall_3):
            self.player_x += self.player_speed + 1
        if self.rect.colliderect(wall_4):
            self.player_x -= self.player_speed + 1

class Bullet:
    def __init__(self, rect, angle, name):
        self.name = name
        spawn_offset_x = 10
        spawn_offset_y = 0
        self.bullet_speed = 40
        spawn_x = rect.centerx + spawn_offset_x * math.cos(math.radians(angle))
        spawn_y = rect.centery + spawn_offset_y * math.sin(math.radians(angle))
        self.rect = py.Rect(spawn_x, spawn_y, 10, 5)
        self.dx = math.cos(math.radians(angle)) * self.bullet_speed
        self.dy = math.sin(math.radians(angle)) * self.bullet_speed
        self.player_angle = angle
        self.bullet_image = bullet_image.copy()
        self.deviation = random.randrange(2, 15, 1) / 10 * random.randint(-1, 1) / player.accuracy

    def move(self):
        self.rect.x += int(self.dx) + self.deviation
        self.rect.y -= int(self.dy) + self.deviation
        for enemy in game.enemies:
            if self.rect.colliderect(enemy.rect) and self.name == "PLAYER_BULLET":
                enemy.health -= 34
                return False
        if self.name == "ENEMY_BULLET":
            global player_health_img, player_shield_img
            if self.rect.colliderect(player.rect):
                if player.shield > 0:
                    player.shield -= 9
                    try:
                        scaled_image = py.transform.scale(player_shield_img, (player_shield_img.get_width(), player.shield))
                        player_shield_img = scaled_image.copy()
                    except:
                        scaled_image = py.transform.scale(player_shield_img, (player_shield_img.get_width(), 0))
                        player_shield_img = scaled_image.copy()
                    return False
                if player.health > 0 and player.shield <= 0:
                    player.health -= 9
                    if player.health <= 0:
                        game.reset()
                    scaled_image = py.transform.scale(player_health_img, (player.health , player_health_img.get_height()))
                    player_health_img = scaled_image.copy()
                    return False
            for wall in [wall_1, wall_2, wall_3, wall_4]:
                if self.rect.colliderect(wall):
                    odds = random.randint(0, 100)
                    if odds <= 33:
                        return False
        if self.rect.x > width or self.rect.x < 0 or self.rect.y > height or self.rect.y < 0:
            return False
        return True

    def draw_bullet(self):
        rotated_bullet = py.transform.rotate(self.bullet_image, self.player_angle)
        rotated_bullet_rect = rotated_bullet.get_rect(center=self.rect.center)
        WIN.blit(rotated_bullet, rotated_bullet_rect.topleft)

class Grenade:
    def __init__(self, rect, angle, name):
        self.name = name
        spawn_offset_x = 10
        spawn_offset_y = 0
        self.grenade_speed = 4
        spawn_x = rect.centerx + spawn_offset_x * math.cos(math.radians(angle))
        spawn_y = rect.centery + spawn_offset_y * math.sin(math.radians(angle))
        self.rect = py.Rect(spawn_x, spawn_y, 10, 5)
        grenade_image = py.image.load(directory + r'\\Assets\\grenade.png')
        grenade_image = py.transform.scale(grenade_image, (20, 20))
        self.dx = math.cos(math.radians(angle)) * self.grenade_speed
        self.dy = math.sin(math.radians(angle)) * self.grenade_speed
        self.angle = angle
        self.grenade_image = grenade_image.copy()
        self.dest_x, self.dest_y = py.mouse.get_pos()

    def move(self):
        self.rect.x += int(self.dx)
        self.rect.y -= int(self.dy)
        if not self.check_destination():
            game.explosions.append(Explosion(self.rect.x, self.rect.y))
            return False
        return True
    
    def draw_grenade(self):
        rotated_grenade = py.transform.rotate(self.grenade_image, self.angle)
        rotated_grenade_rect = rotated_grenade.get_rect(center=self.rect.center)
        WIN.blit(rotated_grenade, rotated_grenade_rect.topleft)

    def check_destination(self):
        if self.angle > 135 or self.angle < -135:
            if self.rect.x < self.dest_x:
                return False
        if self.angle < 135 and self.angle > 45:
            if self.rect.y < self.dest_y:
                return False 
        if self.angle < 45 and self.angle > -45:
            if self.rect.x > self.dest_x:
                return False
        if self.angle < -45 and self.angle > -135:
            if self.rect.y > self.dest_y:
                return False
        if self.rect.x > width or self.rect.x < 0 or self.rect.y > height or self.rect.y < 0:
                return False
        return True

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = py.Rect(x, y, 10, 10)
        self.time = py.time.get_ticks()
        self.delay = 100
        self.index = 1

    def explode(self):
        if self.index > 7:
            game.explosions[:1]
            return
        self.rect = explosions[self.index -1].get_rect()
        self.rect.centerx = self.x
        self.rect.centery = self.y
        WIN.blit(explosions[self.index - 1], (self.rect.topleft[0], self.rect.topleft[1]))
        if py.time.get_ticks() - self.delay * self.index > self.time:
            self.index+=1
        for enemy in game.enemies:
            if self.rect.colliderect(enemy.rect):
                enemy.health -= 10

class Enemy:
    def __init__(self, spawn_x, spawn_y):
        self.name = "ENEMY"
        self.rect = py.Rect(spawn_x, spawn_y, 50, 25)
        self.dx = player.player_x - self.rect.x
        self.dy = player.player_y - self.rect.y
        self.angle = math.degrees(math.atan2(-self.dy, self.dx)) % 360
        self.speed = 1
        self.bullets = []
        self.shoot_timer = random.randint(100, 200)
        self.health = 100

    def move(self):
        old_x, old_y = self.rect.x, self.rect.y

        if self.rect.x > player.player_x + player.buffer:
            self.rect.x -= self.speed
        if self.rect.x < player.player_x - player.buffer:
            self.rect.x += self.speed
        if self.rect.y > player.player_y + player.buffer:
            self.rect.y -= self.speed
        if self.rect.y < player.player_y - player.buffer:
            self.rect.y += self.speed

        for other in game.enemies:
            if other != self and self.rect.colliderect(other.rect):
                self.rect.x, self.rect.y = old_x, old_y
                
        self.draw_enemy()
    
    def check_state(self):
        if self.health <= 0:
            return False
        return True
    
    def shoot(self):
        if len(self.bullets) < 1 and self.shoot_timer == 0:
            bullet = Bullet(self.rect, self.angle, "ENEMY_BULLET")
            self.bullets.append(bullet)
            self.shoot_timer = 100
            shot_bolt_sound.play()
        else:
            self.shoot_timer -= 1

    def draw_enemy(self):
        self.dx = player.player_x - self.rect.x
        self.dy = player.player_y - self.rect.y
        self.angle = math.degrees(math.atan2(-self.dy, self.dx)) % 360
        rotated_enemy_img = py.transform.rotate(enemy_img, self.angle)
        self.rect = rotated_enemy_img.get_rect(center=self.rect.center)
        if self.health > 66:
            WIN.blit(health_3_img, (self.rect.topleft[0]+15, self.rect.topleft[1]-10))
        elif self.health > 33:
            WIN.blit(health_2_img, (self.rect.topleft[0]+15, self.rect.topleft[1]-10))
        else:
            WIN.blit(health_1_img, (self.rect.topleft[0]+15, self.rect.topleft[1]-10))
        WIN.blit(rotated_enemy_img, self.rect)

class Corpse:
    def __init__(self, angle, x, y, time):
        self.corpse_x = x
        self.corpse_y = y
        self.angle = angle
        if  self.corpse_x > width/2:
            self.image = corpse_img.copy()
        else:
            self.image = corpse_flipped_img.copy()
            self.corpse_x -= 35
        self.rect = py.Rect(self.corpse_x, self.corpse_y, 65,47)
        self.time = time

    def draw_corpse(self):
        WIN.blit(self.image, self.rect.topleft)

font = py.font.Font(None, 25)  
 
escape_time=0 
escape_delay=1000

def main():
    global player, player_bullets
    global wall_1, wall_2, wall_3, wall_4
    global enemies, corpses
    global button_time 
    global wave_time, enemies_can_spawn, num_enemies, corpse_delay, wave_delay
    button_time = 0
    wave_time = 0
    player = Player()
    playing = True
    enemies_can_spawn = True
    wall_1, wall_2, wall_3, wall_4 = (
        py.Rect(670, 330, 280, 5),
        py.Rect(670, 525, 280, 5),
        py.Rect(690, 335, 5, 210),
        py.Rect(930, 335, 5, 210))
    num_enemies = 1
    player_bullets = []
    corpse_delay = 20000
    wave_delay = 2500
    while playing:
        game.draw_screen()
        game.handle_shooting()
        game.handle_enemies_and_corpses()
        game.handle_bullets()
        game.handle_buttons()
        game.draw_shadow(player)
        player.draw_player()

        for explosion in game.explosions:
            explosion.explode()

        mouse_x, mouse_y = py.mouse.get_pos()
        WIN.blit(cursor_image, (mouse_x - 7.5, mouse_y - 7.5))
        game.check_inputs()
        py.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
    py.quit()