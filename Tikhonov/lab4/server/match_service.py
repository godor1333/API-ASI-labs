from sqlalchemy.orm import Session
from db.database import SessionLocal
from core.models import Player, Character, Item, Match
from core.board import generate_valid_board, apply_move_and_cascade  # ← обе функции
from core.bot_ai import bot_find_best_move
from core.elo import update_elo
from core.equipment import generate_random_item
from kafka_utils.producer import send_match_result
from datetime import datetime, timedelta
from copy import deepcopy

def create_test_player(username: str, char_name: str, db: Session):
    # Проверим, не существует ли уже игрок с таким именем
    existing = db.query(Player).filter(Player.username == username).first()
    if existing:
        return existing

    player = Player(username=username)
    db.add(player)
    db.flush()

    char = Character(name=char_name, player_id=player.id)
    db.add(char)
    # Не делаем commit здесь — пусть вызывающий код делает
    return player

def start_match(player1_id: int, player2_id: int, db: Session) -> Match:
    board = generate_valid_board()
    char1 = db.query(Character).filter(Character.player_id == player1_id).first()
    hp1 = char1.base_hp + sum(i.hp_bonus for i in char1.items)
    if player2_id > 0:
        char2 = db.query(Character).filter(Character.player_id == player2_id).first()
        hp2 = char2.base_hp + sum(i.hp_bonus for i in char2.items)
    else:
        hp2 = 100
    match = Match(
        player1_id=player1_id,
        player2_id=player2_id,
        player1_hp_start=hp1,
        player2_hp_start=hp2,
        player1_hp_end=hp1,
        player2_hp_end=hp2,
        board_state=board,
        initial_board_state=deepcopy(board),
        finished=False
    )
    db.add(match)
    db.commit()
    return match

def apply_player_move(match_id: int, move: tuple, db: Session) -> dict:
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match or match.finished:
        return {"error": "Match not active"}
    removed = apply_move_and_cascade(match.board_state, *move)
    if removed is None:
        return {"error": "Invalid move"}
    match.player1_total_score += removed
    db.commit()
    return {"removed": removed, "total": match.player1_total_score}

def end_match(match_id: int, db: Session):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match or match.finished:
        return
    if datetime.utcnow() - match.start_time > timedelta(seconds=45):
        match.is_timeout = True
    match.finished = True
    match.end_time = datetime.utcnow()
    # Счёт игрока
    player_score = match.player1_total_score
    # Счёт бота
    if match.player2_id < 0:
        _, bot_score = bot_find_best_move(match.initial_board_state)
    else:
        bot_score = 0  # PvP — не используется здесь
    # Урон
    dmg_to_p2 = min(match.player2_hp_start, player_score * 3)
    dmg_to_p1 = min(match.player1_hp_start, bot_score * 3)
    match.player1_hp_end = max(0, match.player1_hp_start - dmg_to_p1)
    match.player2_hp_end = max(0, match.player2_hp_start - dmg_to_p2)
    # Определение победителя
    if match.player2_hp_end == 0:
        winner_id = match.player1_id
        outcome = 1.0
    elif match.player1_hp_end == 0:
        winner_id = match.player2_id
        outcome = 0.0
    else:
        if match.player1_hp_end > match.player2_hp_end:
            winner_id = match.player1_id
            outcome = 1.0
        elif match.player2_hp_end > match.player1_hp_end:
            winner_id = match.player2_id
            outcome = 0.0
        else:
            winner_id = None
            outcome = 0.5
    match.winner_id = winner_id
    # Обновление статистики
    p1 = db.query(Player).filter(Player.id == match.player1_id).first()
    if winner_id == match.player1_id:
        p1.wins += 1
    elif winner_id is not None:
        p1.losses += 1
    if match.player2_id > 0:
        p2 = db.query(Player).filter(Player.id == match.player2_id).first()
        if winner_id == match.player2_id:
            p2.wins += 1
        else:
            p2.losses += 1
        new_r1, new_r2 = update_elo(p1.elo_rating, p2.elo_rating, outcome)
        p1.elo_rating = new_r1
        p2.elo_rating = new_r2
    else:
        bot_rating = 1200.0
        new_r1, _ = update_elo(p1.elo_rating, bot_rating, outcome)
        p1.elo_rating = new_r1
    # Награда победителю
    if winner_id == match.player1_id:
        item = generate_random_item()
        char1 = db.query(Character).filter(Character.player_id == match.player1_id).first()
        item.character_id = char1.id
        db.add(item)
    db.commit()
    send_match_result({
        "match_id": match.id,
        "winner_id": winner_id,
        "player1_score": player_score,
        "bot_score": bot_score if match.player2_id < 0 else None,
        "timeout": match.is_timeout
    })