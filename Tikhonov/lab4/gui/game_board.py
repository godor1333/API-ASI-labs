# gui/game_board.py
import pygame
from core.board import apply_move_and_cascade, is_valid_move
from .theme import TILE_COLORS

TILE_SIZE = 50
ROWS, COLS = 8, 8
BOARD_OFFSET_X = (900 - COLS * TILE_SIZE) // 2
BOARD_OFFSET_Y = (650 - ROWS * TILE_SIZE) // 2

class GameBoard:
    def __init__(self, board_state):
        self.board = [row[:] for row in board_state]
        self.selected = None
        self.message = "Сделайте ход"

    def draw(self, screen):
        for r in range(ROWS):
            for c in range(COLS):
                tile = self.board[r][c]
                color = (40, 40, 60) if tile == 0 else TILE_COLORS[tile - 1]
                rect = pygame.Rect(
                    BOARD_OFFSET_X + c * TILE_SIZE,
                    BOARD_OFFSET_Y + r * TILE_SIZE,
                    TILE_SIZE, TILE_SIZE
                )
                pygame.draw.rect(screen, color, rect, border_radius=6)
                pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=6)
        if self.selected:
            r, c = self.selected
            rect = pygame.Rect(
                BOARD_OFFSET_X + c * TILE_SIZE,
                BOARD_OFFSET_Y + r * TILE_SIZE,
                TILE_SIZE, TILE_SIZE
            )
            pygame.draw.rect(screen, (255, 255, 100), rect, 4, border_radius=6)

    def handle_click(self, pos):
        x, y = pos
        c = (x - BOARD_OFFSET_X) // TILE_SIZE
        r = (y - BOARD_OFFSET_Y) // TILE_SIZE
        if not (0 <= r < ROWS and 0 <= c < COLS):
            return None
        if self.selected is None:
            self.selected = (r, c)
            return None
        else:
            r1, c1 = self.selected
            if (r, c) == (r1, c1):
                self.selected = None
                return None
            if is_valid_move(self.board, r1, c1, r, c):
                removed = apply_move_and_cascade(self.board, r1, c1, r, c)
                self.selected = None
                return removed
            else:
                self.selected = None
                return None

    def apply_bot_move(self, r1, c1, r2, c2):
        """Применяет ход бота."""
        removed = apply_move_and_cascade(self.board, r1, c1, r2, c2)
        return removed