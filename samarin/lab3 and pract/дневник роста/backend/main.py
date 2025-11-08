from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import List, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from pathlib import Path

# Настройки
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# База данных
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/plant_diary")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except Exception:
    # Fallback to pbkdf2_sha256 if bcrypt fails
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Модели базы данных
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Plant(Base):
    __tablename__ = "plants"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    species = Column(String)
    description = Column(Text)
    planted_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", backref="plants")
    entries = relationship("PlantEntry", back_populates="plant", cascade="all, delete-orphan")
    photos = relationship("PlantPhoto", back_populates="plant", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="plant", cascade="all, delete-orphan")

class PlantEntry(Base):
    __tablename__ = "plant_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id"))
    entry_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    watering = Column(Boolean, default=False)
    fertilizing = Column(Boolean, default=False)
    pruning = Column(Boolean, default=False)
    other_care = Column(String)
    
    plant = relationship("Plant", back_populates="entries")

class PlantPhoto(Base):
    __tablename__ = "plant_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id"))
    photo_path = Column(String)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    plant = relationship("Plant", back_populates="photos")

class Reminder(Base):
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id"))
    reminder_type = Column(String)  # watering, fertilizing, pruning, etc.
    times_per_day = Column(Integer, default=1)  # Количество раз в день
    reminder_time = Column(String)  # Время в формате HH:MM
    days_of_week = Column(String)  # Дни недели через запятую (0-6, где 0=понедельник)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    plant = relationship("Plant", back_populates="reminders")

# Создание таблиц
# Удаляем старые таблицы и создаем заново (для разработки)
# В production использовать миграции Alembic
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Pydantic модели
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    
    class Config:
        from_attributes = True

class PlantCreate(BaseModel):
    name: str
    species: Optional[str] = None
    description: Optional[str] = None

class PlantResponse(BaseModel):
    id: int
    name: str
    species: Optional[str]
    description: Optional[str]
    planted_date: datetime
    
    class Config:
        from_attributes = True

class PlantEntryCreate(BaseModel):
    notes: Optional[str] = None
    watering: bool = False
    fertilizing: bool = False
    pruning: bool = False
    other_care: Optional[str] = None

class PlantEntryResponse(BaseModel):
    id: int
    entry_date: datetime
    notes: Optional[str]
    watering: bool
    fertilizing: bool
    pruning: bool
    other_care: Optional[str]
    
    class Config:
        from_attributes = True

class ReminderCreate(BaseModel):
    reminder_type: str
    times_per_day: int = 1
    reminder_time: str  # HH:MM
    days_of_week: str  # "0,1,2,3,4,5,6" или "0,2,4" и т.д.

class ReminderResponse(BaseModel):
    id: int
    reminder_type: str
    times_per_day: int
    reminder_time: str
    days_of_week: str
    is_active: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# FastAPI приложение
