import pygame
import sys
import random
import os

# --- Инициализация ---
pygame.init()
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Doodle Jump с направленной стрельбой")
clock = pygame.time.Clock()
FPS = 60

# --- Пути к картинкам ---
IMG_DIR = os.path.join(os.path.dirname(__file__), "images")
PLAYER_IMG_RIGHT = pygame.transform.scale(pygame.image.load(os.path.join(IMG_DIR, "doodler_right.png")).convert_alpha(), (80, 60))
PLAYER_IMG_LEFT = pygame.transform.scale(pygame.image.load(os.path.join(IMG_DIR, "doodler_left.png")).convert_alpha(), (80, 60))
PLAYER_IMG_UP = pygame.transform.scale(pygame.image.load(os.path.join(IMG_DIR, "doodlerup.png")).convert_alpha(), (80, 60))
PLAYER_IMG_UP_LEFT = pygame.transform.scale(pygame.image.load(os.path.join(IMG_DIR, "doodlerup_left.png")).convert_alpha(), (80, 60))
PLAYER_IMG_UP_RIGHT = pygame.transform.scale(pygame.image.load(os.path.join(IMG_DIR, "doodlerup_right.png")).convert_alpha(), (80, 60))
PLATFORM_IMG = pygame.transform.scale(pygame.image.load(os.path.join(IMG_DIR, "platform.png")).convert_alpha(), (100, 20))
BULLET_IMG = pygame.transform.scale(pygame.image.load(os.path.join(IMG_DIR, "bullet.png")).convert_alpha(), (20, 20))

# --- Настройки ---
GRAVITY = 0.4
JUMP_POWER = -10
PLATFORM_COUNT = 7
BULLET_SPEED = 8
SHOT_COOLDOWN = 500
PLAYER_SPEED = 6  # плавная скорость

# --- Классы ---
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = PLATFORM_IMG
        self.rect = self.image.get_rect(topleft=(x, y))

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = PLAYER_IMG_RIGHT  # Изначально смотрит вправо
        self.rect = self.image.get_rect(center=(x, y))
        self.vy = 0
        self.last_direction = "right"  # left, right, up, up_left, up_right

    def update(self, platforms, keys):
        dx = 0

        # --- Движение ---
        if keys[pygame.K_a]:
            dx = -PLAYER_SPEED
            self.last_direction = "left"
        elif keys[pygame.K_d]:
            dx = PLAYER_SPEED
            self.last_direction = "right"

        # Телепорт через края
        if self.rect.right + dx < 0:
            self.rect.left = WIDTH
        if self.rect.left + dx > WIDTH:
            self.rect.right = 0
        self.rect.x += dx

        # --- Гравитация ---
        self.vy += GRAVITY
        self.rect.y += self.vy

        # Прыжок от платформ
        if self.vy > 0:
            hits = pygame.sprite.spritecollide(self, platforms, False)
            for p in hits:
                if self.rect.bottom <= p.rect.bottom + 10:
                    self.rect.bottom = p.rect.top
                    self.vy = JUMP_POWER

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy):
        super().__init__()
        self.image = BULLET_IMG
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.bottom < 0 or self.rect.left > WIDTH or self.rect.right < 0:
            self.kill()

