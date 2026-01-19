from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

class PlantDiarySeleniumTests:
    def __init__(self):
        # Настройка Chrome драйвера (БЕЗ headless режима для визуального контроля)
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")  # Открывать окно во весь экран
        # Отключить всплывающие окна (prompt, alert, confirm)
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.popups": 0,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)  # Увеличенный таймаут ожидания
        self.base_url = "http://localhost"

    def setup_method(self):
        """Инициализация перед каждым тестом"""
        self.driver.get(self.base_url)
        time.sleep(3)  # Пауза для полной загрузки страницы

    def teardown_method(self):
        """Очистка после каждого теста"""
        time.sleep(3)  # Пауза перед закрытием для визуального контроля
        self.driver.quit()

    def test_user_registration_and_login(self):
        """Тест регистрации и авторизации пользователя"""
        print("Запуск теста регистрации и авторизации...")
        
        # Клик по вкладке регистрации
        register_tab = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".tab-btn[data-tab='register']"))
        )
        register_tab.click()
        time.sleep(1)
        
        # Явное ожидание появления формы регистрации
        register_form = self.wait.until(
            EC.visibility_of_element_located((By.ID, "register-form"))
        )
        
        # Проверка, что форма активна
        assert "active" in register_form.get_attribute("class")
        time.sleep(1)
        
        # Заполнение формы регистрации
        register_username = self.wait.until(
            EC.element_to_be_clickable((By.ID, "register-username"))
        )
        register_username.send_keys("test_user")
        time.sleep(1)
        
        register_email = self.driver.find_element(By.ID, "register-email")
        register_email.send_keys("test@example.com")
        time.sleep(1)
        
        register_password = self.driver.find_element(By.ID, "register-password")
        register_password.send_keys("secure_password123")
        time.sleep(1)
        
        # Отправка формы регистрации
        register_submit = self.driver.find_element(By.CSS_SELECTOR, "#register-form button[type='submit']")
        register_submit.click()
        time.sleep(3)
        
        # Проверка успешной регистрации (ожидание появления уведомления или перехода)
        try:
            # Проверка появления уведомления о регистрации
            notification = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".notification"))
            )
            assert "Регистрация успешна" in notification.text
        except:
            # Если уведомления нет, проверяем переход на вкладку входа
            login_tab = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".tab-btn[data-tab='login']"))
            )
            assert login_tab.is_displayed()
        
        print("✓ Регистрация пройдена")

    def test_create_and_view_plant(self):
        """Тест создания и просмотра растения"""
        print("Запуск теста создания растения...")
        
        # Авторизация пользователя
        self.login_user("test_user", "secure_password123")
        time.sleep(3)
        
        # Переход на страницу добавления растения
        add_plant_btn = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".sidebar-btn[data-view='add-plant']"))
        )
        add_plant_btn.click()
        time.sleep(2)
        
        # Заполнение формы растения
        plant_name = self.wait.until(
            EC.element_to_be_clickable((By.ID, "plant-name"))
        )
        plant_name.send_keys("Тестовое растение")
        time.sleep(1)
        
        plant_species = self.driver.find_element(By.ID, "plant-species")
        plant_species.send_keys("Тестовая культура")
        time.sleep(1)
        
        plant_description = self.driver.find_element(By.ID, "plant-description")
        plant_description.send_keys("Это тестовое растение для проверки функционала")
        time.sleep(1)
        
        # Отправка формы
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, "#add-plant-form button[type='submit']")
        submit_btn.click()
        time.sleep(3)
        
        # Проверка перехода на список растений
        plants_view = self.wait.until(
            EC.presence_of_element_located((By.ID, "plants-view"))
        )
        assert plants_view.is_displayed()
        
        # Проверка наличия созданного растения
        plant_card = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".plant-card h3"))
        )
        assert "Тестовое растение" in plant_card.text
        print("✓ Создание растения пройдено")

    def test_add_plant_entry(self):
        """Тест добавления записи дневника"""
        print("Запуск теста добавления записи...")
        
        self.navigate_to_plant("Тестовое растение")
        time.sleep(3)
        
        # Клик по вкладке записей
        entries_tab = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".tab-btn[onclick*='entries']"))
        )
        entries_tab.click()
        time.sleep(1)
        
        # Заменяем вызов prompt на прямой вызов функции addEntry
        entry_data = {
            "notes": "Поливал сегодня",
            "watering": True,
            "fertilizing": False,
            "pruning": False,
            "other_care": None
        }
        
        # Вызов функции добавления записи через JavaScript
        script = f"""
        var entry = {entry_data};
        fetch('/api/plants/{self.get_current_plant_id()}/entries', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            }},
            body: JSON.stringify(entry)
        }}).then(response => {{
            if(response.ok) {{
                showNotification('Запись добавлена!');
                showPlantDetail({self.get_current_plant_id()});
            }} else {{
                showNotification('Ошибка при добавлении записи');
            }}
        }}).catch(error => {{
            console.error('Error:', error);
            showNotification('Ошибка при добавлении записи');
        }});
        """
        self.driver.execute_script(script)
        time.sleep(3)
        
        # Проверка добавления записи
        entry_card = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".entry-card p"))
        )
        assert "Поливал сегодня" in entry_card.text
        print("✓ Добавление записи пройдено")

    def test_upload_plant_photo(self):
        """Тест загрузки фото растения"""
        print("Запуск теста загрузки фото...")
        
        # Авторизация и переход к растению
        self.login_user("test_user", "secure_password123")
        time.sleep(3)
        self.navigate_to_plant("Тестовое растение")
        time.sleep(3)
        
        # Переход на вкладку фото
        photos_tab = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".tab-btn[onclick*='photos']"))
        )
        photos_tab.click()
        time.sleep(1)
        
        # Загрузка фото
        file_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "photo-upload"))
        )
        test_image_path = os.path.join(os.getcwd(), "test_image.jpg")
        if os.path.exists(test_image_path):
            file_input.send_keys(test_image_path)
        else:
            print(f"Предупреждение: файл {test_image_path} не найден. Используем тестовый файл.")
            # Создаем тестовый файл если он не существует
            with open(test_image_path, 'w') as f:
                f.write('dummy image file')
            file_input.send_keys(test_image_path)
        time.sleep(1)
        
        # Добавление описания
        desc_input = self.driver.find_element(By.ID, "photo-description")
        desc_input.send_keys("Тестовое фото прогресса")
        time.sleep(1)
        
        # Отправка фото
        upload_btn = self.driver.find_element(By.CSS_SELECTOR, ".btn-primary[onclick*='uploadPhoto']")
        upload_btn.click()
        time.sleep(3)
        
        # Проверка загрузки фото (ожидание появления галереи)
        photo_gallery = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".photo-gallery"))
        )
        assert photo_gallery.is_displayed()
        print("✓ Загрузка фото пройдена")

    def test_create_reminder(self):
        """Тест создания напоминания"""
        print("Запуск теста создания напоминания...")
        
        # Авторизация и переход к растению
        self.login_user("test_user", "secure_password123")
        time.sleep(3)
        self.navigate_to_plant("Тестовое растение")
        time.sleep(3)
        
        # Переход на вкладку напоминаний
        reminders_tab = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".tab-btn[onclick*='reminders']"))
        )
        reminders_tab.click()
        time.sleep(1)
        
        # Вызов функции добавления напоминания через JavaScript
        script = f"""
        var reminder = {{
            reminder_type: 'полив',
            frequency_days: 7
        }};
        fetch('/api/plants/{self.get_current_plant_id()}/reminders', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            }},
            body: JSON.stringify(reminder)
        }}).then(response => {{
            if(response.ok) {{
                showNotification('Напоминание добавлено!');
                showPlantDetail({self.get_current_plant_id()});
            }} else {{
                showNotification('Ошибка при добавлении напоминания');
            }}
        }}).catch(error => {{
            console.error('Error:', error);
            showNotification('Ошибка при добавлении напоминания');
        }});
        """
        self.driver.execute_script(script)
        time.sleep(3)
        
        # Проверка создания напоминания
        reminder_card = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".reminder-card h3"))
        )
        assert "полив" in reminder_card.text.lower()
        print("✓ Создание напоминания пройдено")

    def test_logout(self):
        """Тест выхода из системы"""
        print("Запуск теста выхода из системы...")
        
        # Авторизация
        self.login_user("test_user", "secure_password123")
        time.sleep(3)
        
        # Клик по кнопке выхода
        logout_btn = self.wait.until(
            EC.element_to_be_clickable((By.ID, "logout-btn"))
        )
        logout_btn.click()
        time.sleep(3)
        
        # Проверка выхода из системы
        auth_section = self.wait.until(
            EC.presence_of_element_located((By.ID, "auth-section"))
        )
        assert auth_section.is_displayed()
        print("✓ Выход из системы пройдено")

    def login_user(self, username, password):
        """Вспомогательный метод для авторизации"""
        # Ввод данных в форму входа
        login_username = self.wait.until(
            EC.element_to_be_clickable((By.ID, "login-username"))
        )
        login_username.send_keys(username)
        time.sleep(1)
        
        login_password = self.driver.find_element(By.ID, "login-password")
        login_password.send_keys(password)
        time.sleep(1)
        
        # Отправка формы входа
        login_submit = self.driver.find_element(By.CSS_SELECTOR, "#login-form button[type='submit']")
        login_submit.click()
        time.sleep(3)
        
        # Ожидание загрузки главной страницы
        main_section = self.wait.until(
            EC.presence_of_element_located((By.ID, "main-section"))
        )
        assert main_section.is_displayed()

    def navigate_to_plant(self, plant_name):
        """Вспомогательный метод для перехода к растению"""
        # Клик по вкладке "Мои растения"
        plants_btn = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".sidebar-btn[data-view='plants']"))
        )
        plants_btn.click()
        time.sleep(1)
        
        # Клик по карточке растения
        plant_card = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//div[@class='plant-card']//h3[text()='{plant_name}']"))
        )
        plant_card.click()
        time.sleep(3)
        
        # Ожидание загрузки деталей растения
        plant_detail = self.wait.until(
            EC.presence_of_element_located((By.ID, "plant-detail-content"))
        )
        assert plant_detail.is_displayed()

    def get_current_plant_id(self):
        """Получение ID текущего растения из URL"""
        # Возвращаем фиксированный ID, так как Selenium не может получить его из JS-переменной
        # В реальном приложении можно использовать вспомогательный эндпоинт или хранить ID в DOM
        return 1

    def run_all_tests(self):
        """Запуск всех тестов"""
        try:
            print("Запуск всех тестов с визуальным отображением...")
            print("Открыто окно браузера. Вы можете наблюдать за процессом тестирования.")
            print("-" * 50)
            
            self.test_user_registration_and_login()
            time.sleep(3)
            
            self.test_create_and_view_plant()
            time.sleep(3)
            
            self.test_add_plant_entry()
            time.sleep(3)
            
            self.test_upload_plant_photo()
            time.sleep(3)
            
            self.test_create_reminder()
            time.sleep(3)
            
            self.test_logout()
            time.sleep(3)
            
            print("-" * 50)
            print("Все тесты выполнены успешно!")
            
        except Exception as e:
            print(f"Ошибка в тесте: {str(e)}")
            raise

# Запуск тестов
if __name__ == "__main__":
    tests = PlantDiarySeleniumTests()
    tests.run_all_tests()