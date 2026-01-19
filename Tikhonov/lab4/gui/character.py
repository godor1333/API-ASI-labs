import pygame

class PixelCharacter:
    def __init__(self, name, x, y, hp=50, weapon_level=0, weapon_type="none"):
        self.name = name
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = min(150, hp)  # Максимум 150
        self.weapon_level = weapon_level
        self.weapon_type = weapon_type
        self.atk = 5 + weapon_level * 10  # Базовая сила
        self.image = self.create_pixel_art()
        self.rect = self.image.get_rect(topleft=(x, y))

    def create_pixel_art(self):
        surf = pygame.Surface((60, 80))
        surf.fill((100, 150, 200))
        pygame.draw.circle(surf, (255, 255, 200), (30, 20), 10)
        pygame.draw.rect(surf, (150, 100, 50), (20, 30, 20, 40))
        if self.weapon_type == "sword":
            pygame.draw.line(surf, (200, 200, 200), (40, 50), (50, 40), 3)
        elif self.weapon_type == "bow":
            pygame.draw.arc(surf, (200, 200, 200), (25, 55, 10, 10), 0, 3.14, 2)
        elif self.weapon_type == "staff":
            pygame.draw.line(surf, (100, 100, 255), (30, 30), (30, 60), 3)
        return surf

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        # Шкала HP
        bar_width = 100
        bar_height = 10
        fill = int((self.hp / self.max_hp) * bar_width)
        pygame.draw.rect(screen, (100, 100, 100), (self.x - 20, self.y + 90, bar_width, bar_height))
        pygame.draw.rect(screen, (255, 0, 0), (self.x - 20, self.y + 90, fill, bar_height))
        # Шкала атаки
        atk_fill = int((self.atk / 55) * bar_width)  # Максимум 55 при уровне 5
        pygame.draw.rect(screen, (100, 100, 100), (self.x - 20, self.y + 105, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (self.x - 20, self.y + 105, atk_fill, bar_height))
        # Текст HP и атаки
        font = pygame.font.SysFont("Courier New", 16)
        hp_text = font.render(f"HP: {self.hp}", True, (255, 255, 255))
        atk_text = font.render(f"Сила: {self.atk}", True, (255, 255, 255))
        screen.blit(hp_text, (self.x - 20, self.y + 120))
        screen.blit(atk_text, (self.x - 20, self.y + 140))
        # Имя
        name_surf = font.render(self.name, True, (255, 255, 255))
        screen.blit(name_surf, (self.x - 20, self.y + 160))

    def take_damage(self, damage):
        self.hp = max(0, self.hp - damage)
        return self.hp <= 0