# --- Создание платформ ---
def create_platforms():
    group = pygame.sprite.Group()
    base = Platform(WIDTH//2-50, HEIGHT-40)
    group.add(base)
    last_y = HEIGHT-40
    for i in range(PLATFORM_COUNT-1):
        x = random.randint(0, WIDTH-100)
        max_jump_height = (JUMP_POWER**2)/(2*GRAVITY)
        y = last_y - random.randint(int(max_jump_height*0.6), int(max_jump_height*0.9))
        if y < 0: y = random.randint(0,50)
        last_y = y
        group.add(Platform(x,y))
    return group

# --- Главная функция ---
def main():
    platforms = create_platforms()
    player = Player(WIDTH // 2, HEIGHT - 100)
    bullets = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    all_sprites.add(platforms)

    last_shot_time = 0
    score = 0
    running = True

    while running:
        clock.tick(FPS)
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- Определяем направление стрельбы ---
        shoot_dx, shoot_dy = 0, 0
        shoot_image = None
        if keys[pygame.K_SPACE]:
            if keys[pygame.K_w] and keys[pygame.K_a]:
                shoot_dx = -BULLET_SPEED
                shoot_dy = -BULLET_SPEED
                shoot_image = PLAYER_IMG_UP_LEFT
                player.last_direction = "up_left"
            elif keys[pygame.K_w] and keys[pygame.K_d]:
                shoot_dx = BULLET_SPEED
                shoot_dy = -BULLET_SPEED
                shoot_image = PLAYER_IMG_UP_RIGHT
                player.last_direction = "up_right"
            elif keys[pygame.K_w]:
                shoot_dy = -BULLET_SPEED
                shoot_image = PLAYER_IMG_UP
                player.last_direction = "up"
            elif keys[pygame.K_a]:
                shoot_dx = -BULLET_SPEED
                shoot_image = PLAYER_IMG_LEFT
                player.last_direction = "left"
            elif keys[pygame.K_d]:
                shoot_dx = BULLET_SPEED
                shoot_image = PLAYER_IMG_RIGHT
                player.last_direction = "right"

            if (shoot_dx != 0 or shoot_dy != 0) and current_time - last_shot_time > SHOT_COOLDOWN:
                bullet = Bullet(player.rect.centerx, player.rect.top, shoot_dx, shoot_dy)
                bullets.add(bullet)
                all_sprites.add(bullet)
                last_shot_time = current_time

        # --- Смена картинки игрока ---
        center = player.rect.center
        if keys[pygame.K_SPACE] and shoot_image:
            player.image = shoot_image
        else:
            # Оставляем последнюю позицию
            if player.last_direction == "left":
                player.image = PLAYER_IMG_LEFT
            elif player.last_direction == "right":
                player.image = PLAYER_IMG_RIGHT
            elif player.last_direction == "up":
                player.image = PLAYER_IMG_UP
            elif player.last_direction == "up_left":
                player.image = PLAYER_IMG_UP_LEFT
            elif player.last_direction == "up_right":
                player.image = PLAYER_IMG_UP_RIGHT
        player.rect = player.image.get_rect(center=center)

        # --- Обновления ---
        player.update(platforms, keys)
        bullets.update()

        # --- Скролл ---
        dy_scroll = 0
        if player.rect.top < HEIGHT // 3:
            dy_scroll = (HEIGHT // 3) - player.rect.top
            player.rect.top = HEIGHT // 3
            score += dy_scroll
            for p in platforms:
                p.rect.y += dy_scroll

        # --- Генерация новых платформ ---
        while len(platforms) < PLATFORM_COUNT:
            x = random.randint(0, WIDTH-100)
            max_jump_height = (JUMP_POWER**2)/(2*GRAVITY)
            last_y = min([p.rect.y for p in platforms])
            y = last_y - random.randint(int(max_jump_height*0.6), int(max_jump_height*0.9))
            if y < -PLATFORM_IMG.get_height():
                y = -PLATFORM_IMG.get_height()
            p = Platform(x, y)
            platforms.add(p)
            all_sprites.add(p)

        # --- Удаление платформ ---
        for p in list(platforms):
            if p.rect.top > HEIGHT:
                p.kill()

        # --- Рисование ---
        screen.fill((200, 220, 255))
        platforms.draw(screen)
        bullets.draw(screen)
        screen.blit(player.image, player.rect)

        font = pygame.font.SysFont(None, 28)
        text = font.render("Счёт: " + str(int(score)), True, (0, 0, 0))
        screen.blit(text, (10, 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
