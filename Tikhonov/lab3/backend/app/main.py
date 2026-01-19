from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel, EmailStr
import logging
from .database import get_db, init_db
from .models import User
from .auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from .memes import router as memes_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Meme Generator API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутер для мемов
app.include_router(memes_router)


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


class Token(BaseModel):
    access_token: str
    token_type: str


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске приложения"""
    import asyncio
    logger.info("Запуск приложения...")
    # Даем время PostgreSQL полностью запуститься
    await asyncio.sleep(2)
    try:
        init_db()
        logger.info("Приложение готово к работе")
    except Exception as e:
        logger.error(f"Ошибка при инициализации БД: {e}")
        raise


@app.post("/api/auth/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    logger.info(f"Регистрация нового пользователя: {user.username}")
    # Проверяем, существует ли пользователь
    db_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if db_user:
        logger.warning(f"Пользователь уже существует: {user.username}")
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered"
        )

    # Создаем нового пользователя
    hashed_password = get_password_hash(user.password)
    logger.info(f"Пароль захеширован, длина хеша: {len(hashed_password)}")
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"Пользователь успешно зарегистрирован: {db_user.username}")
    return db_user


@app.post("/api/auth/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Авторизация пользователя"""
    logger.info(f"Попытка входа пользователя: {form_data.username}")
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user:
        logger.warning(f"Пользователь не найден: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"Пользователь найден: {user.username}, проверка пароля...")
    if not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Неверный пароль для пользователя: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f"Успешный вход пользователя: {form_data.username}")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/auth/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Получение информации о текущем пользователе"""
    return current_user


@app.get("/")
def root():
    return {"message": "Meme Generator API"}

