import pygame
from .theme import BACKGROUND, TEXT_COLOR, get_title_font, get_font
from .ui import Button
from .admin_panel import AdminPanel

class MainMenu:
    def __init__(self, game):
        self.game = game
        self.visible = True
        self.buttons = []
        self.selected_players = 1
        self.admin_panel = AdminPanel(game)
        self.init_buttons()

    def init_buttons(self):
        center_x = 450
        y = 200
        btn_width, btn_height = 250, 60  # Достаточно широкая кнопка
        gap = 20

        self.buttons.append(Button(center_x - btn_width//2, y, btn_width, btn_height, "1 Игрок", font_size=28))
        y += btn_height + gap
        self.buttons.append(Button(center_x - btn_width//2, y, btn_width, btn_height, "2 Игрока", font_size=28))
        y += btn_height + gap
        # Уменьшен шрифт, чтобы текст "Панель администратора" поместился
        self.buttons.append(Button(center_x - btn_width//2, y, btn_width, btn_height, "Панель администратора", font_size=20))
        y += btn_height + gap
        self.buttons.append(Button(center_x - btn_width//2, y, btn_width, btn_height, "Выход", font_size=28))

    def draw(self, screen):
        if not self.visible:
            return
        screen.fill(BACKGROUND)
        title = get_title_font(48).render("Match3 MMORPG", True, TEXT_COLOR)
        screen.blit(title, (450 - title.get_width()//2, 100))

        for btn in self.buttons:
            btn.draw(screen)

        if self.admin_panel.visible:
            self.admin_panel.draw(screen)

    def handle_event(self, event, pos):
        if not self.visible:
            return
        if self.admin_panel.visible:
            self.admin_panel.handle_event(event, pos)
            return

        for btn in self.buttons:
            btn.check_hover(pos)
            if btn.is_clicked(pos, event):
                if "1 Игрок" in btn.text:
                    self.selected_players = 1
                    self.start_game()
                elif "2 Игрока" in btn.text:
                    self.selected_players = 2
                    self.start_game()
                elif "Панель администратора" in btn.text:
                    self.admin_panel.visible = True
                elif "Выход" in btn.text:
                    self.game.running = False

    def start_game(self):
        self.visible = False
        self.game.start_match(self.selected_players)