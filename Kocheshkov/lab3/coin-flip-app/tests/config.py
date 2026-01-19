# tests/config.py
"""
Selenium config & helpers for tests.
- BASE_URL: адрес работающего фронтенда (по-умолчанию http://localhost:3002)
- create_driver(): создаёт Chrome WebDriver (webdriver-manager)
- login(driver, username, password): вспомогательная функция для быстрого логина
"""

import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Если фронтенд слушает другой порт/хост — поменяй здесь
BASE_URL = "http://localhost:3002"

def _resolve_chromedriver_path(candidate_path: str) -> str:
    """Устойчиво находит chromedriver.exe рядом с результатом ChromeDriverManager().install()."""
    if os.path.isdir(candidate_path):
        for root, _, files in os.walk(candidate_path):
            for f in files:
                if f.lower() == "chromedriver.exe":
                    return os.path.join(root, f)

    if os.path.isfile(candidate_path):
        name = os.path.basename(candidate_path).lower()
        if name.endswith(".exe"):
            return candidate_path
        parent = os.path.dirname(candidate_path)
        alt = os.path.join(parent, "chromedriver.exe")
        if os.path.isfile(alt):
            return alt
        # искать любые chromedriver*.exe
        try:
            for f in os.listdir(parent):
                if f.lower().startswith("chromedriver") and f.lower().endswith(".exe"):
                    return os.path.join(parent, f)
        except Exception:
            pass

    # предположение
    try:
        guessed = os.path.join(os.path.dirname(candidate_path), "chromedriver.exe")
        if os.path.isfile(guessed):
            return guessed
    except Exception:
        pass

    raise FileNotFoundError(
        f"Не удалось найти chromedriver.exe рядом с: {candidate_path}. "
        "Попробуй установить chromedriver вручную или проверь webdriver-manager."
    )

def create_driver(headless: bool = False):
    """Создаёт Chrome WebDriver через webdriver-manager."""
    options = Options()
    if headless:
        # new headless mode
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    else:
        options.add_argument("--start-maximized")

    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    candidate = ChromeDriverManager().install()
    driver_path = _resolve_chromedriver_path(candidate)

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def login(driver, username: str = "admin", password: str = "1234", wait_seconds: int = 15):
    """
    Утилита — открыть страницу логина и выполнить вход.
    Возвращает True если успешен (URL содержит /game).
    """
    driver.get(f"{BASE_URL}/login")
    wait = WebDriverWait(driver, wait_seconds)

    # Ждём форму логина (ожидаем два поля)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))

    # Поля на фронтенде: placeholders "Имя пользователя" и "Пароль"
    username_input = driver.find_element(By.XPATH, '//input[@placeholder="Имя пользователя"]')
    password_input = driver.find_element(By.XPATH, '//input[@placeholder="Пароль"]')

    username_input.clear()
    username_input.send_keys(username)
    password_input.clear()
    password_input.send_keys(password + Keys.ENTER)

    # Дождёмся редиректа на /game или навигационного элемента
    try:
        wait.until(EC.url_contains("/game"))
        return True
    except Exception:
        # как запасной вариант — ждать nav
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "nav")))
            return True
        except Exception:
            return False
