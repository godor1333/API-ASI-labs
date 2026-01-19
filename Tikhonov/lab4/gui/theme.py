import pygame

BACKGROUND = (20, 20, 40)
PANEL_BG = (30, 30, 60)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT = (255, 255, 100)
BUTTON_NORMAL = (50, 50, 80)
BUTTON_HOVER = (70, 70, 100)
HP_PLAYER = (0, 255, 100)
HP_BOT = (255, 100, 100)
TILE_COLORS = [
    (255, 50, 50),
    (50, 50, 255),
    (50, 255, 50),
    (255, 255, 50),
    (150, 50, 150),
    (255, 150, 50),
]

_pixel_font = None
_courier_font_cache = {}

def get_pixel_font(size=24):
    global _pixel_font
    if _pixel_font is None:
        try:
            _pixel_font = pygame.font.Font("assets/pixel.ttf", size)
        except:
            _pixel_font = pygame.font.SysFont("Courier New", size, bold=True)
    if _pixel_font.get_height() != size:
        try:
            return pygame.font.Font("assets/pixel.ttf", size)
        except:
            return pygame.font.SysFont("Courier New", size, bold=True)
    return _pixel_font

def get_font(size=24):
    if size not in _courier_font_cache:
        _courier_font_cache[size] = pygame.font.SysFont("Courier New", size, bold=True)
    return _courier_font_cache[size]

def get_title_font(size=32):
    return pygame.font.SysFont("Courier New", size, bold=True)