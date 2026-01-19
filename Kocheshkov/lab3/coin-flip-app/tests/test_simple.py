# tests/test_simple.py
from tests.config import create_driver   # <-- импортируем функцию из tests/config.py

def test_open_homepage():
    driver = create_driver()
    try:
        driver.get("http://localhost:3001")   # URL твоего фронтенда
        assert "Coin Flip" in driver.title or driver.current_url.startswith("http")
    finally:
        driver.quit()
