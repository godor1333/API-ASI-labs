from db.database import SessionLocal
from core.models import Player, Character, Item, Match
from utils.board_renderer import render_board_cli
from core.equipment import generate_random_item
from server.match_service import end_match

def admin_list_players():
    db = SessionLocal()
    players = db.query(Player).all()
    for p in players:
        char = db.query(Character).filter(Character.player_id == p.id).first()
        hp = char.base_hp + sum(i.hp_bonus for i in char.items) if char else 0
        print(f"ID: {p.id} | {p.username} | Elo: {p.elo_rating:.0f} | W/L: {p.wins}/{p.losses} | HP: {hp}")
        if char:
            for i, item in enumerate(char.items):
                print(f"  🧬 [{i}] {item.name} (+{item.hp_bonus} HP)")
    db.close()

def admin_give_item(player_id: int):
    db = SessionLocal()
    char = db.query(Character).filter(Character.player_id == player_id).first()
    if not char:
        print("❌ Персонаж не найден")
        db.close()
        return
    item = generate_random_item()
    item.character_id = char.id
    db.add(item)
    db.commit()
    print(f"✅ Выдано: {item.name}")
    db.close()

def admin_remove_item(player_id: int, item_index: int):
    db = SessionLocal()
    char = db.query(Character).filter(Character.player_id == player_id).first()
    if not char or item_index < 0 or item_index >= len(char.items):
        print("❌ Неверный индекс")
        db.close()
        return
    item = char.items[item_index]
    db.delete(item)
    db.commit()
    print(f"🗑️ Удалено: {item.name}")
    db.close()

def admin_list_matches():
    db = SessionLocal()
    matches = db.query(Match).all()
    for m in matches:
        status = "✅ Завершён" if m.finished else "⏳ Активен"
        print(f"Матч #{m.id}: {m.player1_id} vs {m.player2_id} — {status}")
    db.close()

def admin_show_board(match_id: int):
    db = SessionLocal()
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        print("❌ Матч не найден")
        db.close()
        return
    print(f"\n🎮 Текущая доска матча #{match.id}:")
    print(render_board_cli(match.board_state))
    print(f"\n🆕 Стартовая доска:")
    print(render_board_cli(match.initial_board_state))
    db.close()

def admin_end_match(match_id: int):
    db = SessionLocal()
    end_match(match_id, db)
    db.close()
    print(f"✅ Матч #{match_id} завершён принудительно.")