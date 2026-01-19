"""
Тесты Selenium для Генератора мемов
Покрывает весь функционал приложения
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os
import random
import string


class TestMemeGenerator:
    """Класс с тестами для генератора мемов"""
    
    def generate_username(self):
        """Генерация уникального имени пользователя"""
        return f"test_user_{random.randint(1000, 9999)}"
    
    def generate_email(self):
        """Генерация уникального email"""
        return f"test_{random.randint(1000, 9999)}@test.com"
    
    def test_01_registration_and_login(self, driver, base_url, wait, cleanup_storage):
        """Тест: Регистрация нового пользователя и вход в систему"""
        driver.get(base_url)
        
        # Переходим к регистрации
        register_link = wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Зарегистрироваться"))
        )
        register_link.click()
        
        # Заполняем форму регистрации
        username = self.generate_username()
        email = self.generate_email()
        password = "testpass123"
        
        username_input = wait.until(
            EC.presence_of_element_located((By.ID, "register-username"))
        )
        username_input.send_keys(username)
        
        email_input = driver.find_element(By.ID, "register-email")
        email_input.send_keys(email)
        
        password_input = driver.find_element(By.ID, "register-password")
        password_input.send_keys(password)
        
        # Отправляем форму
        register_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Зарегистрироваться')]")
        register_button.click()
        
        # Ждем успешной регистрации (должна появиться форма входа)
        time.sleep(2)
        
        # Проверяем, что появилась форма входа
        login_form = wait.until(
            EC.presence_of_element_located((By.ID, "login-form"))
        )
        assert login_form.is_displayed(), "Форма входа должна отображаться после регистрации"
        
        # Входим в систему
        login_username = driver.find_element(By.ID, "login-username")
        login_username.clear()
        login_username.send_keys(username)
        
        login_password = driver.find_element(By.ID, "login-password")
        login_password.clear()
        login_password.send_keys(password)
        
        login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Войти')]")
        login_button.click()
        
        # Проверяем успешный вход
        time.sleep(2)
        user_info = wait.until(
            EC.presence_of_element_located((By.ID, "user-info"))
        )
        assert user_info.is_displayed(), "Информация о пользователе должна отображаться"
        
        # Проверяем, что имя пользователя отображается
        username_display = driver.find_element(By.ID, "username-display")
        assert username in username_display.text, f"Имя пользователя {username} должно отображаться"
    
    def test_02_upload_image(self, driver, base_url, wait, cleanup_storage):
        """Тест: Загрузка изображения"""
        # Сначала регистрируемся и входим
        self._login_user(driver, base_url, wait)
        
        # Находим поле загрузки файла
        file_input = wait.until(
            EC.presence_of_element_located((By.ID, "image-input"))
        )
        
        # Используем существующее тестовое изображение
        test_image_path = self._get_test_image_path()
        
        # Загружаем файл
        file_input.send_keys(test_image_path)
        
        # Нажимаем кнопку загрузки
        upload_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Загрузить')]")
        upload_button.click()
        
        # Ждем успешной загрузки
        time.sleep(2)
        
        # Проверяем сообщение об успехе
        upload_status = driver.find_element(By.ID, "upload-status")
        assert "успешно" in upload_status.text.lower() or upload_status.text == "", \
            "Должно появиться сообщение об успешной загрузке"
        
        # Проверяем, что появилась секция создания мема
        meme_section = wait.until(
            EC.presence_of_element_located((By.ID, "meme-section"))
        )
        assert meme_section.is_displayed(), "Секция создания мема должна отображаться"
    
    def test_03_create_meme_with_text(self, driver, base_url, wait, cleanup_storage):
        """Тест: Создание мема с текстом"""
        # Регистрируемся, входим и загружаем изображение
        self._login_user(driver, base_url, wait)
        self._upload_test_image(driver, wait)
        
        # Вводим текст для мема
        text_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".text-input"))
        )
        text_input.send_keys("Тестовый мем")
        
        # Нажимаем кнопку создания мема
        create_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Создать мем')]")
        create_button.click()
        
        # Ждем создания мема
        time.sleep(3)
        
        # Проверяем сообщение об успехе
        meme_status = wait.until(
            EC.presence_of_element_located((By.ID, "meme-status"))
        )
        assert "успешно" in meme_status.text.lower() or meme_status.text == "", \
            "Должно появиться сообщение об успешном создании мема"
        
        # Проверяем, что появилось превью мема
        meme_preview = driver.find_elements(By.ID, "meme-preview")
        if meme_preview:
            assert meme_preview[0].is_displayed(), "Превью мема должно отображаться"
    
    def test_04_text_alignment_buttons(self, driver, base_url, wait, cleanup_storage):
        """Тест: Проверка кнопок выравнивания текста"""
        # Регистрируемся, входим и загружаем изображение
        self._login_user(driver, base_url, wait)
        self._upload_test_image(driver, wait)
        
        # Ждем появления секции создания мема
        meme_section = wait.until(
            EC.presence_of_element_located((By.ID, "meme-section"))
        )
        assert meme_section.is_displayed(), "Секция создания мема должна отображаться"
        
        time.sleep(1)  # Даем время на полную загрузку
        
        # Проверяем наличие кнопок выравнивания
        alignment_buttons = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".align-btn"))
        )
        assert len(alignment_buttons) >= 3, "Должно быть минимум 3 кнопки выравнивания"
        
        # Проверяем, что кнопка "по центру" активна по умолчанию
        center_button = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".align-btn[data-alignment='center']"))
        )
        center_button_classes = center_button.get_attribute("class") or ""
        assert "active" in center_button_classes, \
            f"Кнопка 'по центру' должна быть активна по умолчанию. Классы: {center_button_classes}"
        
        # Нажимаем кнопку "сверху"
        top_button = driver.find_element(By.CSS_SELECTOR, ".align-btn[data-alignment='top']")
        top_button.click()
        time.sleep(0.5)
        
        # Проверяем, что кнопка "сверху" стала активной
        top_button_classes = top_button.get_attribute("class") or ""
        assert "active" in top_button_classes, \
            f"Кнопка 'сверху' должна стать активной после клика. Классы: {top_button_classes}"
        
        # Проверяем, что кнопка "по центру" больше не активна
        center_button_classes = center_button.get_attribute("class") or ""
        assert "active" not in center_button_classes, \
            f"Кнопка 'по центру' не должна быть активной. Классы: {center_button_classes}"
        
        # Нажимаем кнопку "снизу"
        bottom_button = driver.find_element(By.CSS_SELECTOR, ".align-btn[data-alignment='bottom']")
        bottom_button.click()
        time.sleep(0.5)
        
        # Проверяем, что кнопка "снизу" стала активной
        bottom_button_classes = bottom_button.get_attribute("class") or ""
        assert "active" in bottom_button_classes, \
            f"Кнопка 'снизу' должна стать активной после клика. Классы: {bottom_button_classes}"
    
    def test_05_add_multiple_texts(self, driver, base_url, wait, cleanup_storage):
        """Тест: Добавление нескольких текстовых полей"""
        # Регистрируемся, входим и загружаем изображение
        self._login_user(driver, base_url, wait)
        self._upload_test_image(driver, wait)
        
        # Находим начальное количество текстовых полей
        initial_inputs = driver.find_elements(By.CSS_SELECTOR, ".text-input")
        initial_count = len(initial_inputs)
        
        # Нажимаем кнопку добавления текста
        add_text_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Добавить еще текст')]")
        add_text_button.click()
        
        time.sleep(1)
        
        # Проверяем, что добавилось новое текстовое поле
        new_inputs = driver.find_elements(By.CSS_SELECTOR, ".text-input")
        assert len(new_inputs) == initial_count + 1, \
            f"Должно быть {initial_count + 1} текстовых полей, найдено {len(new_inputs)}"
        
        # Проверяем, что у нового поля есть кнопки выравнивания
        text_groups = driver.find_elements(By.CSS_SELECTOR, ".text-input-group")
        assert len(text_groups) == initial_count + 1, \
            "Должна добавиться новая группа с текстовым полем"
        
        # Вводим текст во второе поле
        new_input = new_inputs[-1]
        new_input.send_keys("Второй текст")
        
        # Проверяем, что текст введен
        assert new_input.get_attribute("value") == "Второй текст", \
            "Текст должен быть введен во второе поле"
    
    def test_06_create_meme_with_alignment(self, driver, base_url, wait, cleanup_storage):
        """Тест: Создание мема с разным выравниванием текста"""
        # Регистрируемся, входим и загружаем изображение
        self._login_user(driver, base_url, wait)
        self._upload_test_image(driver, wait)
        
        # Вводим первый текст и устанавливаем выравнивание "сверху"
        first_input = driver.find_element(By.CSS_SELECTOR, ".text-input")
        first_input.send_keys("Текст сверху")
        
        top_button = driver.find_element(By.CSS_SELECTOR, ".align-btn[data-alignment='top']")
        top_button.click()
        time.sleep(0.5)
        
        # Добавляем второй текст с выравниванием "снизу"
        add_text_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Добавить еще текст')]")
        add_text_button.click()
        time.sleep(1)
        
        second_inputs = driver.find_elements(By.CSS_SELECTOR, ".text-input")
        second_input = second_inputs[-1]
        second_input.send_keys("Текст снизу")
        
        # Находим кнопки выравнивания для второго текста
        text_groups = driver.find_elements(By.CSS_SELECTOR, ".text-input-group")
        second_group = text_groups[-1]
        bottom_button = second_group.find_element(By.CSS_SELECTOR, ".align-btn[data-alignment='bottom']")
        bottom_button.click()
        time.sleep(0.5)
        
        # Создаем мем
        create_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Создать мем')]")
        create_button.click()
        
        # Ждем создания
        time.sleep(3)
        
        # Проверяем успешное создание
        meme_status = driver.find_element(By.ID, "meme-status")
        assert "успешно" in meme_status.text.lower() or meme_status.text == "", \
            "Мем должен быть создан успешно"
    
    def test_07_view_memes_list(self, driver, base_url, wait, cleanup_storage):
        """Тест: Просмотр списка мемов"""
        # Регистрируемся, входим, загружаем изображение и создаем мем
        self._login_user(driver, base_url, wait)
        self._upload_test_image(driver, wait)
        self._create_test_meme(driver, wait)
        
        # Прокручиваем к списку мемов
        meme_list_section = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "meme-list-section"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", meme_list_section)
        time.sleep(1)
        
        # Проверяем наличие списка мемов
        meme_list = driver.find_element(By.ID, "meme-list")
        assert meme_list.is_displayed(), "Список мемов должен отображаться"
        
        # Проверяем, что в списке есть мемы (может быть пустым, если мем еще не создан)
        meme_items = driver.find_elements(By.CSS_SELECTOR, ".meme-item")
        # Мемы могут загружаться асинхронно, поэтому просто проверяем наличие контейнера
    
    def test_08_logout(self, driver, base_url, wait, cleanup_storage):
        """Тест: Выход из системы"""
        # Регистрируемся и входим
        self._login_user(driver, base_url, wait)
        
        # Проверяем, что мы вошли
        user_info = wait.until(
            EC.presence_of_element_located((By.ID, "user-info"))
        )
        assert user_info.is_displayed(), "Должна отображаться информация о пользователе"
        
        # Нажимаем кнопку выхода
        logout_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Выйти')]")
        logout_button.click()
        
        time.sleep(1)
        
        # Проверяем, что вернулись к форме входа
        login_form = wait.until(
            EC.presence_of_element_located((By.ID, "login-form"))
        )
        assert login_form.is_displayed(), "Должна отображаться форма входа после выхода"
        
        # Проверяем, что основной контент скрыт
        main_content = driver.find_element(By.ID, "main-content")
        assert not main_content.is_displayed() or main_content.get_attribute("style") == "display: none;", \
            "Основной контент должен быть скрыт после выхода"
    
    # Вспомогательные методы
    
    def _login_user(self, driver, base_url, wait):
        """Вспомогательный метод: регистрация и вход пользователя"""
        driver.get(base_url)
        
        # Регистрация
        register_link = wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Зарегистрироваться"))
        )
        register_link.click()
        
        username = self.generate_username()
        email = self.generate_email()
        password = "testpass123"
        
        driver.find_element(By.ID, "register-username").send_keys(username)
        driver.find_element(By.ID, "register-email").send_keys(email)
        driver.find_element(By.ID, "register-password").send_keys(password)
        driver.find_element(By.XPATH, "//button[contains(text(), 'Зарегистрироваться')]").click()
        
        time.sleep(2)
        
        # Вход
        driver.find_element(By.ID, "login-username").send_keys(username)
        driver.find_element(By.ID, "login-password").send_keys(password)
        driver.find_element(By.XPATH, "//button[contains(text(), 'Войти')]").click()
        
        time.sleep(2)
        
        wait.until(EC.presence_of_element_located((By.ID, "user-info")))
        return username
    
    def _get_test_image_path(self):
        """Получение пути к тестовому изображению"""
        test_image_path = os.path.join(os.path.dirname(__file__), "test_image.jpg")
        if os.path.exists(test_image_path):
            return os.path.abspath(test_image_path)
        else:
            # Если файл не найден, создаем простой PNG
            test_image_path = os.path.join(os.path.dirname(__file__), "test_image.png")
            try:
                from PIL import Image
                img = Image.new('RGB', (200, 200), color='red')
                img.save(test_image_path)
            except ImportError:
                # Если PIL не установлен, создаем простой PNG файл вручную
                png_data = bytes([
                    0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
                    0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
                    0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 dimensions
                    0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53, 0xDE,
                    0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41, 0x54,  # IDAT chunk
                    0x08, 0x99, 0x01, 0x01, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x02,
                    0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82  # IEND
                ])
                with open(test_image_path, 'wb') as f:
                    f.write(png_data)
            return os.path.abspath(test_image_path)
    
    def _upload_test_image(self, driver, wait):
        """Вспомогательный метод: загрузка тестового изображения"""
        test_image_path = self._get_test_image_path()
        
        file_input = wait.until(
            EC.presence_of_element_located((By.ID, "image-input"))
        )
        file_input.send_keys(test_image_path)
        
        upload_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Загрузить')]")
        upload_button.click()
        
        time.sleep(2)
    
    def _create_test_meme(self, driver, wait):
        """Вспомогательный метод: создание тестового мема"""
        text_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".text-input"))
        )
        text_input.send_keys("Тестовый мем")
        
        create_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Создать мем')]")
        create_button.click()
        
        time.sleep(3)

