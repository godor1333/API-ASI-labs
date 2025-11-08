# app/bot.py

import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from typing import Dict, Optional
from datetime import datetime

# Настройки
API_URL = os.getenv("API_URL", "http://backend:8000")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8559943094:AAGrehiOIitIza5Gospac74yxhRzzZrcCEU")
if not BOT_TOKEN:
    print("Ошибка: Переменная окружения BOT_TOKEN не установлена!")
    exit(1)

# Список ID администраторов (можно задать через переменную окружения)
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]

# Хранилище токенов пользователей (в production использовать Redis или БД)
user_tokens: Dict[int, str] = {}

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_headers(user_id: int) -> Dict[str, str]:
    """Получить заголовки с токеном для API запросов"""
    token = user_tokens.get(user_id)
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def is_admin(user_id: int) -> bool:
    """Проверить, является ли пользователь администратором"""
    return user_id in ADMIN_IDS

def get_main_keyboard():
    """Получить основную клавиатуру с функциональными кнопками"""
    keyboard = [
        [KeyboardButton("🌿 Мои растения"), KeyboardButton("🔔 Напоминания")],
        [KeyboardButton("➕ Добавить растение"), KeyboardButton("🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, persistent=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    if user_id in user_tokens:
        keyboard = [
            [InlineKeyboardButton("🌿 Мои растения", callback_data="plants")],
            [InlineKeyboardButton("🔔 Напоминания", callback_data="reminders")],
            [InlineKeyboardButton("➕ Добавить растение", callback_data="add_plant_menu")],
            [InlineKeyboardButton("🚪 Выйти", callback_data="logout")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message_text = "🌱 Добро пожаловать в Дневник растений!\nВыберите действие:"
        if update.message:
            await update.message.reply_text(message_text, reply_markup=reply_markup)
            # Добавляем постоянные кнопки для авторизованных пользователей
            await update.message.reply_text(
                "Используйте кнопки внизу для быстрого доступа:",
                reply_markup=get_main_keyboard()
            )
        elif update.callback_query:
            await update.callback_query.edit_message_text(message_text, reply_markup=reply_markup)
    else:
        keyboard = [
            [InlineKeyboardButton("🔐 Войти", callback_data="login")],
            [InlineKeyboardButton("📝 Зарегистрироваться", callback_data="register")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message_text = (
            "🌱 Добро пожаловать в Дневник растений!\n"
            "Для начала работы необходимо войти или зарегистрироваться."
        )
        if update.message:
            await update.message.reply_text(message_text, reply_markup=reply_markup)
        elif update.callback_query:
            await update.callback_query.edit_message_text(message_text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    if not query:
        return
    await query.answer()

    user_id = update.effective_user.id
    data = query.data

    # Проверка авторизации для защищенных действий
    protected_actions = ["plants", "add_plant_menu", "reminders", "plant_", "entry_", "photo_", "reminder_", "view_", "delete_"]
    if any(data.startswith(action) or data == action for action in protected_actions):
        if user_id not in user_tokens:
            await query.edit_message_text("❌ Сначала войдите в систему.")
            await start(update, context)
            return

    # Главное меню
    if data == "back_to_menu":
        await start(update, context)
        return

    # Авторизация
    if data == "login":
        await query.edit_message_text("Введите ваше имя пользователя:")
        context.user_data["action"] = "login_username"
        return
    if data == "register":
        await query.edit_message_text("Введите имя пользователя для регистрации:")
        context.user_data["action"] = "register_username"
        return
    if data == "logout":
        if user_id in user_tokens:
            del user_tokens[user_id]
        await query.edit_message_text("Вы вышли из системы.")
        await start(update, context)
        return

    # Растения
    if data == "plants":
        await show_plants(update, context)
        return
    if data == "add_plant_menu":
        await show_add_plant_menu(update, context)
        return
    if data.startswith("add_plant_"):
        if data == "add_plant_custom":
            await query.edit_message_text("Введите название растения:")
            context.user_data["action"] = "add_plant_name"
            return
        plant_name = data.replace("add_plant_", "")
        context.user_data["plant_name"] = plant_name
        await show_add_plant_species(update, context, plant_name)
        return
    if data.startswith("add_species_skip_"):
        plant_name = data.replace("add_species_skip_", "")
        context.user_data["plant_name"] = plant_name
        context.user_data["plant_species"] = None
        await show_add_plant_description(update, context)
        return
    if data == "add_desc_skip":
        await save_plant(update, context)
        return
    if data.startswith("plant_"):
        plant_id = int(data.split("_")[1])
        await show_plant_detail(update, context, plant_id)
        return

    # Записи
    if data.startswith("entry_"):
        plant_id = int(data.split("_")[1])
        await show_add_entry_menu(update, context, plant_id)
        return
    if data.startswith("entry_type_"):
        parts = data.split("_")
        plant_id = int(parts[2])
        entry_type = parts[3] if len(parts) > 3 else "notes"
        await show_entry_notes(update, context, plant_id, entry_type)
        return

    # Фото
    if data.startswith("photo_"):
        plant_id = int(data.split("_")[1])
        await query.edit_message_text("Отправьте фото растения:")
        context.user_data["action"] = "add_photo"
        context.user_data["plant_id"] = plant_id
        return

    # Напоминания
    if data == "reminders":
        await show_reminders(update, context)
        return
    if data.startswith("reminder_"):
        plant_id = int(data.split("_")[1])
        await show_reminder_type_menu(update, context, plant_id)
        return
    if data.startswith("rem_type_"):
        parts = data.split("_")
        plant_id = int(parts[2])
        rem_type = parts[3]
        context.user_data["reminder_plant_id"] = plant_id
        context.user_data["reminder_type"] = rem_type
        await show_times_per_day_menu(update, context)
        return
    if data.startswith("times_"):
        times = int(data.split("_")[1])
        context.user_data["reminder_times_per_day"] = times
        await show_time_menu(update, context)
        return
    if data.startswith("time_"):
        time_str = data.replace("time_", "").replace("_", ":")
        context.user_data["reminder_time"] = time_str
        await show_days_of_week_menu(update, context)
        return
    if data.startswith("day_"):
        day = data.split("_")[1]
        if "reminder_days" not in context.user_data:
            context.user_data["reminder_days"] = []
        if day in context.user_data["reminder_days"]:
            context.user_data["reminder_days"].remove(day)
        else:
            context.user_data["reminder_days"].append(day)
        await show_days_of_week_menu(update, context)
        return
    if data == "reminder_save":
        await save_reminder(update, context)
        return
    if data == "reminder_cancel":
        context.user_data.pop("reminder_plant_id", None)
        context.user_data.pop("reminder_type", None)
        context.user_data.pop("reminder_times_per_day", None)
        context.user_data.pop("reminder_time", None)
        context.user_data.pop("reminder_days", None)
        await start(update, context)
        return

    # Просмотр записей
    if data.startswith("view_entries_"):
        plant_id = int(data.split("_")[2])
        await show_plant_entries(update, context, plant_id)
        return

    # Просмотр фото
    if data.startswith("view_photos_"):
        plant_id = int(data.split("_")[2])
        await show_plant_photos(update, context, plant_id)
        return

    # Просмотр напоминаний растения
    if data.startswith("view_reminders_"):
        plant_id = int(data.split("_")[2])
        await show_plant_reminders(update, context, plant_id)
        return

    # Удаление растения
    if data.startswith("delete_plant_"):
        plant_id = int(data.split("_")[2])
        await confirm_delete_plant(update, context, plant_id)
        return
    if data.startswith("confirm_delete_plant_"):
        plant_id = int(data.split("_")[3])
        await delete_plant(update, context, plant_id)
        return

    # Удаление напоминания
    if data.startswith("delete_reminder_"):
        reminder_id = int(data.split("_")[2])
        await delete_reminder(update, context, reminder_id)
        return

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений (только для авторизации)"""
    user_id = update.effective_user.id
    text = update.message.text.strip() if update.message.text else ""
    action = context.user_data.get("action")

    if not text:
        await update.message.reply_text("❌ Пожалуйста, введите текст.")
        return

    if action == "login_username":
        if len(text) < 3:
            await update.message.reply_text("❌ Имя пользователя должно быть не менее 3 символов.")
            return
        context.user_data["username"] = text
        await update.message.reply_text("Введите пароль:")
        context.user_data["action"] = "login_password"
    elif action == "login_password":
        if len(text) < 4:
            await update.message.reply_text("❌ Пароль должен быть не менее 4 символов.")
            return
        username = context.user_data.get("username")
        password = text
        form_data = {
            "username": username,
            "password": password
        }
        try:
            response = requests.post(f"{API_URL}/token", data=form_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                user_tokens[user_id] = data["access_token"]
                await update.message.reply_text("✅ Вы успешно вошли!")
                context.user_data.clear()
                await start(update, context)
                # Добавляем постоянные кнопки после входа
                await update.message.reply_text(
                    "Используйте кнопки внизу для быстрого доступа:",
                    reply_markup=get_main_keyboard()
                )
            elif response.status_code == 401:
                await update.message.reply_text("❌ Неверное имя пользователя или пароль.")
                context.user_data.clear()
            else:
                error_msg = response.json().get("detail", "Неверное имя пользователя или пароль")
                await update.message.reply_text(f"❌ {error_msg}")
                context.user_data.clear()
        except requests.exceptions.Timeout:
            await update.message.reply_text("❌ Превышено время ожидания. Попробуйте позже.")
        except Exception as e:
            logger.error(f"Login error: {e}")
            await update.message.reply_text("❌ Ошибка подключения к серверу.")
    elif action == "register_username":
        if len(text) < 3:
            await update.message.reply_text("❌ Имя пользователя должно быть не менее 3 символов.")
            return
        context.user_data["reg_username"] = text
        await update.message.reply_text("Введите email:")
        context.user_data["action"] = "register_email"
    elif action == "register_email":
        if "@" not in text or "." not in text:
            await update.message.reply_text("❌ Введите корректный email адрес.")
            return
        context.user_data["reg_email"] = text
        await update.message.reply_text("Введите пароль (минимум 4 символа):")
        context.user_data["action"] = "register_password"
    elif action == "register_password":
        if len(text) < 4:
            await update.message.reply_text("❌ Пароль должен быть не менее 4 символов.")
            return
        username = context.user_data.get("reg_username")
        email = context.user_data.get("reg_email")
        password = text
        try:
            response = requests.post(
                f"{API_URL}/register",
                json={"username": username, "email": email, "password": password},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if response.status_code == 200:
                await update.message.reply_text("✅ Регистрация успешна! Теперь войдите в систему.")
                context.user_data.clear()
                await start(update, context)
                # После регистрации показываем кнопки входа
                keyboard = [
                    [InlineKeyboardButton("🔐 Войти", callback_data="login")],
                    [InlineKeyboardButton("📝 Зарегистрироваться", callback_data="register")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    "Войдите в систему:",
                    reply_markup=reply_markup
                )
            elif response.status_code == 400:
                error = response.json().get("detail", "Ошибка регистрации: Неверный формат данных")
                await update.message.reply_text(f"❌ {error}")
                context.user_data.clear()
            else:
                error = response.json().get("detail", "Ошибка регистрации")
                await update.message.reply_text(f"❌ {error}")
                context.user_data.clear()
        except requests.exceptions.Timeout:
            await update.message.reply_text("❌ Превышено время ожидания. Попробуйте позже.")
        except Exception as e:
            logger.error(f"Register error: {e}")
            await update.message.reply_text("❌ Ошибка подключения к серверу.")
    elif action == "add_plant_name":
        if len(text) < 2:
            await update.message.reply_text("❌ Название растения должно быть не менее 2 символов.")
            return
        context.user_data["plant_name"] = text
        keyboard = [
            [InlineKeyboardButton("Пропустить", callback_data=f"add_species_skip_{text}")],
            [InlineKeyboardButton("🔙 Назад", callback_data="add_plant_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"Растение: {text}\nВведите вид/сорт или пропустите:",
            reply_markup=reply_markup
        )
        context.user_data["action"] = "add_plant_species"
    elif action == "add_plant_species":
        context.user_data["plant_species"] = text
        keyboard = [
            [InlineKeyboardButton("Пропустить", callback_data="add_desc_skip")],
            [InlineKeyboardButton("🔙 Назад", callback_data="add_plant_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Введите описание или пропустите:",
            reply_markup=reply_markup
        )
        context.user_data["action"] = "add_plant_description"
    elif action == "add_plant_description":
        context.user_data["plant_description"] = text
        await save_plant_from_message(update, context)
    elif action == "add_photo":
        # Обработка фото будет в handle_photo
        pass
    else:
        # Обработка текстовых команд через постоянные кнопки
        if user_id in user_tokens:
            text_lower = text.lower()
            if text_lower in ["🌿 мои растения", "мои растения", "растения"]:
                await show_plants(update, context)
                return
            elif text_lower in ["🔔 напоминания", "напоминания"]:
                await show_reminders(update, context)
                return
            elif text_lower in ["➕ добавить растение", "добавить растение", "новое растение"]:
                await show_add_plant_menu_from_text(update, context)
                return
            elif text_lower in ["🏠 главное меню", "главное меню", "меню"]:
                await start(update, context)
                return
            else:
                keyboard = [
                    [InlineKeyboardButton("🌿 Мои растения", callback_data="plants")],
                    [InlineKeyboardButton("🔔 Напоминания", callback_data="reminders")],
                    [InlineKeyboardButton("➕ Добавить растение", callback_data="add_plant_menu")],
                    [InlineKeyboardButton("🚪 Выйти", callback_data="logout")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    "Используйте кнопки внизу экрана или выберите действие:",
                    reply_markup=reply_markup
                )
                await update.message.reply_text(
                    "Или используйте постоянные кнопки внизу:",
                    reply_markup=get_main_keyboard()
                )
        else:
            await start(update, context)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик фотографий"""
    user_id = update.effective_user.id
    action = context.user_data.get("action")
    if action == "add_photo":
        plant_id = context.user_data.get("plant_id")
        photo = update.message.photo[-1] # Берем фото с наивысшим разрешением
        try:
            file = await context.bot.get_file(photo.file_id)
            photo_bytes = await file.download_as_bytearray()

            # Проверка размера файла (макс 10 МБ) перед загрузкой
            if photo.file_size > 10 * 1024 * 1024:
                 await update.message.reply_text("❌ Фото слишком большое. Максимальный размер: 10 МБ")
                 return

            # Проверка размера файла (макс 10 МБ) после загрузки
            if len(photo_bytes) > 10 * 1024 * 1024:
                await update.message.reply_text("❌ Фото слишком большое. Максимальный размер: 10 МБ")
                return

            import io
            files = {"file": ("photo.jpg", io.BytesIO(photo_bytes), "image/jpeg")}
            response = requests.post(
                f"{API_URL}/plants/{plant_id}/photos",
                files=files,
                headers=get_headers(user_id),
                timeout=30
            )
            if response.status_code == 200:
                await update.message.reply_text("✅ Фото загружено!")
                saved_plant_id = plant_id
                context.user_data.clear()
                # Показываем кнопки для возврата к растению
                keyboard = [
                    [InlineKeyboardButton("🔙 К растению", callback_data=f"plant_{saved_plant_id}")],
                    [InlineKeyboardButton("🌿 Мои растения", callback_data="plants")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)
            elif response.status_code == 401:
                await update.message.reply_text("❌ Сессия истекла. Войдите снова.")
                if user_id in user_tokens:
                    del user_tokens[user_id]
                await start(update, context)
            elif response.status_code == 404:
                 await update.message.reply_text("❌ Растение не найдено.")
                 await show_plants(update, context)
            else:
                error_msg = response.json().get("detail", "Ошибка при загрузке фото")
                await update.message.reply_text(f"❌ {error_msg}")
        except requests.exceptions.Timeout:
            await update.message.reply_text("❌ Превышено время ожидания при загрузке фото.")
        except Exception as e:
            logger.error(f"Photo upload error: {e}")
            await update.message.reply_text("❌ Ошибка при загрузке фото.")

async def show_plants(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список растений"""
    user_id = update.effective_user.id
    if user_id not in user_tokens:
        if update.callback_query:
            await update.callback_query.edit_message_text("❌ Сначала войдите в систему.")
        elif update.message:
            await update.message.reply_text("❌ Сначала войдите в систему.")
        await start(update, context)
        return

    try:
        response = requests.get(f"{API_URL}/plants", headers=get_headers(user_id), timeout=10)
        if response.status_code == 200:
            plants = response.json()
            if not plants:
                keyboard = [
                    [InlineKeyboardButton("➕ Добавить растение", callback_data="add_plant_menu")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message_text = "У вас пока нет растений.\nДобавьте первое растение!"
                if update.callback_query:
                    await update.callback_query.edit_message_text(message_text, reply_markup=reply_markup)
                elif update.message:
                    await update.message.reply_text(message_text, reply_markup=reply_markup)
                    await update.message.reply_text("Используйте кнопки внизу:", reply_markup=get_main_keyboard())
                return
            text = "🌿 Ваши растения:\n"
            keyboard = []
            for plant in plants:
                text += f"🌱 {plant['name']}\n"
                if plant.get('species'):
                    text += f"   Вид: {plant['species']}\n"
                text += "\n"
                keyboard.append([InlineKeyboardButton(
                    f"🌱 {plant['name']}",
                    callback_data=f"plant_{plant['id']}"
                )])
            keyboard.append([InlineKeyboardButton("➕ Добавить растение", callback_data="add_plant_menu")])
            keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            if update.callback_query:
                await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
            elif update.message:
                await update.message.reply_text(text, reply_markup=reply_markup)
                await update.message.reply_text("Используйте кнопки внизу:", reply_markup=get_main_keyboard())
        elif response.status_code == 401:
            message_text = "❌ Сессия истекла. Войдите снова."
            if update.callback_query:
                await update.callback_query.edit_message_text(message_text)
            elif update.message:
                await update.message.reply_text(message_text)
            if user_id in user_tokens:
                del user_tokens[user_id]
            await start(update, context)
        else:
            error_msg = response.json().get("detail", "Ошибка при загрузке растений")
            message_text = f"❌ {error_msg}"
            if update.callback_query:
                await update.callback_query.edit_message_text(message_text)
            elif update.message:
                await update.message.reply_text(message_text)
    except requests.exceptions.Timeout:
        message_text = "❌ Превышено время ожидания. Попробуйте позже."
        if update.callback_query:
            await update.callback_query.edit_message_text(message_text)
        elif update.message:
            await update.message.reply_text(message_text)
    except Exception as e:
        logger.error(f"Show plants error: {e}")
        message_text = "❌ Ошибка подключения к серверу."
        if update.callback_query:
            await update.callback_query.edit_message_text(message_text)
        elif update.message:
            await update.message.reply_text(message_text)

async def show_add_plant_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню добавления растения - выбор названия"""
    # Предустановленные названия или можно ввести свое
    keyboard = [
        [InlineKeyboardButton("🌿 Фикус", callback_data="add_plant_Фикус")],
        [InlineKeyboardButton("🌱 Кактус", callback_data="add_plant_Кактус")],
        [InlineKeyboardButton("🌺 Орхидея", callback_data="add_plant_Орхидея")],
        [InlineKeyboardButton("🌿 Монстера", callback_data="add_plant_Монстера")],
        [InlineKeyboardButton("🌱 Суккулент", callback_data="add_plant_Суккулент")],
        [InlineKeyboardButton("🌿 Другое", callback_data="add_plant_custom")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        "Выберите название растения из списка или нажмите 'Другое' для ввода своего:",
        reply_markup=reply_markup
    )

async def show_add_plant_menu_from_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню добавления растения из текстового сообщения"""
    keyboard = [
        [InlineKeyboardButton("🌿 Фикус", callback_data="add_plant_Фикус")],
        [InlineKeyboardButton("🌱 Кактус", callback_data="add_plant_Кактус")],
        [InlineKeyboardButton("🌺 Орхидея", callback_data="add_plant_Орхидея")],
        [InlineKeyboardButton("🌿 Монстера", callback_data="add_plant_Монстера")],
        [InlineKeyboardButton("🌱 Суккулент", callback_data="add_plant_Суккулент")],
        [InlineKeyboardButton("🌿 Другое", callback_data="add_plant_custom")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Выберите название растения из списка или нажмите 'Другое' для ввода своего:",
        reply_markup=reply_markup
    )

async def show_add_plant_species(update: Update, context: ContextTypes.DEFAULT_TYPE, plant_name: str):
    """Выбор вида растения"""
    keyboard = [
        [InlineKeyboardButton("Пропустить", callback_data=f"add_species_skip_{plant_name}")],
        [InlineKeyboardButton("🔙 Назад", callback_data="add_plant_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        f"Растение: {plant_name}\nВведите вид/сорт или пропустите:",
        reply_markup=reply_markup
    )
    context.user_data["plant_name"] = plant_name
    context.user_data["action"] = "add_plant_species"

async def show_add_plant_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор описания растения"""
    keyboard = [
        [InlineKeyboardButton("Пропустить", callback_data="add_desc_skip")],
        [InlineKeyboardButton("🔙 Назад", callback_data="add_plant_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    plant_name = context.user_data.get("plant_name", "")
    await update.callback_query.edit_message_text(
        f"Растение: {plant_name}\nВведите описание или пропустите:",
        reply_markup=reply_markup
    )
    context.user_data["action"] = "add_plant_description"

async def save_plant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение растения из callback"""
    user_id = update.effective_user.id
    name = context.user_data.get("plant_name")
    species = context.user_data.get("plant_species")
    description = context.user_data.get("plant_description")

    try:
        response = requests.post(
            f"{API_URL}/plants",
            json={"name": name, "species": species, "description": description},
            headers={**get_headers(user_id), "Content-Type": "application/json"}
        )
        if response.status_code == 200:
            await update.callback_query.edit_message_text("✅ Растение добавлено!")
            context.user_data.clear()
            await show_plants(update, context)
        elif response.status_code == 401:
            await update.callback_query.edit_message_text("❌ Сессия истекла. Войдите снова.")
            if user_id in user_tokens:
                del user_tokens[user_id]
            await start(update, context)
        else:
            error_msg = response.json().get("detail", "Ошибка при добавлении растения")
            await update.callback_query.edit_message_text(f"❌ {error_msg}")
    except Exception as e:
        logger.error(f"Add plant error: {e}")
        await update.callback_query.edit_message_text("❌ Ошибка подключения к серверу.")

async def save_plant_from_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение растения из текстового сообщения"""
    user_id = update.effective_user.id
    name = context.user_data.get("plant_name")
    species = context.user_data.get("plant_species")
    description = context.user_data.get("plant_description")

    try:
        response = requests.post(
            f"{API_URL}/plants",
            json={"name": name, "species": species, "description": description},
            headers={**get_headers(user_id), "Content-Type": "application/json"}
        )
        if response.status_code == 200:
            await update.message.reply_text("✅ Растение добавлено!")
            context.user_data.clear()
            # Возвращаемся к списку растений
            await show_plants(update, context)
        elif response.status_code == 401:
            await update.message.reply_text("❌ Сессия истекла. Войдите снова.")
            if user_id in user_tokens:
                del user_tokens[user_id]
            await start(update, context)
        else:
            error_msg = response.json().get("detail", "Ошибка при добавлении растения")
            await update.message.reply_text(f"❌ {error_msg}")
    except Exception as e:
        logger.error(f"Add plant error: {e}")
        await update.message.reply_text("❌ Ошибка подключения к серверу.")

async def show_plant_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, plant_id: int):
    """Показать детали растения"""
    user_id = update.effective_user.id
    try:
        plant_response = requests.get(
            f"{API_URL}/plants/{plant_id}",
            headers=get_headers(user_id)
        )
        if plant_response.status_code == 404:
            await update.callback_query.edit_message_text("❌ Растение не найдено.")
            await show_plants(update, context)
            return
        elif plant_response.status_code != 200:
            if plant_response.status_code == 401:
                await update.callback_query.edit_message_text("❌ Сессия истекла. Войдите снова.")
                if user_id in user_tokens:
                    del user_tokens[user_id]
                await start(update, context)
            else:
                await update.callback_query.edit_message_text("❌ Ошибка при загрузке растения.")
            return

        plant = plant_response.json()
        entries_response = requests.get(
            f"{API_URL}/plants/{plant_id}/entries",
            headers=get_headers(user_id)
        )
        photos_response = requests.get(
            f"{API_URL}/plants/{plant_id}/photos",
            headers=get_headers(user_id)
        )
        reminders_response = requests.get(
            f"{API_URL}/plants/{plant_id}/reminders",
            headers=get_headers(user_id)
        )

        entries = entries_response.json() if entries_response.status_code == 200 else []
        photos = photos_response.json() if photos_response.status_code == 200 else []
        reminders = reminders_response.json() if reminders_response.status_code == 200 else []

        text = f"🌱 {plant['name']}\n"
        if plant.get('species'):
            text += f"Вид: {plant['species']}\n"
        if plant.get('description'):
            text += f"Описание: {plant['description']}\n"
        text += f"\n📝 Записей: {len(entries)}\n"
        text += f"📷 Фото: {len(photos)}\n"
        text += f"🔔 Напоминаний: {len(reminders)}\n"

        keyboard = [
            [InlineKeyboardButton("📝 Записи", callback_data=f"view_entries_{plant_id}"),
             InlineKeyboardButton("📷 Фото", callback_data=f"view_photos_{plant_id}")],
            [InlineKeyboardButton("🔔 Напоминания", callback_data=f"view_reminders_{plant_id}")],
            [InlineKeyboardButton("📝 Добавить запись", callback_data=f"entry_{plant_id}")],
            [InlineKeyboardButton("📷 Добавить фото", callback_data=f"photo_{plant_id}")],
            [InlineKeyboardButton("🔔 Добавить напоминание", callback_data=f"reminder_{plant_id}")],
            [InlineKeyboardButton("🗑️ Удалить растение", callback_data=f"delete_plant_{plant_id}")],
            [InlineKeyboardButton("🔙 К списку растений", callback_data="plants")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
        elif update.message:
            await update.message.reply_text(text, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Show plant detail error: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text("❌ Ошибка подключения к серверу.")
        elif update.message:
            await update.message.reply_text("❌ Ошибка подключения к серверу.")

async def show_add_entry_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, plant_id: int):
    """Меню добавления записи"""
    keyboard = [
        [InlineKeyboardButton("💧 Полив", callback_data=f"entry_type_{plant_id}_watering")],
        [InlineKeyboardButton("🌿 Удобрение", callback_data=f"entry_type_{plant_id}_fertilizing")],
        [InlineKeyboardButton("✂️ Обрезка", callback_data=f"entry_type_{plant_id}_pruning")],
        [InlineKeyboardButton("📝 Заметка", callback_data=f"entry_type_{plant_id}_notes")],
        [InlineKeyboardButton("🔙 Назад", callback_data=f"plant_{plant_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        "Выберите тип записи:",
        reply_markup=reply_markup
    )

async def show_entry_notes(update: Update, context: ContextTypes.DEFAULT_TYPE, plant_id: int, entry_type: str):
    """Добавление записи с выбранным типом"""
    user_id = update.effective_user.id
    entry_data = {
        "notes": "",
        "watering": entry_type == "watering",
        "fertilizing": entry_type == "fertilizing",
        "pruning": entry_type == "pruning",
        "other_care": None
    }
    if entry_type == "notes":
        entry_data["notes"] = "Заметка"

    try:
        response = requests.post(
            f"{API_URL}/plants/{plant_id}/entries",
            json=entry_data,
            headers={**get_headers(user_id), "Content-Type": "application/json"}
        )
        if response.status_code == 200:
            await update.callback_query.edit_message_text("✅ Запись добавлена!")
            await show_plant_detail(update, context, plant_id)
        elif response.status_code == 401:
            await update.callback_query.edit_message_text("❌ Сессия истекла. Войдите снова.")
            if user_id in user_tokens:
                del user_tokens[user_id]
            await start(update, context)
        elif response.status_code == 404:
            await update.callback_query.edit_message_text("❌ Растение не найдено.")
            await show_plants(update, context)
        else:
            error_msg = response.json().get("detail", "Ошибка при добавлении записи")
            await update.callback_query.edit_message_text(f"❌ {error_msg}")
    except Exception as e:
        logger.error(f"Add entry error: {e}")
        await update.callback_query.edit_message_text("❌ Ошибка подключения к серверу.")

async def show_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать предстоящие напоминания"""
    user_id = update.effective_user.id
    if user_id not in user_tokens:
        if update.callback_query:
            await update.callback_query.edit_message_text("❌ Сначала войдите в систему.")
        elif update.message:
            await update.message.reply_text("❌ Сначала войдите в систему.")
        await start(update, context)
        return

    try:
        response = requests.get(
            f"{API_URL}/reminders/upcoming",
            headers=get_headers(user_id),
            timeout=10
        )
        if response.status_code == 200:
            reminders = response.json()
            if not reminders:
                keyboard = [
                    [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message_text = "Нет предстоящих напоминаний."
                if update.callback_query:
                    await update.callback_query.edit_message_text(message_text, reply_markup=reply_markup)
                elif update.message:
                    await update.message.reply_text(message_text, reply_markup=reply_markup)
                    await update.message.reply_text("Используйте кнопки внизу:", reply_markup=get_main_keyboard())
                return
            text = "🔔 Предстоящие напоминания:\n"
            for rem in reminders:
                text += f"🌱 {rem['plant_name']}\n"
                text += f"   {rem['reminder_type']}\n"
                text += f"   Время: {rem['reminder_time']}\n"
                text += f"   Раз в день: {rem['times_per_day']}\n"
            keyboard = [
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            if update.callback_query:
                await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
            elif update.message:
                await update.message.reply_text(text, reply_markup=reply_markup)
                await update.message.reply_text("Используйте кнопки внизу:", reply_markup=get_main_keyboard())
        elif response.status_code == 401:
            message_text = "❌ Сессия истекла. Войдите снова."
            if update.callback_query:
                await update.callback_query.edit_message_text(message_text)
            elif update.message:
                await update.message.reply_text(message_text)
            if user_id in user_tokens:
                del user_tokens[user_id]
            await start(update, context)
        else:
            message_text = "❌ Ошибка при загрузке напоминаний."
            if update.callback_query:
                await update.callback_query.edit_message_text(message_text)
            elif update.message:
                await update.message.reply_text(message_text)
    except Exception as e:
        logger.error(f"Show reminders error: {e}")
        message_text = "❌ Ошибка подключения к серверу."
        if update.callback_query:
            await update.callback_query.edit_message_text(message_text)
        elif update.message:
            await update.message.reply_text(message_text)

async def get_my_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для получения своего Telegram ID"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "без username"
    await update.message.reply_text(
        f"Ваш Telegram ID: `{user_id}`\n"
        f"Username: @{username}\n"
        f"Добавьте этот ID в переменную ADMIN_IDS для получения прав администратора.",
        parse_mode='Markdown'
    )

async def admin_check_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Админ команда для проверки всех напоминаний"""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ У вас нет прав администратора.\n"
            "Используйте /myid чтобы узнать свой Telegram ID и добавить его в ADMIN_IDS."
        )
        return

    if user_id not in user_tokens:
        await update.message.reply_text("❌ Сначала войдите в систему.")
        return

    try:
        # Получаем все растения админа
        plants_response = requests.get(
            f"{API_URL}/plants",
            headers=get_headers(user_id)
        )

        if plants_response.status_code == 401:
            await update.message.reply_text("❌ Сессия истекла. Войдите снова.")
            if user_id in user_tokens:
                del user_tokens[user_id]
            return
        elif plants_response.status_code != 200:
            await update.message.reply_text("❌ Ошибка при получении растений.")
            return

        plants = plants_response.json()
        if not plants:
            await update.message.reply_text("📋 Нет растений для проверки.")
            return

        text = "📋 **Статистика напоминаний:**\n"
        total_reminders = 0
        active_reminders = 0
        for plant in plants:
            reminders_response = requests.get(
                f"{API_URL}/plants/{plant['id']}/reminders",
                headers=get_headers(user_id)
            )
            if reminders_response.status_code == 200:
                reminders = reminders_response.json()
                total_reminders += len(reminders)
                active_count = sum(1 for r in reminders if r.get('is_active', True))
                active_reminders += active_count
                if reminders:
                    text += f"🌱 *{plant['name']}*\n"
                    for rem in reminders:
                        status = "✅" if rem.get('is_active', True) else "❌"
                        days_list = rem.get('days_of_week', '').split(',')
                        days_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
                        days_display = ", ".join([days_names[int(d)] for d in days_list if d.isdigit()])
                        text += f"  {status} {rem['reminder_type']}\n"
                        text += f"     Время: {rem['reminder_time']}\n"
                        text += f"     Раз в день: {rem['times_per_day']}\n"
                        text += f"     Дни: {days_display}\n"
        text += f"\n📊 **Итого:**\n"
        text += f"Всего напоминаний: {total_reminders}\n"
        text += f"Активных: {active_reminders}\n"
        text += f"Неактивных: {total_reminders - active_reminders}"

        await update.message.reply_text(text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Admin check reminders error: {e}")
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def show_reminder_type_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, plant_id: int):
    """Меню выбора типа напоминания"""
    keyboard = [
        [InlineKeyboardButton("💧 Полив", callback_data=f"rem_type_{plant_id}_полив")],
        [InlineKeyboardButton("🌿 Удобрение", callback_data=f"rem_type_{plant_id}_удобрение")],
        [InlineKeyboardButton("✂️ Обрезка", callback_data=f"rem_type_{plant_id}_обрезка")],
        [InlineKeyboardButton("🔙 Назад", callback_data=f"plant_{plant_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        "Выберите тип напоминания:",
        reply_markup=reply_markup
    )

async def show_times_per_day_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню выбора количества раз в день"""
    keyboard = [
        [InlineKeyboardButton("1 раз", callback_data="times_1")],
        [InlineKeyboardButton("2 раза", callback_data="times_2")],
        [InlineKeyboardButton("3 раза", callback_data="times_3")],
        [InlineKeyboardButton("❌ Отмена", callback_data="reminder_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    rem_type = context.user_data.get("reminder_type", "")
    await update.callback_query.edit_message_text(
        f"Тип: {rem_type}\nСколько раз в день?",
        reply_markup=reply_markup
    )

async def show_time_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню выбора времени"""
    times = []
    for hour in range(6, 23):
        for minute in [0, 30]:
            time_str = f"{hour:02d}:{minute:02d}"
            times.append(time_str)

    keyboard = []
    row = []
    for i, time_str in enumerate(times):
        row.append(InlineKeyboardButton(time_str, callback_data=f"time_{time_str.replace(':', '_')}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="reminder_cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    rem_type = context.user_data.get("reminder_type", "")
    times_per_day = context.user_data.get("reminder_times_per_day", 1)
    await update.callback_query.edit_message_text(
        f"Тип: {rem_type}\nРаз в день: {times_per_day}\nВыберите время:",
        reply_markup=reply_markup
    )

async def show_days_of_week_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню выбора дней недели"""
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    day_numbers = ["0", "1", "2", "3", "4", "5", "6"]
    selected_days = context.user_data.get("reminder_days", [])
    keyboard = []
    row = []
    for i, (day, num) in enumerate(zip(days, day_numbers)):
        prefix = "✅" if num in selected_days else ""
        row.append(InlineKeyboardButton(f"{prefix} {day}", callback_data=f"day_{num}"))
        if len(row) == 4:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("💾 Сохранить", callback_data="reminder_save")])
    keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="reminder_cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    rem_type = context.user_data.get("reminder_type", "")
    times_per_day = context.user_data.get("reminder_times_per_day", 1)
    time_str = context.user_data.get("reminder_time", "")
    selected_text = ", ".join([days[int(d)] for d in selected_days]) if selected_days else "Не выбрано"
    await update.callback_query.edit_message_text(
        f"Тип: {rem_type}\n"
        f"Раз в день: {times_per_day}\n"
        f"Время: {time_str}\n"
        f"Выберите дни недели:\nВыбрано: {selected_text}",
        reply_markup=reply_markup
    )

async def save_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение напоминания"""
    user_id = update.effective_user.id
    plant_id = context.user_data.get("reminder_plant_id")
    rem_type = context.user_data.get("reminder_type")
    times_per_day = context.user_data.get("reminder_times_per_day")
    time_str = context.user_data.get("reminder_time")
    days = context.user_data.get("reminder_days", [])

    if not days:
        await update.callback_query.answer("❌ Выберите хотя бы один день недели!", show_alert=True)
        return

    days_str = ",".join(sorted(days))

    try:
        response = requests.post(
            f"{API_URL}/plants/{plant_id}/reminders",
            json={
                "reminder_type": rem_type,
                "times_per_day": times_per_day,
                "reminder_time": time_str,
                "days_of_week": days_str
            },
            headers={**get_headers(user_id), "Content-Type": "application/json"}
        )
        if response.status_code == 200:
            await update.callback_query.edit_message_text("✅ Напоминание создано!")
            context.user_data.pop("reminder_plant_id", None)
            context.user_data.pop("reminder_type", None)
            context.user_data.pop("reminder_times_per_day", None)
            context.user_data.pop("reminder_time", None)
            context.user_data.pop("reminder_days", None)
            await show_plant_detail(update, context, plant_id)
        elif response.status_code == 401:
            await update.callback_query.edit_message_text("❌ Сессия истекла. Войдите снова.")
            if user_id in user_tokens:
                del user_tokens[user_id]
            await start(update, context)
        elif response.status_code == 404:
            await update.callback_query.edit_message_text("❌ Растение не найдено.")
            await show_plants(update, context)
        else:
            error_msg = response.json().get("detail", "Ошибка при создании напоминания")
            await update.callback_query.edit_message_text(f"❌ {error_msg}")
    except Exception as e:
        logger.error(f"Save reminder error: {e}")
        await update.callback_query.edit_message_text("❌ Ошибка подключения к серверу.")

async def show_plant_entries(update: Update, context: ContextTypes.DEFAULT_TYPE, plant_id: int):
    """Показать записи дневника растения"""
    user_id = update.effective_user.id
    try:
        plant_response = requests.get(
            f"{API_URL}/plants/{plant_id}",
            headers=get_headers(user_id)
        )
        if plant_response.status_code == 404:
            await update.callback_query.edit_message_text("❌ Растение не найдено.")
            await show_plants(update, context)
            return
        elif plant_response.status_code != 200:
            if plant_response.status_code == 401:
                await update.callback_query.edit_message_text("❌ Сессия истекла. Войдите снова.")
                if user_id in user_tokens:
                    del user_tokens[user_id]
                await start(update, context)
            else:
                await update.callback_query.edit_message_text("❌ Ошибка при загрузке растения.")
            return

        plant = plant_response.json()
        entries_response = requests.get(
            f"{API_URL}/plants/{plant_id}/entries",
            headers=get_headers(user_id)
        )
        if entries_response.status_code != 200:
            if entries_response.status_code == 401:
                await update.callback_query.edit_message_text("❌ Сессия истекла. Войдите снова.")
                if user_id in user_tokens:
                    del user_tokens[user_id]
                await start(update, context)
            else:
                await update.callback_query.edit_message_text("❌ Ошибка при загрузке записей.")
            return

        entries = entries_response.json()
        if not entries:
            keyboard = [
                [InlineKeyboardButton("📝 Добавить запись", callback_data=f"entry_{plant_id}")],
                [InlineKeyboardButton("🔙 Назад", callback_data=f"plant_{plant_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                f"🌱 {plant['name']}\n📝 Записей пока нет.",
                reply_markup=reply_markup
            )
            return

        text = f"🌱 {plant['name']}\n📝 Записи дневника:\n"
        for entry in entries[:10]: # Показываем последние 10 записей
            entry_date = datetime.fromisoformat(entry['entry_date'].replace('Z', '+00:00'))
            date_str = entry_date.strftime('%d.%m.%Y %H:%M')
            text += f"📅 {date_str}\n"
            actions = []
            if entry.get('watering'):
                actions.append("💧 Полив")
            if entry.get('fertilizing'):
                actions.append("🌿 Удобрение")
            if entry.get('pruning'):
                actions.append("✂️ Обрезка")
            if entry.get('other_care'):
                actions.append(entry['other_care'])
            if actions:
                text += f"   {', '.join(actions)}\n"
            if entry.get('notes'):
                text += f"   {entry['notes']}\n"
            text += "\n"

        if len(entries) > 10:
            text += f"\n... и еще {len(entries) - 10} записей"

        keyboard = [
            [InlineKeyboardButton("📝 Добавить запись", callback_data=f"entry_{plant_id}")],
            [InlineKeyboardButton("🔙 Назад", callback_data=f"plant_{plant_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Show entries error: {e}")
        await update.callback_query.edit_message_text("❌ Ошибка подключения к серверу.")

async def show_plant_photos(update: Update, context: ContextTypes.DEFAULT_TYPE, plant_id: int):
    """Показать фото растения"""
    user_id = update.effective_user.id
    try:
        plant_response = requests.get(
            f"{API_URL}/plants/{plant_id}",
            headers=get_headers(user_id)
        )
        if plant_response.status_code == 404:
            await update.callback_query.edit_message_text("❌ Растение не найдено.")
            await show_plants(update, context)
            return
        elif plant_response.status_code != 200:
            if plant_response.status_code == 401:
                await update.callback_query.edit_message_text("❌ Сессия истекла. Войдите снова.")
                if user_id in user_tokens:
                    del user_tokens[user_id]
                await start(update, context)
            else:
                await update.callback_query.edit_message_text("❌ Ошибка при загрузке растения.")
            return

        plant = plant_response.json()
        photos_response = requests.get(
            f"{API_URL}/plants/{plant_id}/photos",
            headers=get_headers(user_id)
        )
        if photos_response.status_code != 200:
            if photos_response.status_code == 401:
                await update.callback_query.edit_message_text("❌ Сессия истекла. Войдите снова.")
                if user_id in user_tokens:
                    del user_tokens[user_id]
                await start(update, context)
            else:
                await update.callback_query.edit_message_text("❌ Ошибка при загрузке фото.")
            return

        photos = photos_response.json()
        if not photos:
            keyboard = [
                [InlineKeyboardButton("📷 Добавить фото", callback_data=f"photo_{plant_id}")],
                [InlineKeyboardButton("🔙 Назад", callback_data=f"plant_{plant_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                f"🌱 {plant['name']}\n📷 Фото пока нет.",
                reply_markup=reply_markup
            )
            return

        text = f"🌱 {plant['name']}\n📷 Фото ({len(photos)}):\n"
        for i, photo in enumerate(photos[:5], 1): # Показываем первые 5
            photo_date = datetime.fromisoformat(photo['created_at'].replace('Z', '+00:00'))
            date_str = photo_date.strftime('%d.%m.%Y')
            text += f"{i}. {date_str}\n"
            if photo.get('description'):
                text += f"   {photo['description']}\n"
            text += f"   {API_URL}{photo['photo_path']}\n"

        if len(photos) > 5:
            text += f"... и еще {len(photos) - 5} фото"

        keyboard = [
            [InlineKeyboardButton("📷 Добавить фото", callback_data=f"photo_{plant_id}")],
            [InlineKeyboardButton("🔙 Назад", callback_data=f"plant_{plant_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Show photos error: {e}")
        await update.callback_query.edit_message_text("❌ Ошибка подключения к серверу.")

async def show_plant_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE, plant_id: int):
    """Показать напоминания растения"""
    user_id = update.effective_user.id
    try:
        plant_response = requests.get(
            f"{API_URL}/plants/{plant_id}",
            headers=get_headers(user_id)
        )
        if plant_response.status_code == 404:
            await update.callback_query.edit_message_text("❌ Растение не найдено.")
            await show_plants(update, context)
            return
        elif plant_response.status_code != 200:
            if plant_response.status_code == 401:
                await update.callback_query.edit_message_text("❌ Сессия истекла. Войдите снова.")
                if user_id in user_tokens:
                    del user_tokens[user_id]
                await start(update, context)
            else:
                await update.callback_query.edit_message_text("❌ Ошибка при загрузке растения.")
            return

        plant = plant_response.json()
        reminders_response = requests.get(
            f"{API_URL}/plants/{plant_id}/reminders",
            headers=get_headers(user_id)
        )
        if reminders_response.status_code != 200:
            if reminders_response.status_code == 401:
                await update.callback_query.edit_message_text("❌ Сессия истекла. Войдите снова.")
                if user_id in user_tokens:
                    del user_tokens[user_id]
                await start(update, context)
            else:
                await update.callback_query.edit_message_text("❌ Ошибка при загрузке напоминаний.")
            return

        reminders = reminders_response.json()
        if not reminders:
            keyboard = [
                [InlineKeyboardButton("🔔 Добавить напоминание", callback_data=f"reminder_{plant_id}")],
                [InlineKeyboardButton("🔙 Назад", callback_data=f"plant_{plant_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                f"🌱 {plant['name']}\n🔔 Напоминаний пока нет.",
                reply_markup=reply_markup
            )
            return

        text = f"🌱 {plant['name']}\n🔔 Напоминания:\n"
        for rem in reminders:
            status = "✅" if rem.get('is_active', True) else "❌"
            days_list = rem.get('days_of_week', '').split(',')
            days_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
            days_display = ", ".join([days_names[int(d)] for d in days_list if d.isdigit()])
            text += f"{status} {rem['reminder_type']}\n"
            text += f"   Время: {rem['reminder_time']}\n"
            text += f"   Раз в день: {rem['times_per_day']}\n"
            text += f"   Дни: {days_display}\n"

        keyboard = []
        for rem in reminders:
            keyboard.append([InlineKeyboardButton(
                f"🗑️ Удалить: {rem['reminder_type']}",
                callback_data=f"delete_reminder_{rem['id']}"
            )])
        keyboard.append([InlineKeyboardButton("🔔 Добавить напоминание", callback_data=f"reminder_{plant_id}")])
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=f"plant_{plant_id}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Show reminders error: {e}")
        await update.callback_query.edit_message_text("❌ Ошибка подключения к серверу.")

async def confirm_delete_plant(update: Update, context: ContextTypes.DEFAULT_TYPE, plant_id: int):
    """Подтверждение удаления растения"""
    keyboard = [
        [InlineKeyboardButton("✅ Да, удалить", callback_data=f"confirm_delete_plant_{plant_id}")],
        [InlineKeyboardButton("❌ Отмена", callback_data=f"plant_{plant_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        "⚠️ Вы уверены, что хотите удалить это растение?\nВсе записи, фото и напоминания также будут удалены!",
        reply_markup=reply_markup
    )

async def delete_plant(update: Update, context: ContextTypes.DEFAULT_TYPE, plant_id: int):
    """Удаление растения"""
    user_id = update.effective_user.id
    try:
        response = requests.delete(
            f"{API_URL}/plants/{plant_id}",
            headers=get_headers(user_id)
        )
        if response.status_code == 200:
            await update.callback_query.edit_message_text("✅ Растение удалено!")
            await show_plants(update, context)
        elif response.status_code == 401:
            await update.callback_query.edit_message_text("❌ Сессия истекла. Войдите снова.")
            if user_id in user_tokens:
                del user_tokens[user_id]
            await start(update, context)
        elif response.status_code == 404:
            await update.callback_query.edit_message_text("❌ Растение не найдено.")
            await show_plants(update, context)
        else:
            error_msg = response.json().get("detail", "Ошибка при удалении растения")
            await update.callback_query.edit_message_text(f"❌ {error_msg}")
    except Exception as e:
        logger.error(f"Delete plant error: {e}")
        await update.callback_query.edit_message_text("❌ Ошибка подключения к серверу.")

async def delete_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE, reminder_id: int):
    """Удаление напоминания"""
    user_id = update.effective_user.id
    try:
        # Получаем все растения пользователя для поиска plant_id
        plants_response = requests.get(
            f"{API_URL}/plants",
            headers=get_headers(user_id)
        )

        if plants_response.status_code == 401:
            await update.callback_query.edit_message_text("❌ Сессия истекла. Войдите снова.")
            if user_id in user_tokens:
                del user_tokens[user_id]
            await start(update, context)
            return
        elif plants_response.status_code != 200:
            await update.callback_query.edit_message_text("❌ Ошибка при получении растений.")
            return

        plants = plants_response.json()
        plant_id = None
        # Ищем растение с этим напоминанием
        for plant in plants:
            # Для каждого растения запрашиваем его напоминания
            reminders_response = requests.get(
                f"{API_URL}/plants/{plant['id']}/reminders",
                headers=get_headers(user_id)
            )
            if reminders_response.status_code == 200:
                reminders = reminders_response.json()
                if any(r['id'] == reminder_id for r in reminders):
                    plant_id = plant['id']
                    break # Нашли растение, выходим из цикла

        if not plant_id:
            await update.callback_query.edit_message_text("❌ Напоминание не найдено.")
            return

        # Удаляем напоминание
        delete_response = requests.delete(
            f"{API_URL}/reminders/{reminder_id}",
            headers=get_headers(user_id)
        )

        if delete_response.status_code == 200:
            await update.callback_query.edit_message_text("✅ Напоминание удалено!")
            await show_plant_reminders(update, context, plant_id)
        elif delete_response.status_code == 401:
            await update.callback_query.edit_message_text("❌ Сессия истекла. Войдите снова.")
            if user_id in user_tokens:
                del user_tokens[user_id]
            await start(update, context)
        elif delete_response.status_code == 404:
            await update.callback_query.edit_message_text("❌ Напоминание не найдено.")
            await show_plant_reminders(update, context, plant_id)
        else:
            error_msg = delete_response.json().get("detail", "Ошибка при удалении напоминания")
            await update.callback_query.edit_message_text(f"❌ {error_msg}")

    except Exception as e:
        logger.error(f"Delete reminder error: {e}")
        await update.callback_query.edit_message_text("❌ Ошибка подключения к серверу.")

def main():
    """Запуск бота"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен!")
        return
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("myid", get_my_id))
    application.add_handler(CommandHandler("admin", admin_check_reminders))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Запуск бота
    logger.info("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()