app = FastAPI(title="Дневник растений", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статические файлы для фото
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Утилиты
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# API Endpoints
@app.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# Растения
@app.post("/plants", response_model=PlantResponse)
def create_plant(plant: PlantCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_plant = Plant(**plant.dict(), user_id=current_user.id)
    db.add(db_plant)
    db.commit()
    db.refresh(db_plant)
    return db_plant

@app.get("/plants", response_model=List[PlantResponse])
def get_plants(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plants = db.query(Plant).filter(Plant.user_id == current_user.id).all()
    return plants

@app.get("/plants/{plant_id}", response_model=PlantResponse)
def get_plant(plant_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plant = db.query(Plant).filter(Plant.id == plant_id, Plant.user_id == current_user.id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant

@app.delete("/plants/{plant_id}")
def delete_plant(plant_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plant = db.query(Plant).filter(Plant.id == plant_id, Plant.user_id == current_user.id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    db.delete(plant)
    db.commit()
    return {"message": "Plant deleted"}

# Записи дневника
@app.post("/plants/{plant_id}/entries", response_model=PlantEntryResponse)
def create_entry(plant_id: int, entry: PlantEntryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plant = db.query(Plant).filter(Plant.id == plant_id, Plant.user_id == current_user.id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    
    db_entry = PlantEntry(**entry.dict(), plant_id=plant_id)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@app.get("/plants/{plant_id}/entries", response_model=List[PlantEntryResponse])
def get_entries(plant_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plant = db.query(Plant).filter(Plant.id == plant_id, Plant.user_id == current_user.id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    
    entries = db.query(PlantEntry).filter(PlantEntry.plant_id == plant_id).order_by(PlantEntry.entry_date.desc()).all()
    return entries

# Фото
@app.post("/plants/{plant_id}/photos")
async def upload_photo(plant_id: int, file: UploadFile = File(...), description: Optional[str] = None, 
                       current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plant = db.query(Plant).filter(Plant.id == plant_id, Plant.user_id == current_user.id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    
    # Сохранение файла
    file_ext = file.filename.split(".")[-1]
    filename = f"{plant_id}_{datetime.now().timestamp()}.{file_ext}"
    file_path = UPLOAD_DIR / filename
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    db_photo = PlantPhoto(plant_id=plant_id, photo_path=f"/uploads/{filename}", description=description)
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    
    return {"id": db_photo.id, "photo_path": db_photo.photo_path, "description": db_photo.description}

@app.get("/plants/{plant_id}/photos")
def get_photos(plant_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plant = db.query(Plant).filter(Plant.id == plant_id, Plant.user_id == current_user.id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    
    photos = db.query(PlantPhoto).filter(PlantPhoto.plant_id == plant_id).order_by(PlantPhoto.created_at.desc()).all()
    return [{"id": p.id, "photo_path": p.photo_path, "description": p.description, "created_at": p.created_at} for p in photos]

# Напоминания
@app.post("/plants/{plant_id}/reminders", response_model=ReminderResponse)
def create_reminder(plant_id: int, reminder: ReminderCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plant = db.query(Plant).filter(Plant.id == plant_id, Plant.user_id == current_user.id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    
    db_reminder = Reminder(
        plant_id=plant_id,
        reminder_type=reminder.reminder_type,
        times_per_day=reminder.times_per_day,
        reminder_time=reminder.reminder_time,
        days_of_week=reminder.days_of_week
    )
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

@app.get("/plants/{plant_id}/reminders", response_model=List[ReminderResponse])
def get_reminders(plant_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plant = db.query(Plant).filter(Plant.id == plant_id, Plant.user_id == current_user.id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    
    reminders = db.query(Reminder).filter(Reminder.plant_id == plant_id).all()  # Показываем все, не только активные
    return reminders

@app.delete("/reminders/{reminder_id}")
def delete_reminder(reminder_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    reminder = db.query(Reminder).join(Plant).filter(
        Reminder.id == reminder_id,
        Plant.user_id == current_user.id
    ).first()
    
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    db.delete(reminder)
    db.commit()
    return {"message": "Reminder deleted"}

@app.get("/reminders/upcoming")
def get_upcoming_reminders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plants = db.query(Plant).filter(Plant.user_id == current_user.id).all()
    plant_ids = [p.id for p in plants]
    
    reminders = db.query(Reminder).filter(
        Reminder.plant_id.in_(plant_ids),
        Reminder.is_active == True
    ).all()
    
    result = []
    now = datetime.utcnow()
    current_weekday = now.weekday()  # 0=Monday, 6=Sunday
    
    for rem in reminders:
        days_list = [int(d) for d in rem.days_of_week.split(",")]
        if current_weekday in days_list:
            plant = db.query(Plant).filter(Plant.id == rem.plant_id).first()
            result.append({
                "id": rem.id,
                "plant_name": plant.name,
                "reminder_type": rem.reminder_type,
                "reminder_time": rem.reminder_time,
                "times_per_day": rem.times_per_day
            })
    
    return result

@app.post("/reminders/{reminder_id}/complete")
def complete_reminder(reminder_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    reminder = db.query(Reminder).join(Plant).filter(
        Reminder.id == reminder_id,
        Plant.user_id == current_user.id
    ).first()
    
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    # Напоминание просто остается активным, выполнение отмечается в записях дневника
    return {"message": "Reminder completed"}

@app.get("/")
def root():
    return {"message": "Дневник растений API", "version": "1.0.0"}

