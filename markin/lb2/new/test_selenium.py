# test_selenium.py
import os
import unittest
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# === Настройка логирования ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("auction_test.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()


class TestArtAuctionSelenium(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Запускаем браузер ВИДИМЫЙ (без headless)"""
        logger.info("=== Запуск браузера Chrome ===")
        options = webdriver.ChromeOptions()
        # УБРАЛИ --headless → теперь всё видно!
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # Отключаем логи DevTools в консоли
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)

        service = Service(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service, options=options)

        # Открываем HTML-файл
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cls.driver.get(f"file://{current_dir}/auction.html")
        logger.info(f"Открыта страница: file://{current_dir}/auction.html")

    @classmethod
    def tearDownClass(cls):
        logger.info("=== Закрытие браузера ===")
        cls.driver.quit()

    def setUp(self):
        logger.info("--- Начало нового теста ---")
        # Очищаем данные
        self.driver.execute_script("localStorage.clear();")
        self.driver.refresh()
        logger.info("localStorage очищен, страница обновлена")

    def test_multi_user_bidding_simulation(self):
        """
        🎯 Интересный тест: имитация ставок от двух "пользователей"
        на одну картину — побеждает тот, кто делает последнюю ставку.
        """
        logger.info("🚀 Тест: имитация ставок от нескольких пользователей")

        # Пользователь 1 добавляет картину
        self.driver.find_element(By.ID, "title").send_keys("Космос")
        self.driver.find_element(By.ID, "author").send_keys("А. Васнецов")
        self.driver.find_element(By.ID, "price").send_keys("100")
        self.driver.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
        logger.info("Пользователь 1 добавил картину 'Космос', стартовая цена: 100 ₽")

        # Пользователь 2 делает ставку → 110
        bid_btn = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "bid-btn"))
        )
        bid_btn.click()
        logger.info("Пользователь 2 сделал ставку → цена: 110 ₽")

        # Пользователь 1 делает ещё ставку → 121
        bid_btn = self.driver.find_element(By.CLASS_NAME, "bid-btn")
        bid_btn.click()
        logger.info("Пользователь 1 сделал ставку → цена: 121 ₽")

        # Пользователь 2 делает ещё ставку → 133
        bid_btn = self.driver.find_element(By.CLASS_NAME, "bid-btn")
        bid_btn.click()
        logger.info("Пользователь 2 сделал ставку → цена: 133 ₽")

        # Завершаем аукцион
        self.driver.find_element(By.ID, "end-auction").click()
        winner_text = self.driver.find_element(By.ID, "winner").text
        logger.info(f"Аукцион завершён. Победитель: {winner_text}")

        # Проверка: цена должна быть 133
        self.assertIn("133", winner_text)
        self.assertIn("Космос", winner_text)
        self.assertIn("А. Васнецов", winner_text)
        logger.info("✅ Тест пройден: победитель определён корректно")

    def test_add_and_bid_basic(self):
        """Базовый тест с логированием"""
        logger.info("Тест: добавление и одна ставка")
        d = self.driver
        d.find_element(By.ID, "title").send_keys("Тест")
        d.find_element(By.ID, "author").send_keys("Автор")
        d.find_element(By.ID, "price").send_keys("200")
        d.find_element(By.CSS_SELECTOR, "form button[type='submit']").click()
        logger.info("Картина добавлена")

        d.find_element(By.CLASS_NAME, "bid-btn").click()
        logger.info("Сделана ставка (200 → 220)")

        art_text = d.find_element(By.CLASS_NAME, "art-item").text
        self.assertIn("220", art_text)
        logger.info("✅ Цена обновлена корректно")

    def test_empty_auction(self):
        logger.info("Тест: пустой аукцион")
        self.driver.find_element(By.ID, "end-auction").click()
        text = self.driver.find_element(By.ID, "winner").text
        self.assertEqual(text, "Нет картин для торгов.")
        logger.info("✅ Пустой аукцион обработан верно")


if __name__ == "__main__":
    logger.info("🏁 ЗАПУСК ТЕСТОВ АУКЦИОНА")
    unittest.main(verbosity=2)