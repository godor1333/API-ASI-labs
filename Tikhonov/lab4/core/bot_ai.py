from typing import List, Tuple, Optional
from copy import deepcopy
from core.board import is_valid_move, apply_move_and_cascade, ROWS, COLS

def bot_find_best_move(board: List[List[int]]) -> Tuple[Optional[Tuple[int, int, int, int]], int]:
    best_move = None
    max_removed = 0
    for r in range(ROWS):
        for c in range(COLS):
            for dr, dc in [(0, 1), (1, 0)]:
                nr, nc = r + dr, c + dc
                if nr >= ROWS or nc >= COLS:
                    continue
                if is_valid_move(board, r, c, nr, nc):
                    test_board = deepcopy(board)
                    removed = apply_move_and_cascade(test_board, r, c, nr, nc)
                    if removed is not None and removed > max_removed:
                        max_removed = removed
                        best_move = (r, c, nr, nc)
    return best_move, max_removed