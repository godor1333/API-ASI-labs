import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
import platform


@pytest.fixture(scope="session")
def browser():
    """Фикстура для создания браузера Яндекс"""
    
    # Определяем путь к Яндекс.Браузеру в зависимости от ОС
    system = platform.system()
    
    if system == "Windows":
        # Пути для Windows
        yandex_paths = [
            r"C:\Users\%USERNAME%\AppData\Local\Yandex\YandexBrowser\Application\browser.exe",
            r"C:\Program Files (x86)\Yandex\YandexBrowser\Application\browser.exe"
        ]
    elif system == "Linux":
        # Пути для Linux
        yandex_paths = [
            "/usr/bin/yandex-browser",
            "/usr/bin/yandex_browser",
            "/snap/bin/yandex-browser"
        ]
    elif system == "Darwin":  # macOS
        yandex_paths = [
            "/Applications/Yandex.app/Contents/MacOS/Yandex"
        ]
    else:
        yandex_paths = []
    
    # Находим существующий путь к Яндекс.Браузеру
    yandex_executable_path = None
    for path in yandex_paths:
        expanded_path = os.path.expandvars(path) if "%" in path else path
        if os.path.exists(expanded_path):
            yandex_executable_path = expanded_path
            break
    
    if not yandex_executable_path:
        # Если Яндекс.Браузер не найден, используем обычный Chrome
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        print("⚠️  Яндекс.Браузер не найден, используется Chrome")
    else:
        # Настройки для Яндекс.Браузера
        chrome_options = Options()
        chrome_options.binary_location = yandex_executable_path
        
        # Общие настройки
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Раскомментируйте для запуска без GUI
        # chrome_options.add_argument("--headless")
        
        # Используем ChromeDriver для Яндекс.Браузера
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Скрываем автоматизацию
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Используется Яндекс.Браузер")
    
    # Настройка неявных ожиданий
    driver.implicitly_wait(15)
    
    yield driver
    
    # Закрытие браузера после тестов
    driver.quit()


@pytest.fixture
def base_url():
    """Базовый URL приложения"""
    return "http://localhost:3001"


@pytest.fixture
def api_url():
    """URL бэкенда API"""
    return "http://localhost:3000"


@pytest.fixture(autouse=True)
def setup_teardown(browser, base_url):
    """Настройка перед каждым тестом и очистка после"""
    # Сохраняем исходный размер окна
    original_size = browser.get_window_size()
    
    # Устанавливаем оптимальный размер для тестов
    browser.set_window_size(1920, 1080)
    
    yield
    
    # Восстанавливаем исходный размер
    browser.set_window_size(original_size['width'], original_size['height'])
    
    # Очищаем cookies между тестами
    browser.delete_all_cookies()