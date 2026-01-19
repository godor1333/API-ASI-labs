# core/models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator, TEXT
import json
from datetime import datetime

class JsonType(TypeDecorator):
    impl = TEXT
    def process_bind_param(self, value, dialect):
        return json.dumps(value) if value else None
    def process_result_value(self, value, dialect):
        return json.loads(value) if value else None

Base = declarative_base()

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    elo_rating = Column(Float, default=1200.0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    coins = Column(Integer, default=0)
    characters = relationship("Character", back_populates="owner", cascade="all, delete-orphan")

class Character(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    player_id = Column(Integer, ForeignKey("players.id"))
    base_hp = Column(Integer, default=50)
    weapon_level = Column(Integer, default=0)  # 0 = нет оружия, 1-5 = уровень
    weapon_type = Column(String, default="none")  # "sword", "bow", "staff"
    owner = relationship("Player", back_populates="characters")
    items = relationship("Item", back_populates="character", cascade="all, delete-orphan")

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    quality = Column(Integer)
    hp_bonus = Column(Integer)
    character_id = Column(Integer, ForeignKey("characters.id"))
    character = relationship("Character", back_populates="items")

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True, index=True)
    player1_id = Column(Integer, ForeignKey("players.id"))
    player2_id = Column(Integer)  # <0 = бот, >0 = игрок
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    player1_hp_start = Column(Integer)
    player2_hp_start = Column(Integer)
    player1_hp_end = Column(Integer)
    player2_hp_end = Column(Integer)
    player1_total_score = Column(Integer, default=0)
    player2_total_score = Column(Integer, default=0)
    winner_id = Column(Integer, nullable=True)
    is_timeout = Column(Boolean, default=False)
    finished = Column(Boolean, default=False)
    board_state = Column(JsonType)
    initial_board_state = Column(JsonType)