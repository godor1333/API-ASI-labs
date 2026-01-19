from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
from config import DB_PATH

Base = declarative_base()

class VideoAnalysis(Base):
    __tablename__ = "video_analyses"
    
    id = Column(Integer, primary_key=True)
    video_url = Column(String, unique=True)
    video_id = Column(String)
    author = Column(String)
    title = Column(String)
    brainrot_index = Column(Float)
    metrics = Column(JSON)  # JSON с детальными метриками
    transcript = Column(Text)
    memes_detected = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "video_url": self.video_url,
            "video_id": self.video_id,
            "author": self.author,
            "title": self.title,
            "brainrot_index": self.brainrot_index,
            "metrics": json.loads(self.metrics) if isinstance(self.metrics, str) else self.metrics,
            "transcript": self.transcript,
            "memes_detected": json.loads(self.memes_detected) if isinstance(self.memes_detected, str) else self.memes_detected,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

# Создаем engine и сессию
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

