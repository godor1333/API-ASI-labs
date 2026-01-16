from sqlalchemy import Column, Integer, Text, Float, JSON, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Данные берутся из docker-compose.yml
DATABASE_URL = "postgresql://admin:admin@localhost:5432/arzamas_radar"

Base = declarative_base()


class NewsPost(Base):
    __tablename__ = 'news_posts'

    id = Column(Integer, primary_key=True)
    text = Column(Text)
    locations = Column(JSON)  # Список найденных улиц
    temperature = Column(Float)  # Коэффициент интенсивности
    embedding = Column(JSON)  # Вектор для кластеризации
    is_anomaly = Column(Integer, default=0)
    timestamp = Column(Integer)


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        print("🗄 База данных успешно инициализирована.")
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")