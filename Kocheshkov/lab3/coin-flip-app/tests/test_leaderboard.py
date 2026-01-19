# tests/test_leaderboard.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.config import create_driver, login, BASE_URL

def test_leaderboard_shown():
    """
    Логинимся, открываем /leaderboard и проверяем заголовок 'Топ игроков'
    """
    driver = create_driver()
    try:
        assert login(driver, username="admin", password="1234"), "Не удалось залогиниться."

        driver.get(f"{BASE_URL}/leaderboard")
        wait = WebDriverWait(driver, 15)

        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        title = driver.find_element(By.TAG_NAME, "h1").text
        assert "Топ игроков" in title or "Таблица лидеров" in title
    finally:
        driver.quit()
