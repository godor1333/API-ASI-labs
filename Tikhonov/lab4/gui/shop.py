import pygame
from .theme import PANEL_BG, TEXT_COLOR, get_font
from .ui import Button
from db.database import SessionLocal


class Shop:
    def __init__(self, player, game):
        self.player = player
        self.game = game
        self.visible = False
        self.tab = "character"
        self.buttons = []
        self.back_btn = Button(260, 350, 80, 40, "Назад", font_size=18)
        self.confirm_buy = False
        self.item_to_buy = None
        self.message = ""
        self.message_timer = 0
        self.init_buttons()

    def init_buttons(self):
        self.tabs = {
            "character": Button(20, 60, 100, 40, "Перс", font_size=16),
            "weapon": Button(130, 60, 100, 40, "Оружие", font_size=16),
            "buy": Button(240, 60, 100, 40, "Покупки", font_size=16),
        }
        self.update_buttons()

    def update_buttons(self):
        self.buttons = []
        y = 120
        if self.tab == "character":
            char = self.player.characters[0]
            font = pygame.font.SysFont("Courier New", 18)
            name_surf = font.render(f"Имя: {char.name}", True, TEXT_COLOR)
            hp_surf = font.render(f"HP: {char.base_hp}", True, (255, 100, 100))
            atk_surf = font.render(f"Сила: {5 + char.weapon_level * 10}", True, (100, 255, 100))
            self.buttons.append({"type": "text", "surface": name_surf, "pos": (20, y)})
            y += 30
            self.buttons.append({"type": "text", "surface": hp_surf, "pos": (20, y)})
            y += 30
            self.buttons.append({"type": "text", "surface": atk_surf, "pos": (20, y)})
        elif self.tab == "weapon":
            char = self.player.characters[0]
            weapons = {"sword": "Меч", "bow": "Лук", "staff": "Посох", "none": "Нет"}
            current = weapons.get(char.weapon_type, "Неизвестно")
            surf = pygame.font.SysFont("Courier New", 18).render(f"Оружие: {current}, уровень: {char.weapon_level}", True, TEXT_COLOR)
            self.buttons.append({"type": "text", "surface": surf, "pos": (20, y)})
        elif self.tab == "buy":
            weapons = [
                {"name": "Лук", "cost": 30, "atk": 3, "type": "bow"},
                {"name": "Меч", "cost": 40, "atk": 4, "type": "sword"},
                {"name": "Посох", "cost": 50, "atk": 5, "type": "staff"},
            ]
            for w in weapons:
                btn = Button(20, y, 100, 40, "Купить", font_size=16)
                self.buttons.append({"type": "button", "obj": btn, "weapon": w})
                y += 50

    def draw(self, screen):
        if not self.visible:
            return

        # Окно подтверждения покупки
        if self.confirm_buy:
            overlay = pygame.Surface((900, 650), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            pygame.draw.rect(screen, (50, 50, 80), (300, 250, 300, 150), border_radius=12)
            title = get_font(24).render("Купить?", True, TEXT_COLOR)
            screen.blit(title, (450 - title.get_width() // 2, 270))
            yes_btn = Button(330, 320, 100, 40, "Да", font_size=20)
            no_btn = Button(470, 320, 100, 40, "Нет", font_size=20)
            yes_btn.draw(screen)
            no_btn.draw(screen)
            pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if yes_btn.is_clicked(pos, event):
                        self.confirm_buy = False
                        self.execute_purchase()
                    if no_btn.is_clicked(pos, event):
                        self.confirm_buy = False
            return

        # Основное окно магазина
        pygame.draw.rect(screen, PANEL_BG, (0, 0, 360, 400), border_radius=12)
        title_font = pygame.font.SysFont("Courier New", 24, bold=True)
        title = title_font.render("Магазин", True, TEXT_COLOR)
        screen.blit(title, (20, 20))

        for btn in self.tabs.values():
            btn.draw(screen)

        for item in self.buttons:
            if item["type"] == "button":
                item["obj"].draw(screen)
                font = pygame.font.SysFont("Courier New", 16)
                w = item["weapon"]
                text = font.render(f"{w['name']} ({w['cost']} монет, +{w['atk']} силы)", True, TEXT_COLOR)
                screen.blit(text, (130, item["obj"].rect.y))
            elif item["type"] == "text":
                screen.blit(item["surface"], item["pos"])

        self.back_btn.draw(screen)

        # Баланс
        coin_font = pygame.font.SysFont("Courier New", 18)
        coin_text = coin_font.render(f"Монеты: {self.player.coins}", True, (255, 255, 0))
        screen.blit(coin_text, (20, 360))

        # Сообщение
        if self.message:
            msg_font = get_font(18)
            msg_surf = msg_font.render(self.message, True, (255, 100, 100))
            screen.blit(msg_surf, (20, 320))

    def execute_purchase(self):
        w = self.item_to_buy
        char = self.player.characters[0]
        if char.weapon_type == w["type"]:
            # Улучшение
            if self.player.coins >= w["cost"]:
                char.weapon_level = min(5, char.weapon_level + 1)
                self.player.coins -= w["cost"]
                self.message = f"Улучшено оружие: {w['name']}"
                self.message_timer = pygame.time.get_ticks() + 2000
                # Обновляем силу в GUI
                if self.game.char1 and self.game.char1.name == char.name:
                    self.game.char1.weapon_level = char.weapon_level
                    self.game.char1.atk = 5 + char.weapon_level * 10
                db = SessionLocal()
                db.commit()
                db.close()
                self.update_buttons()
            else:
                self.message = "Недостаточно монет!"
                self.message_timer = pygame.time.get_ticks() + 2000
        else:
            # Покупка нового оружия
            if self.player.coins >= w["cost"]:
                char.weapon_type = w["type"]
                char.weapon_level = 1
                self.player.coins -= w["cost"]
                self.message = f"Куплено оружие: {w['name']}"
                self.message_timer = pygame.time.get_ticks() + 2000
                # Обновляем оружие в GUI
                if self.game.char1 and self.game.char1.name == char.name:
                    self.game.char1.weapon_type = char.weapon_type
                    self.game.char1.weapon_level = char.weapon_level
                    self.game.char1.atk = 5 + char.weapon_level * 10
                db = SessionLocal()
                db.commit()
                db.close()
                self.update_buttons()
            else:
                self.message = "Недостаточно монет!"
                self.message_timer = pygame.time.get_ticks() + 2000

    def handle_event(self, event, pos):
        if not self.visible:
            return
        if self.confirm_buy:
            return
        for name, btn in self.tabs.items():
            btn.check_hover(pos)
            if btn.is_clicked(pos, event):
                self.tab = name
                self.update_buttons()
        for item in self.buttons:
            if item["type"] == "button":
                item["obj"].check_hover(pos)
                if item["obj"].is_clicked(pos, event):
                    if self.tab == "buy":
                        self.item_to_buy = item["weapon"]
                        self.confirm_buy = True
        if self.back_btn.is_clicked(pos, event):
            self.visible = False
        # Таймер сообщения
        if self.message and pygame.time.get_ticks() >= self.message_timer:
            self.message = ""