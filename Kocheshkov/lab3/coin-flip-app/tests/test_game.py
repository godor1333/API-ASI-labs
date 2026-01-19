# tests/test_game.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.config import create_driver, login, BASE_URL

def test_coin_flip_result_shown():
    """
    Залогиниться, открыть /game, поставить сумму, выбрать "Орел" и нажать Поставить.
    Ожидаем появления блока результата .result
    """
    driver = create_driver()
    try:
        assert login(driver, username="admin", password="1234"), "Не удалось залогиниться."

        driver.get(f"{BASE_URL}/game")
        wait = WebDriverWait(driver, 15)

        # Ждём поле суммы (input type=number)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="number"]')))

        amount_input = driver.find_element(By.CSS_SELECTOR, 'input[type="number"]')
        amount_input.clear()
        amount_input.send_keys("10")

        # Нажимаем кнопку выбора "Орел" (ищем по тексту)
        btn_orol = driver.find_element(By.XPATH, '//button[contains(text(),"Орел")]')
        btn_orol.click()

        # Нажать кнопку поставить (класс .flip-button)
        flip_btn = driver.find_element(By.CSS_SELECTOR, '.flip-button')
        flip_btn.click()

        # Ожидаем появления результата
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'result')))
        assert True
    finally:
        driver.quit()
