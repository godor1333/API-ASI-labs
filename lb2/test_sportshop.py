import os
import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# === ЛОГИРОВАНИЕ ===
def log_step(message):
    print(f"[{time.strftime('%H:%M:%S')}] 📌 {message}")

# === ПУТЬ К САЙТУ ===
HTML_FILE = os.path.abspath("index.html")
URL = f"file://{HTML_FILE}"

def test_sportshop():
    driver = None
    try:
        log_step("Начало теста")

        # === 1. Настройка драйвера ===
        log_step("Создание ChromeOptions...")
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        # options.add_argument("--headless=new")  # раскомментируйте, если не хотите видеть браузер

        log_step("Установка ChromeDriver через WebDriver Manager...")
        service = Service(ChromeDriverManager().install())

        log_step("Запуск веб-драйвера...")
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 15)

        # === 2. Открытие главной страницы ===
        log_step(f"Переход на URL: {URL}")
        driver.get(URL)

        log_step("Проверка наличия приветствия 'Добро пожаловать'...")
        assert "Добро пожаловать" in driver.page_source, "Текст 'Добро пожаловать' не найден"
        log_step("✅ Главная страница загружена")

        # === 3. Переключение темы ===
        log_step("Поиск кнопки переключения темы...")
        theme_btn = wait.until(EC.element_to_be_clickable((By.ID, "theme-toggle")))
        theme_btn.click()
        time.sleep(0.5)
        log_step("✅ Тема переключена")

        # === 4. Переход в каталог ===
        log_step("Поиск кнопки 'Перейти в каталог'...")
        go_btn = wait.until(EC.element_to_be_clickable((By.ID, "go-to-catalog")))
        go_btn.click()
        log_step("✅ Переход в каталог выполнен")

        # === 5. Ожидание товаров ===
        log_step("Ожидание появления карточек товаров...")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "product-card")))
        log_step("✅ Товары отображаются")

        # === 6. Проверка пустой корзины ===
        log_step("Открытие корзины (должна быть пустой)...")
        cart_icon = driver.find_element(By.ID, "cart-icon")
        cart_icon.click()
        time.sleep(0.5)

        checkout_btn = driver.find_element(By.ID, "checkout-btn")
        assert checkout_btn.get_attribute("disabled") is not None, "Кнопка должна быть неактивна"
        log_step("✅ Нельзя оформить пустую корзину")

        close_cart = driver.find_element(By.ID, "close-cart")
        close_cart.click()
        time.sleep(0.5)

        # === 7. Добавление товара ===
        log_step("Добавление первого товара в корзину...")
        add_to_cart_btn = driver.find_element(By.XPATH, "//button[text()='В корзину']")
        add_to_cart_btn.click()
        time.sleep(0.7)
        log_step("✅ Товар добавлен")

        # === 8. Проверка непустой корзины ===
        log_step("Открытие корзины (теперь с товаром)...")
        cart_icon.click()
        time.sleep(0.5)

        checkout_btn = driver.find_element(By.ID, "checkout-btn")
        assert checkout_btn.get_attribute("disabled") is None, "Кнопка должна быть активна"
        log_step("✅ Кнопка оформления активна")

        # === 9. Оформление заказа ===
        log_step("Нажатие 'Оформить заказ'...")
        checkout_btn.click()
        time.sleep(1)

        log_step("Ожидание alert...")
        alert = driver.switch_to.alert
        alert_text = alert.text
        log_step(f"Получен alert: '{alert_text}'")
        assert "Заказ оформлен" in alert_text
        alert.accept()
        log_step("✅ Заказ подтверждён")

        # === 10. Проверка очистки корзины ===
        log_step("Проверка, что корзина пуста после заказа...")
        cart_icon.click()
        time.sleep(0.5)
        cart_count = driver.find_element(By.ID, "cart-count").text
        assert cart_count == "0", f"Ожидалось '0', получено '{cart_count}'"
        log_step("✅ Корзина очищена")

        log_step("🎉 Тест успешно завершён!")

    except Exception as e:
        log_step(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
        log_step("Трассировка стека:")
        traceback.print_exc()
        raise
    finally:
        if driver:
            log_step("Закрытие браузера...")
            driver.quit()
        else:
            log_step("⚠️ Драйвер не был создан")

if __name__ == "__main__":
    log_step("Запуск теста SportShop")
    test_sportshop()
    log_step("Тест завершён")