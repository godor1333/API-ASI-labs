import random
from typing import List, Tuple, Set, Optional
from copy import deepcopy

TILE_TYPES = 6
ROWS, COLS = 8, 8

def generate_valid_board() -> List[List[int]]:
    while True:
        board = [[random.randint(1, TILE_TYPES) for _ in range(COLS)] for _ in range(ROWS)]
        if not find_matches(board) and has_valid_move(board):
            return board

def find_matches(board: List[List[int]]) -> List[Set[Tuple[int, int]]]:
    matches = []
    for r in range(ROWS):
        c = 0
        while c < COLS - 2:
            if board[r][c] != 0 and board[r][c] == board[r][c+1] == board[r][c+2]:
                match = {(r, c), (r, c+1), (r, c+2)}
                c += 3
                while c < COLS and board[r][c] == board[r][c-1]:
                    match.add((r, c))
                    c += 1
                matches.append(match)
            else:
                c += 1
    for c in range(COLS):
        r = 0
        while r < ROWS - 2:
            if board[r][c] != 0 and board[r][c] == board[r+1][c] == board[r+2][c]:
                match = {(r, c), (r+1, c), (r+2, c)}
                r += 3
                while r < ROWS and board[r][c] == board[r-1][c]:
                    match.add((r, c))
                    r += 1
                matches.append(match)
            else:
                r += 1
    return matches

def is_adjacent(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
    (r1, c1), (r2, c2) = pos1, pos2
    return abs(r1 - r2) + abs(c1 - c2) == 1

def swap_tiles(board: List[List[int]], r1: int, c1: int, r2: int, c2: int):
    board[r1][c1], board[r2][c2] = board[r2][c2], board[r1][c1]

def remove_matches_and_cascade(board: List[List[int]]) -> int:
    total_removed = 0
    while True:
        matches = find_matches(board)
        if not matches:
            break
        for match in matches:
            for (r, c) in match:
                board[r][c] = 0
                total_removed += 1
        for c in range(COLS):
            write_pos = ROWS - 1
            for r in range(ROWS - 1, -1, -1):
                if board[r][c] != 0:
                    board[write_pos][c] = board[r][c]
                    if write_pos != r:
                        board[r][c] = 0
                    write_pos -= 1
        for r in range(ROWS):
            for c in range(COLS):
                if board[r][c] == 0:
                    board[r][c] = random.randint(1, TILE_TYPES)
    return total_removed

def is_valid_move(board: List[List[int]], r1: int, c1: int, r2: int, c2: int) -> bool:
    if not (0 <= r1 < ROWS and 0 <= c1 < COLS and 0 <= r2 < ROWS and 0 <= c2 < COLS):
        return False
    if not is_adjacent((r1, c1), (r2, c2)):
        return False
    swap_tiles(board, r1, c1, r2, c2)
    valid = len(find_matches(board)) > 0
    swap_tiles(board, r1, c1, r2, c2)
    return valid

def has_valid_move(board: List[List[int]]) -> bool:
    for r in range(ROWS):
        for c in range(COLS):
            for dr, dc in [(0,1), (1,0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS:
                    if is_valid_move(board, r, c, nr, nc):
                        return True
    return False

def apply_move_and_cascade(board: List[List[int]], r1: int, c1: int, r2: int, c2: int) -> Optional[int]:
    if not is_valid_move(board, r1, c1, r2, c2):
        return None
    swap_tiles(board, r1, c1, r2, c2)
    return remove_matches_and_cascade(board)