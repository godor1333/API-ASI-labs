from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# Путь к вашему HTML файлу
HTML_PATH = os.path.abspath("index.html")
HTML_URL = f"file://{HTML_PATH}"

# Настройка драйвера
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

# Папка для скриншотов
screenshot_dir = "screenshots"
if not os.path.exists(screenshot_dir):
    os.makedirs(screenshot_dir)

def take_screenshot(name):
    driver.save_screenshot(f"{screenshot_dir}/{name}.png")

def test_display_books():
    print("\n--- Тест 1: Проверка отображения книг ---")
    driver.get(HTML_URL)
    time.sleep(1)
    books = driver.find_elements(By.CSS_SELECTOR, ".book-item")
    print(f"Найдено книг: {len(books)}")
    expected_count = 5
    if len(books) == expected_count:
        print("✅ Пройден: Все 5 книг отображаются.")
        return True
    else:
        print("❌ Провален: Количество книг не совпадает.")
        return False

def test_search_book():
    print("\n--- Тест 2: Поиск книги ---")
    search_input = driver.find_element(By.ID, "searchInput")
    search_input.clear()
    search_input.send_keys("1984")
    driver.find_element(By.XPATH, "//button[text()='Найти']").click()
    time.sleep(1)
    books = driver.find_elements(By.CSS_SELECTOR, ".book-item")
    titles = [book.find_element(By.CSS_SELECTOR, "strong").text for book in books]
    if "1984" in titles:
        print("✅ Пройден: Книга найдена.")
        return True
    else:
        print("❌ Провален: Книга не найдена.")
        return False

def test_add_book():
    print("\n--- Тест 3: Добавление новой книги ---")
    driver.get(HTML_URL)
    time.sleep(1)
    initial_count = len(driver.find_elements(By.CSS_SELECTOR, ".book-item"))

    driver.find_element(By.ID, "title").send_keys("Новая Книга")
    driver.find_element(By.ID, "author").send_keys("Новый Автор")
    driver.find_element(By.ID, "year").send_keys("2025")
    driver.find_element(By.ID, "genre").send_keys("Фантастика")
    driver.find_element(By.XPATH, "//button[text()='Добавить книгу']").click()
    time.sleep(1)

    final_count = len(driver.find_elements(By.CSS_SELECTOR, ".book-item"))
    if final_count == initial_count + 1:
        print("✅ Пройден: Книга добавлена.")
        return True
    else:
        print("❌ Провален: Книга не добавлена.")
        return False

def test_delete_book():
    print("\n--- Тест 4: Удаление книги ---")
    initial_count = len(driver.find_elements(By.CSS_SELECTOR, ".book-item"))
    if initial_count == 0:
        print("❌ Провален: Нет книг для удаления.")
        return False

    delete_btn = driver.find_elements(By.CSS_SELECTOR, ".book-actions button")[0]
    delete_btn.click()
    time.sleep(1)

    final_count = len(driver.find_elements(By.CSS_SELECTOR, ".book-item"))
    if final_count == initial_count - 1:
        print("✅ Пройден: Книга удалена.")
        return True
    else:
        print("❌ Провален: Книга не удалена.")
        return False

def test_add_book_screenshot():
    print("\n--- Тест 5: Скринкаст добавления книги ---")
    driver.get(HTML_URL)
    time.sleep(1)
    take_screenshot("before_add_book")
    driver.find_element(By.ID, "title").send_keys("Тестовая Книга")
    driver.find_element(By.ID, "author").send_keys("Тестовый Автор")
    driver.find_element(By.ID, "year").send_keys("2020")
    driver.find_element(By.ID, "genre").send_keys("Тест")
    driver.find_element(By.XPATH, "//button[text()='Добавить книгу']").click()
    time.sleep(1)
    take_screenshot("after_add_book")
    print("📸 Скриншоты сохранены: before_add_book.png, after_add_book.png")
    return True

def test_search_screenshot():
    print("\n--- Тест 6: Скринкаст поиска книги ---")
    driver.get(HTML_URL)
    time.sleep(1)
    take_screenshot("before_search")
    driver.find_element(By.ID, "searchInput").send_keys("Мастер")
    driver.find_element(By.XPATH, "//button[text()='Найти']").click()
    time.sleep(1)
    take_screenshot("after_search")
    print("📸 Скриншоты сохранены: before_search.png, after_search.png")
    return True

# Запуск тестов
if __name__ == "__main__":
    results = {}
    tests = [
        ("test_display_books", test_display_books),
        ("test_search_book", test_search_book),
        ("test_add_book", test_add_book),
        ("test_delete_book", test_delete_book),
        ("test_add_book_screenshot", test_add_book_screenshot),
        ("test_search_screenshot", test_search_screenshot),
    ]

    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = "✅ Пройден" if result else "❌ Провален"
        except Exception as e:
            print(f"❌ Ошибка в {test_name}: {e}")
            results[test_name] = "❌ Ошибка"

    print("\n" + "="*50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("="*50)
    for name, result in results.items():
        print(f"{name:<30} | {result}")
    print("="*50)

    # Закрытие браузера
    driver.quit()
