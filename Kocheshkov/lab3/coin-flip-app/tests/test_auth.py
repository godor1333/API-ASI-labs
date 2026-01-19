# tests/test_auth.py
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.config import create_driver, BASE_URL, login

def test_login_redirects_to_game():
    """
    Тест логина: открывает /login, логинится (admin / 1234), ожидает перехода на /game.
    """
    driver = create_driver()
    try:
        ok = login(driver, username="admin", password="1234")
        assert ok, "Не удалось залогиниться — проверь backend и учетные данные (admin/1234)."
        # Доп. проверка: видим баланс или элемент игры
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="number"]')))
    finally:
        driver.quit()
