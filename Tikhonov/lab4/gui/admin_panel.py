import pygame
from .theme import PANEL_BG, TEXT_COLOR, get_font
from .ui import Button
from db.database import SessionLocal
from core.models import Player, Character


class AdminPanel:
    def __init__(self, game):
        self.game = game
        self.visible = False
        self.password_input = ""
        self.login_error = ""
        self.login_mode = True
        self.selected_char_id = 1
        self.buttons = []
        self.login_btn = Button(350, 300, 200, 50, "Войти", font_size=24)
        self.back_btn = Button(350, 370, 200, 50, "Отмена", font_size=24)
        self.init_char_buttons()

    def init_char_buttons(self):
        x, y = 20, 80
        btn_width, btn_height = 220, 40
        gap = 10
        self.buttons = [
            Button(x, y, btn_width, btn_height, "Дать меч", font_size=18),
            Button(x, y + (btn_height + gap) * 1, btn_width, btn_height, "Дать лук", font_size=18),
            Button(x, y + (btn_height + gap) * 2, btn_width, btn_height, "Дать посох", font_size=18),
            Button(x, y + (btn_height + gap) * 3, btn_width, btn_height, "Добавить 10 HP", font_size=18),
            Button(x, y + (btn_height + gap) * 4, btn_width, btn_height, "Убавить 10 HP", font_size=18),
            Button(x, y + (btn_height + gap) * 5, btn_width, btn_height, "Сбросить оружие", font_size=18),
            Button(x, y + (btn_height + gap) * 6, btn_width, btn_height, "Выйти", font_size=18),
        ]

    def draw(self, screen):
        if not self.visible:
            return

        if self.login_mode:
            overlay = pygame.Surface((900, 650), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            pygame.draw.rect(screen, (40, 40, 70), (300, 200, 300, 250), border_radius=12)
            title = get_font(28).render("Админ-панель", True, TEXT_COLOR)
            screen.blit(title, (450 - title.get_width() // 2, 220))
            pwd_text = get_font(20).render(f"Пароль: {self.password_input}{'_' if pygame.time.get_ticks() % 1000 < 500 else ''}", True, TEXT_COLOR)
            screen.blit(pwd_text, (320, 270))
            if self.login_error:
                err = get_font(18).render(self.login_error, True, (255, 100, 100))
                screen.blit(err, (450 - err.get_width() // 2, 310))
            self.login_btn.draw(screen)
            self.back_btn.draw(screen)
        else:
            pygame.draw.rect(screen, PANEL_BG, (0, 0, 260, 400), border_radius=12)
            title = get_font(26).render("Админ-панель", True, TEXT_COLOR)
            screen.blit(title, (20, 20))
            for btn in self.buttons:
                btn.draw(screen)

    def handle_event(self, event, pos):
        if not self.visible:
            return

        if self.login_mode:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.password_input = self.password_input[:-1]
                elif event.key == pygame.K_RETURN:
                    self.try_login()
                elif event.unicode.isdigit() and len(self.password_input) < 6:
                    self.password_input += event.unicode

            if self.login_btn.is_clicked(pos, event):
                self.try_login()
            if self.back_btn.is_clicked(pos, event):
                self.visible = False
                self.password_input = ""
                self.login_error = ""
        else:
            for i, btn in enumerate(self.buttons):
                btn.check_hover(pos)
                if btn.is_clicked(pos, event):
                    self.execute_action(i)

    def try_login(self):
        # Убираем лишние символы
        pwd = self.password_input.strip()
        if pwd == "111":
            self.login_mode = False
            self.login_error = ""
        else:
            self.login_error = "Неверный пароль!"

    def execute_action(self, action_id):
        db = SessionLocal()
        char = db.query(Character).filter(Character.id == self.selected_char_id).first()
        if not char:
            self.game.message = "Персонаж не найден"
            db.close()
            return

        try:
            if action_id == 0:  # Меч
                char.weapon_type = "sword"
                char.weapon_level = 1
                self.game.message = "Выдан меч"
            elif action_id == 1:  # Лук
                char.weapon_type = "bow"
                char.weapon_level = 1
                self.game.message = "Выдан лук"
            elif action_id == 2:  # Посох
                char.weapon_type = "staff"
                char.weapon_level = 1
                self.game.message = "Выдан посох"
            elif action_id == 3:  # +10 HP
                char.base_hp = min(150, char.base_hp + 10)
                self.game.message = f"HP увеличено (теперь {char.base_hp})"
            elif action_id == 4:  # -10 HP
                char.base_hp = max(0, char.base_hp - 10)
                self.game.message = f"HP уменьшено (теперь {char.base_hp})"
            elif action_id == 5:  # Сбросить оружие
                char.weapon_type = "none"
                char.weapon_level = 0
                self.game.message = "Оружие сброшено"
            elif action_id == 6:  # Выйти
                self.visible = False
                self.login_mode = True
                self.password_input = ""
                return
        except Exception as e:
            self.game.message = f"Ошибка: {str(e)}"
        finally:
            db.commit()
            db.close()