import pygame
from .theme import BUTTON_NORMAL, BUTTON_HOVER, get_font

class Button:
    def __init__(self, x, y, width, height, text, color=None, hover_color=None, font_size=24):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color or BUTTON_NORMAL
        self.hover_color = hover_color or BUTTON_HOVER
        self.font = get_font(font_size)
        self.is_hovered = False
        self.is_pressed = False

    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        if self.is_pressed:
            color = (min(color[0]+30, 255), min(color[1]+30, 255), min(color[2]+30, 255))
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=8)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                self.is_pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_pressed = False
        return False