# db/init_db.py
from core.models import Base
from db.database import engine

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ База данных match3.db создана.")

if __name__ == "__main__":
    init_db()