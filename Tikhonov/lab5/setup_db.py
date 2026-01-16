from sqlalchemy import create_engine, text

# Подключение к вашей базе данных
engine = create_engine("postgresql://admin:admin@localhost:5432/arzamas_radar")

def update_database():
    try:
        with engine.connect() as conn:
            print("Соединение с БД установлено...")
            # Добавляем колонки для текста и типа (новость/реклама)
            conn.execute(text("ALTER TABLE news_posts ADD COLUMN IF NOT EXISTS post_text TEXT;"))
            conn.execute(text("ALTER TABLE news_posts ADD COLUMN IF NOT EXISTS post_type VARCHAR(50);"))
            # Очищаем таблицу для чистого сбора 10к данных
            conn.execute(text("TRUNCATE TABLE news_posts;"))
            conn.commit()
            print("✅ БАЗА ГОТОВА: Таблица обновлена и очищена.")
    except Exception as e:
        print(f"❌ ОШИБКА БД: {e}")

if __name__ == "__main__":
    update_database()