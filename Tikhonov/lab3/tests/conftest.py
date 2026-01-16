"""
Конфигурация для тестов Selenium
"""
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import os
import time


@pytest.fixture(scope="function")
def driver():
    """Создание драйвера для каждого теста"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Отключаем уведомления
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Для headless режима (раскомментировать при необходимости)
    # chrome_options.add_argument("--headless")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    
    yield driver
    
    driver.quit()


@pytest.fixture(scope="function")
def base_url():
    """Базовый URL приложения"""
    return os.getenv("BASE_URL", "http://localhost")


@pytest.fixture(scope="function")
def wait(driver):
    """WebDriverWait для ожидания элементов"""
    return WebDriverWait(driver, 15)


@pytest.fixture(scope="function")
def cleanup_storage(driver, base_url):
    """Очистка localStorage перед каждым тестом"""
    driver.get(base_url)
    driver.execute_script("localStorage.clear();")
    yield
    # Очистка после теста
    try:
        driver.execute_script("localStorage.clear();")
    except:
        pass

