from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
import time
import os

# Настройки
driver_path = r"C:\Users\seryi\OneDrive\Desktop\serv-obya\chromedriver-win32\chromedriver.exe"
site_path = r"C:\Users\seryi\OneDrive\Desktop\serv-obya\index.html"

# Тестовые фото
test_image_tech = r"C:\Users\seryi\OneDrive\Desktop\serv-obya\fototest\test.jpg"
test_image_auto = r"C:\Users\seryi\OneDrive\Desktop\serv-obya\fototest\test1.jpg"
for path in [test_image_tech, test_image_auto]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл не найден: {path}")

# Запуск браузера
service = Service(driver_path)
driver = webdriver.Chrome(service=service)
driver.maximize_window()
print("\n=== Тестирование сайта объявлений ===")

# Тест 1: Загрузка страницы
driver.get("file:///" + site_path)
time.sleep(1)
assert "Сервис объявлений" in driver.page_source
print("✅ Тест 1: страница загружена")

# Тест 2: Добавление "Телефон Samsung" (Техника)
title_input = driver.find_element(By.ID, "title")
desc_input = driver.find_element(By.ID, "description")
category_select = Select(driver.find_element(By.ID, "category"))
photo_input = driver.find_element(By.ID, "photo")
add_button = driver.find_element(By.XPATH, "//button[text()='Добавить']")

title_input.send_keys("Телефон Samsung")
desc_input.send_keys("Почти новый, отличное состояние")
category_select.select_by_visible_text("Техника")
photo_input.send_keys(test_image_tech)
add_button.click()
time.sleep(2)
print("✅ Тест 2: добавлено в 'Техника'")

# Тест 3: Добавление "Honda Civic" (Авто)
title_input.send_keys("Honda Civic")
desc_input.send_keys("Автомобиль 2018 года")
category_select.select_by_visible_text("Авто")
photo_input.send_keys(test_image_auto)
add_button.click()
time.sleep(2)
print("✅ Тест 3: добавлено в 'Авто'")

# Тест 4: Фильтр "Авто"
filter_select = Select(driver.find_element(By.ID, "filter"))
filter_select.select_by_visible_text("Авто")
time.sleep(1)
filtered_ads_auto = driver.find_elements(By.CLASS_NAME, "ad")
assert all("Авто" in ad.text for ad in filtered_ads_auto)
print("✅ Тест 4: фильтр 'Авто' работает")

# Тест 5: Удаление "Honda Civic"
filter_select.select_by_visible_text("Все категории")
time.sleep(1)
all_ads_before_delete = driver.find_elements(By.CLASS_NAME, "ad")
count_before_delete = len(all_ads_before_delete)

delete_button = all_ads_before_delete[-1].find_element(By.CLASS_NAME, "delete-btn")
delete_button.click()
driver.switch_to.alert.accept()
time.sleep(1)

all_ads_after_delete = driver.find_elements(By.CLASS_NAME, "ad")
assert len(all_ads_after_delete) == count_before_delete - 1
print("✅ Тест 5: 'Honda Civic' удалено")

# Завершение
driver.quit()
print("\n🎉 Все тесты пройдены!")
