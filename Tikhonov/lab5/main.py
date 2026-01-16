import time
import random
from sqlalchemy import create_engine, Column, Integer, Text, Float, JSON
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql://admin:admin@localhost:5432/arzamas_radar"
Base = declarative_base()


class NewsPost(Base):
    __tablename__ = 'news_posts'
    id = Column(Integer, primary_key=True)
    text = Column(Text)
    locations = Column(JSON)
    temperature = Column(Float)


engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

STREETS = ["Калинина", "Ленина", "Маркса", "ТЦ Омега", "Соборная площадь", "Парк Гайдара"]


def simulate():
    templates = [
        "Пробка на {} от самого центра.",
        "Открытие нового {} состоялось!",
        "Ремонт дороги на {}: будьте внимательны.",
        "Авария в районе {}, движение перекрыто."
    ]
    print("📡 Георадар запущен: имитация инфопотока Арзамаса...")
    while True:
        try:
            loc = random.choice(STREETS)
            current_time = time.strftime('%H:%M:%S')
            text = f"{random.choice(templates).format(loc)} (Обновлено: {current_time})"

            # Эмуляция работы AI-моделей (температура инфопотока)
            temp = random.uniform(0.4, 0.95)

            post = NewsPost(text=text, locations=[loc], temperature=temp)
            session.add(post)
            session.commit()
            print(f"📩 Сигнал из локации: {loc} | Давление: {temp:.2f}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            session.rollback()
        time.sleep(random.randint(3, 7))


if __name__ == "__main__":
    simulate()