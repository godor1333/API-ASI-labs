import requests
import time
import json
import re
from sqlalchemy import create_engine, text

# --- НАСТРОЙКИ ---
# Твой новый токен (уже вставлен)
TOKEN = 'vk1.a.0Jt3n6AwGKES2sfJD2P76XbMkoAk4cMaqfNXnZL0kGRDGSdwvOuF--2rqhoY_xHjwRSBfCzPN8tlvihcNnVkA8XhDb_9cjw_Rd94YycTxdQ6b0bnChaqmNck95YkJ_pM1opuaj3D43sLLy1ijH1pEHcGwn8zTkdllgB0botCOQvffTud2JcJr0l7m-fdkev_EjpwWXujXd89vzL1YbH8xg'
VERSION = '5.131'

# Твои ID групп (скрипт автоматически делает их отрицательными для обращения к стенам)
RAW_IDS = [
    60246922, 27838907, 108494404, 125528525, 63677604,
    66394898, 161456272, 193336088, 73133102, 5421782,
    199588232, 167467761, 212986781, 166718171, 190831704
]
GROUP_IDS = [-abs(gid) for gid in RAW_IDS]

# Актуальная карта локаций Арзамаса
LOCATION_MAP = {
    r"калин": "Калинина",
    r"ленин": "Ленина",
    r"маркс": "Маркса",
    r"омег": "ТЦ Омега",
    r"плаз": "ТЦ Плаза",
    r"куб": "ТЦ Куб",
    r"(авеню|avenu)": "ТЦ Авеню",
    r"гайдар": "Парк Гайдара",
    r"соборн": "Соборная",
    r"вокзал": "Вокзал",
    r"пландин": "Пландина",
    r"9 мая": "9 Мая",
    r"парковая": "Парковая",
    r"пушкин": "Пушкина",
    r"мира": "Мира",
    r"советск": "Советская",
    r"севастополь": "Севастопольская",
    r"кирилл": "Кирилловка",
    r"выездн": "Выездное",
    r"горько": "Горького",
    r"проспект": "Проспект"
}

engine = create_engine("postgresql://admin:admin@localhost:5432/arzamas_radar")


def get_posts(group_id, offset):
    url = 'https://api.vk.com/method/wall.get'
    params = {
        'access_token': TOKEN,
        'v': VERSION,
        'owner_id': group_id,
        'count': 50,
        'offset': offset
    }
    try:
        resp = requests.get(url, params=params).json()
        if 'error' in resp:
            return f"❌ ОШИБКА ВК: {resp['error']['error_msg']}"
        return resp.get('response', {}).get('items', [])
    except Exception as e:
        return f"❌ СБОЙ СЕТИ: {str(e)}"


def save_post(post, gid):
    text_content = post.get('text', '')
    if not text_content: return False

    # Поиск совпадений по ключам улиц и ТЦ
    found_locs = []
    for pattern, official in LOCATION_MAP.items():
        if re.search(pattern, text_content, re.IGNORECASE):
            found_locs.append(official)

    if not found_locs:
        return False

        # Убираем дубликаты названий (например, если "Ленина" встретилось дважды)
    found_locs = list(set(found_locs))

    try:
        with engine.connect() as conn:
            # Проверка на дубликат самого поста в базе
            dup = conn.execute(text("SELECT 1 FROM news_posts WHERE post_text = :t LIMIT 1"),
                               {"t": text_content}).fetchone()
            if dup: return False

            # Детектор рекламы
            is_ads = post.get('marked_as_ads') or any(
                x in text_content.lower() for x in ["цена", "скидка", "реклама", "запись", "товар"])

            conn.execute(
                text("INSERT INTO news_posts (post_text, locations, post_type) VALUES (:t, :l, :tp)"),
                {"t": text_content, "l": json.dumps(found_locs), "tp": "Реклама" if is_ads else "Событие"}
            )
            conn.commit()

            # Печатаем успех в консоль
            preview = text_content[:60].replace('\n', ' ')
            print(f"✅ [ID:{gid}] Найдено: {found_locs} | Текст: {preview}...")
            return True
    except:
        return False


def run_harvester(target=10000):
    with engine.connect() as conn:
        db_total = conn.execute(text("SELECT count(*) FROM news_posts")).scalar()

    print(f"🚀 СТАРТ ПАРСИНГА АРЗАМАСА. В базе: {db_total}. Цель: {target}")

    offset = 0
    added_session = 0

    while (db_total + added_session) < target and offset < 100000:
        print(f"\n--- Проверка истории на глубине {offset} постов ---")
        any_posts_at_level = False

        for gid in GROUP_IDS:
            posts = get_posts(gid, offset)

            # Если вернулась строка (ошибка), печатаем её
            if isinstance(posts, str):
                print(f"   {posts} (Группа {gid})")
                continue

            if not posts:
                continue

            any_posts_at_level = True
            for p in posts:
                if save_post(p, gid):
                    added_session += 1

            # Пауза для обхода анти-спам фильтра ВК
            time.sleep(0.35)

        if not any_posts_at_level and offset > 5000:
            print("🏁 Посты во всех группах закончились.")
            break

        offset += 50
        print(f"📊 Добавлено за сессию: {added_session} | Всего в БД: {db_total + added_session}")


if __name__ == "__main__":
    run_harvester()