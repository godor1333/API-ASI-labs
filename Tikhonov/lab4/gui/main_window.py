import pygame
import time
from core.board import generate_valid_board
from core.bot_ai import bot_find_best_move
from db.database import SessionLocal
from core.models import Player, Character
from gui.game_board import GameBoard
from gui.menu import MainMenu
from gui.character import PixelCharacter
from gui.shop import Shop
from gui.admin_panel import AdminPanel
from gui.theme import BACKGROUND, PANEL_BG, TEXT_COLOR, get_font
from gui.ui import Button


class MainWindow:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((900, 650))
        pygame.display.set_caption("Match3 MMORPG")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_board = None
        self.main_menu = None
        self.shop = None
        self.admin_panel = None
        self.match_active = False
        self.start_time = 0
        self.player1 = None
        self.player2 = None
        self.char1 = None
        self.char2 = None
        self.message = "Добро пожаловать!"
        self.player1_id = 1
        self.current_turn = "player"
        self.bot_move_delay = 1.5
        self.bot_move_timer = 0
        self.attack_animation = None
        self.match_result_shown = False
        self.time_warning_shown = False
        self.confirm_exit = False
        self.confirm_exit_timer = 0
        self.game_over = False
        self.game_over_timer = 0
        self.confirm_menu = False  # Новое поле

        self.init_main_menu()
        self.init_ui_buttons()

    def init_main_menu(self):
        self.main_menu = MainMenu(self)

    def init_ui_buttons(self):
        self.btn_shop = Button(720, 600, 150, 50, "Магазин", font_size=22)
        self.btn_menu = Button(560, 600, 150, 50, "Меню", font_size=22)

    def start_match(self, players_count):
        db = SessionLocal()
        self.player1 = db.query(Player).filter(Player.id == self.player1_id).first()
        if not self.player1:
            self.player1 = Player(username="Alice", coins=0)
            db.add(self.player1)
            db.flush()
            orm_char = Character(name="Воин", player_id=self.player1.id, base_hp=50)
            db.add(orm_char)
            db.commit()
        else:
            orm_char = self.player1.characters[0]

        self.char1 = PixelCharacter(
            name=orm_char.name,
            x=100, y=200,
            hp=orm_char.base_hp,
            weapon_level=orm_char.weapon_level,
            weapon_type=orm_char.weapon_type
        )

        if players_count == 1:
            self.char2 = PixelCharacter("Бот", 700, 200, hp=50, weapon_level=0, weapon_type="none")
            self.player2 = None
        else:
            self.player2 = db.query(Player).filter(Player.id == 2).first()
            if not self.player2:
                self.player2 = Player(username="Bob", coins=0)
                db.add(self.player2)
                db.flush()
                orm_char2 = Character(name="Лучник", player_id=self.player2.id, base_hp=50)
                db.add(orm_char2)
                db.commit()
            else:
                orm_char2 = self.player2.characters[0]
            self.char2 = PixelCharacter(
                name=orm_char2.name,
                x=700, y=200,
                hp=orm_char2.base_hp,
                weapon_level=orm_char2.weapon_level,
                weapon_type=orm_char2.weapon_type
            )

        db.close()

        self.match_active = True
        self.start_time = time.time()
        self.current_turn = "player"
        self.game_board = GameBoard(generate_valid_board())
        self.message = "Матч начат! Вы ходите первым."
        self.match_result_shown = False
        self.time_warning_shown = False
        self.confirm_exit = False
        self.confirm_menu = False
        self.game_over = False

    def calculate_damage(self, weapon_type, weapon_level):
        if weapon_type == "bow":
            return min(15, 5 + weapon_level * 3)
        elif weapon_type == "sword":
            return min(20, 5 + weapon_level * 4)
        elif weapon_type == "staff":
            return min(25, 5 + weapon_level * 5)
        else:
            return 5

    def apply_damage(self, removed, target_char):
        coins = 0
        if removed == 3:
            coins = 1
        elif removed == 4:
            coins = 5
        elif removed >= 5:
            coins = 10

        attacker = self.char1 if target_char == self.char2 else self.char2
        damage = self.calculate_damage(attacker.weapon_type, attacker.weapon_level)

        target_char.take_damage(damage)
        self.player1.coins += coins
        self.message = f"Урон: {damage} | Монеты: {self.player1.coins}"
        self.attack_animation = {"target": target_char, "start_time": time.time()}

    def end_match(self):
        if not self.match_active:
            return
        if self.match_result_shown:
            return

        elapsed = time.time() - self.start_time
        if elapsed > 45:
            self.message = "⏰ Таймаут!"
        else:
            if self.char1.hp <= 0:
                self.message = "Вы проиграли!"
            elif self.char2.hp <= 0:
                self.message = "Вы победили! Получена шмотка!"
            else:
                if self.char1.hp > self.char2.hp:
                    self.message = "Победа по HP!"
                elif self.char1.hp < self.char2.hp:
                    self.message = "Поражение по HP"
                else:
                    self.message = "Ничья!"

        self.match_active = False
        self.match_result_shown = True

    def draw_status_bar(self):
        elapsed = int(time.time() - self.start_time) if self.match_active else 0
        remaining = max(0, 45 - elapsed)

        if self.match_active and remaining <= 5 and not self.time_warning_shown:
            self.message = "⚠️ Осталось мало времени!"
            self.time_warning_shown = True

        pygame.draw.rect(self.screen, PANEL_BG, (0, 0, 900, 50))

        status_text = f"Ваш HP: {self.char1.hp} | Бот HP: {self.char2.hp} | Таймер: {remaining}s | Ход: {self.current_turn}"
        status_font = get_font(18)
        status_surf = status_font.render(status_text, True, TEXT_COLOR)
        self.screen.blit(status_surf, (10, 10))

        msg_font = get_font(20)
        msg_surf = msg_font.render(self.message, True, (255, 255, 100))
        self.screen.blit(msg_surf, (10, 60))

    def run(self):
        while self.running:
            pos = pygame.mouse.get_pos()
            current_time = time.time()
            for event in pygame.event.get():
                # 🔑 КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: сначала проверяем админ-панель для ЛЮБОГО события
                if self.admin_panel and self.admin_panel.visible:
                    self.admin_panel.handle_event(event, pos)
                    continue  # ← НЕ ОБРАБАТЫВАЕМ НИЧЕГО ДРУГОГО, ЕСЛИ ПАНЕЛЬ ОТКРЫТА

                # Только если панель закрыта — обрабатываем остальное
                if event.type == pygame.QUIT:
                    if self.match_active:
                        self.confirm_exit = True
                    else:
                        self.running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        if self.shop:
                            self.shop.visible = not self.shop.visible
                    elif event.key == pygame.K_m:
                        if self.match_active:
                            self.confirm_menu = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Обработка кликов в окне подтверждения
                    if self.confirm_menu:
                        yes_btn = Button(330, 320, 100, 40, "Да", font_size=20)
                        no_btn = Button(470, 320, 100, 40, "Нет", font_size=20)
                        if yes_btn.is_clicked(pos, event):
                            self.confirm_menu = False
                            self.end_match()
                            self.main_menu.visible = True
                            self.match_active = False
                        if no_btn.is_clicked(pos, event):
                            self.confirm_menu = False
                    elif self.confirm_exit:
                        yes_btn = Button(330, 320, 100, 40, "Да", font_size=20)
                        no_btn = Button(470, 320, 100, 40, "Нет", font_size=20)
                        if yes_btn.is_clicked(pos, event):
                            self.confirm_exit = False
                            self.running = False
                        if no_btn.is_clicked(pos, event):
                            self.confirm_exit = False
                    elif self.game_over:
                        ok_btn = Button(400, 350, 100, 50, "ОК", font_size=24)
                        if ok_btn.is_clicked(pos, event):
                            self.game_over = False
                            self.main_menu.visible = True
                            self.match_active = False
                    elif self.match_active and self.game_board and self.current_turn == "player":
                        removed = self.game_board.handle_click(pos)
                        if removed is not None:
                            self.apply_damage(removed, self.char2)
                            self.current_turn = "bot"
                            self.bot_move_timer = current_time + self.bot_move_delay
                    if self.shop:
                        self.shop.handle_event(event, pos)
                    if self.main_menu:
                        self.main_menu.handle_event(event, pos)
                    if self.btn_shop.is_clicked(pos, event):
                        if not self.shop:
                            self.shop = Shop(self.player1, self)
                        self.shop.visible = not self.shop.visible
                    if self.btn_menu.is_clicked(pos, event):
                        if self.match_active:
                            self.confirm_menu = True  # Показать окно подтверждения
                        else:
                            self.main_menu.visible = True

            if self.match_active and (self.char1.hp <= 0 or self.char2.hp <= 0):
                self.game_over = True
                self.match_active = False

            if self.match_active and self.current_turn == "bot" and current_time >= self.bot_move_timer:
                if self.player2 is None:
                    best_move, removed = bot_find_best_move(self.game_board.board)
                    if best_move:
                        r1, c1, r2, c2 = best_move
                        self.game_board.apply_bot_move(r1, c1, r2, c2)
                        self.apply_damage(removed, self.char1)
                self.current_turn = "player"
                self.bot_move_timer = current_time + self.bot_move_delay

            self.screen.fill(BACKGROUND)

            if self.main_menu and self.main_menu.visible:
                self.main_menu.draw(self.screen)
            elif self.match_active:
                if self.char1:
                    self.char1.draw(self.screen)
                if self.char2:
                    self.char2.draw(self.screen)

                if self.game_board:
                    self.game_board.draw(self.screen)

                if self.attack_animation:
                    target = self.attack_animation["target"]
                    elapsed = current_time - self.attack_animation["start_time"]
                    if elapsed < 1.5:
                        start_pos = (target.x + 30, target.y + 30)
                        end_pos = (target.x + 30, target.y + 30)
                        progress = min(elapsed / 1.5, 1)
                        current_x = start_pos[0] + (end_pos[0] - start_pos[0]) * progress
                        current_y = start_pos[1] + (end_pos[1] - start_pos[1]) * progress
                        pygame.draw.circle(self.screen, (255, 255, 0), (int(current_x), int(current_y)), 8)
                    else:
                        self.attack_animation = None

                self.draw_status_bar()
                self.btn_shop.draw(self.screen)
                self.btn_menu.draw(self.screen)
                if self.shop:
                    self.shop.draw(self.screen)

            # Окно подтверждения меню
            if self.confirm_menu:
                overlay = pygame.Surface((900, 650), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, (0, 0))
                pygame.draw.rect(self.screen, (50, 50, 80), (300, 250, 300, 150), border_radius=12)
                title = get_font(24).render("Выйти в меню?", True, TEXT_COLOR)
                self.screen.blit(title, (450 - title.get_width() // 2, 270))
                yes_btn = Button(330, 320, 100, 40, "Да", font_size=20)
                no_btn = Button(470, 320, 100, 40, "Нет", font_size=20)
                yes_btn.draw(self.screen)
                no_btn.draw(self.screen)

            # Окно подтверждения выхода из приложения
            if self.confirm_exit:
                overlay = pygame.Surface((900, 650), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, (0, 0))
                pygame.draw.rect(self.screen, (50, 50, 80), (300, 250, 300, 150), border_radius=12)
                title = get_font(24).render("Выйти из игры?", True, TEXT_COLOR)
                self.screen.blit(title, (450 - title.get_width() // 2, 270))
                yes_btn = Button(330, 320, 100, 40, "Да", font_size=20)
                no_btn = Button(470, 320, 100, 40, "Нет", font_size=20)
                yes_btn.draw(self.screen)
                no_btn.draw(self.screen)

            # Окно Game Over
            if self.game_over:
                overlay = pygame.Surface((900, 650), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, (0, 0))
                pygame.draw.rect(self.screen, (50, 50, 80), (300, 250, 300, 150), border_radius=12)
                title = get_font(32).render("Game Over!", True, (255, 100, 100))
                self.screen.blit(title, (450 - title.get_width() // 2, 270))
                ok_btn = Button(400, 350, 100, 50, "ОК", font_size=24)
                ok_btn.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()