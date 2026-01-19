from sqlalchemy import create_engine, text

engine = create_engine("postgresql://admin:admin@localhost:5432/arzamas_radar")

with engine.connect() as conn:
    # Добавляем колонку, если её нет
    conn.execute(text("ALTER TABLE news_posts ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
    conn.commit()
    print("✅ Колонка created_at успешно добавлена!")