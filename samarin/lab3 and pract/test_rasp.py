import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def get_driver():
    """Возвращает экземпляр драйвера Chrome."""
    return webdriver.Chrome()

# --- Ожидаемое расписание ---
EXPECTED_SCHEDULE = """Основное расписание
Понедельник
Пара Дисциплина Преподаватель Дист/Ауд Примечание Неделя
1 пара / 08:30-10:00 Инфокоммуникационные системы и сети / Лк. Гуськова Юлия Александровна 220 Всегда
2 пара / 10:10-11:40 Инфокоммуникационные системы и сети / Лк. Гуськова Юлия Александровна 220 Всегда
Вторник
Пара Дисциплина Преподаватель Дист/Ауд Примечание Неделя
1 пара / 08:30-10:00 Надежность и отказоустойчивость информационных систем / Лк. Жидкова Наталья Валерьевна 226 Всегда
2 пара / 10:10-11:40 Надежность и отказоустойчивость информационных систем / Лк. Жидкова Наталья Валерьевна 226 Всегда
3 пара / 12:10-13:40 Управление ИТ-проектами / Лк. Мельникова Оксана Юрьевна 114 Всегда
4 пара / 13:50-15:20 Управление ИТ-проектами / Лк. Мельникова Оксана Юрьевна 114 Всегда
Среда
Пара Дисциплина Преподаватель Дист/Ауд Примечание Неделя
1 пара / 08:30-10:00 Анализ больших данных / Лк. Рябов Антон Владимирович 5 05.11.2025 занятий не будет Всегда
2 пара / 10:10-11:40 Анализ больших данных / Лк. Рябов Антон Владимирович 5 05.11.2025 занятий не будет Всегда
3 пара / 12:10-13:40 Организационно-экономическое обоснование научных и технических решений / Лк. Гусева Ирина Борисовна 218 Всегда
4 пара / 13:50-15:20 Организационно-экономическое обоснование научных и технических решений / Лк. Гусева Ирина Борисовна 218 Всегда
5 пара / 15:30-17:00 Основы тестирования программного обеспечения / Пз. Комаров Александр Олегович 324 Всегда
1 пара вечер / 17:30-19:00 Основы тестирования программного обеспечения / Пз. Комаров Александр Олегович 324 Всегда
2 пара вечер / 19:10-20:40 Основы тестирования программного обеспечения / Пз. Комаров Александр Олегович 324 Всегда
Четверг
Пара Дисциплина Преподаватель Дист/Ауд Примечание Неделя
1 пара / 08:30-10:00 Технологии программирования / Лк. Емельянова Татьяна Владимировна 206 Всегда
2 пара / 10:10-11:40 Технологии программирования / Лк. Емельянова Татьяна Владимировна 206 Всегда
3 пара / 12:10-13:40 Эксплуатация и модификация информационных систем / Лк. свободная 226 Жидкова НВ Всегда
4 пара / 13:50-15:20 Эксплуатация и модификация информационных систем / Лк. свободная 226 Жидкова НВ Всегда
Пятница
Пара Дисциплина Преподаватель Дист/Ауд Примечание Неделя
2 пара / 10:10-11:40 Основы тестирования программного обеспечения / Пз. Комаров Александр Олегович 324 Всегда
3 пара / 12:10-13:40 Основы тестирования программного обеспечения / Пз. Комаров Александр Олегович 324 Всегда
4 пара / 13:50-15:20 Основы тестирования программного обеспечения / Пз. Комаров Александр Олегович 324 Всегда
Суббота
Пара Дисциплина Преподаватель Дист/Ауд Примечание Неделя
1 пара / 08:30-10:00 Основы тестирования программного обеспечения / Пз. Комаров Александр Олегович 324 Всегда
2 пара / 10:10-11:40 Основы тестирования программного обеспечения / Пз. Комаров Александр Олегович 324 Всегда
3 пара / 12:10-13:40 Основы тестирования программного обеспечения / Пз. Комаров Александр Олегович 324 Всегда
4 пара / 13:50-15:20 Основы тестирования программного обеспечения / Пз. Комаров Александр Олегович 324 Всегда"""

# --- URL страницы с формой расписания ---
URL = "https://api.nntu.ru/raspisanie"

# --- Параметры для формы ---
# ЗАМЕНИТЕ НА ВАШИ КОНКРЕТНЫЕ ЗНАЧЕНИЯ (значения атрибута value в опциях)
FORM_OF_EDUCATION_VALUE = "1"  # Значение 'value' для "Очная" -> <option value="1">Очная</option>
GROUP_NAME_VALUE = "777"       # Значение 'value' для "АСИ 22-1" -> <option value="777">АСИ 22-1</option>
SCHEDULE_TYPE_VALUE = "1"      # Значение 'value' для "Основное" -> <option value="1">Основное</option>

FORM_OF_EDUCATION_VALUE2 = "1"  # Значение 'value' для "Очная" -> <option value="1">Очная</option>
GROUP_NAME_VALUE2 = "776"       # Значение 'value' для "АСИ 22-1" -> <option value="777">АСИ 22-1</option>
SCHEDULE_TYPE_VALUE2 = "1"      # Значение 'value' для "Основное" -> <option value="1">Основное</option>



@pytest.fixture(scope="function")
def driver():
    """Фикстура pytest для создания и закрытия экземпляра драйвера."""
    driver_instance = get_driver()
    yield driver_instance
    driver_instance.quit()

def select_dropdown_option_by_value(driver, dropdown_id, option_value):
    """Выбирает опцию в выпадающем списке по ID и значению 'value', дожидаясь её появления."""
    try:
        # 1. Ждем появления самого элемента <select>
        dropdown_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, dropdown_id))
        )

        # 2. Ждем появления *конкретной* опции <option> с нужным value ВНУТРИ этого <select>
        # Для этого можно использовать CSS-селектор: #id option[value='value']
        option_locator = (By.CSS_SELECTOR, f"#{dropdown_id} option[value='{option_value}']")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(option_locator)
        )
        print(f"Опция с value '{option_value}' найдена в списке с ID '{dropdown_id}'.")

        # 3. Теперь, когда опция точно есть, используем Select для выбора
        select = Select(dropdown_element)
        select.select_by_value(option_value)
        print(f"Выбрано значение '{option_value}' (value) в выпадающем списке с ID '{dropdown_id}'.")

    except Exception as e:
        print(f"Ошибка при выборе значения '{option_value}' (value) в выпадающем списке '{dropdown_id}': {e}")
        raise # Пробрасываем исключение, чтобы тест упал

def get_schedule_from_page(driver, url, form_edu_val, group_val, sched_type_val):
    """Открывает страницу, заполняет форму и получает расписание."""
    driver.get(url)
    try:
        # --- Выбираем Форму обучения ---
        select_dropdown_option_by_value(driver, "studentAdvert__controls--department", form_edu_val)

        # --- Выбираем Группу ---
        select_dropdown_option_by_value(driver, "studentAdvert__controls--groups", group_val)

        # --- Выбираем Тип Расписания ---
        select_dropdown_option_by_value(driver, "studentAdvert__controls--types", sched_type_val)

        # --- Ожидание загрузки расписания ---
        expected_h2_text = "Основное расписание"
        if sched_type_val == "2":
            expected_h2_text = "Экзаменационное расписание"
        elif sched_type_val == "3":
            expected_h2_text = "Расписание практики"

        schedule_loaded_element = WebDriverWait(driver, 15).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#printable h2"), expected_h2_text)
        )

        # Извлекаем весь текст из контейнера #printable
        schedule_container = driver.find_element(By.ID, "printable")
        schedule_text = schedule_container.text

        return schedule_text

    except TimeoutException:
        print(f"Ошибка: Элемент с расписанием не загрузился в контейнере #printable на странице {url} в течение 15 секунд.")
        return ""
    except NoSuchElementException as e:
        print(f"Ошибка: Элемент не найден: {e}")
        return ""

def test_schedule_match(driver):
    """Тест: полученное расписание должно совпадать с ожидаемым."""
    actual_schedule = get_schedule_from_page(driver, URL, FORM_OF_EDUCATION_VALUE, GROUP_NAME_VALUE, SCHEDULE_TYPE_VALUE)

    print(f"Полученное расписание:\n{actual_schedule}")
    print(f"Ожидаемое расписание:\n{EXPECTED_SCHEDULE}")

    assert actual_schedule == EXPECTED_SCHEDULE, f"Расписание не совпадает!\nПолучено:\n{actual_schedule}\nОжидается:\n{EXPECTED_SCHEDULE}"

def test_schedule_mismatch():
    """Тест: демонстрирует, что тест падает при изменении ожидаемого значения."""
    driver_instance = get_driver()
    try:
        actual_schedule = get_schedule_from_page(driver_instance, URL, FORM_OF_EDUCATION_VALUE2, GROUP_NAME_VALUE2, SCHEDULE_TYPE_VALUE2)

        wrong_expected_schedule = get_schedule_from_page(driver_instance, URL, FORM_OF_EDUCATION_VALUE, GROUP_NAME_VALUE, SCHEDULE_TYPE_VALUE)

        print(f"Полученное расписание:\n{actual_schedule}")
        print(f"Неверное ожидаемое расписание:\n{wrong_expected_schedule}")

        assert actual_schedule == wrong_expected_schedule, f"Этот тест должен упасть, так как расписания не совпадают!\nПолучено:\n{actual_schedule}\nОжидается (намеренно неправильно):\n{wrong_expected_schedule}"
    finally:
        driver_instance.quit()

if __name__ == "__main__":
    # Запуск тестов pytest
    pytest.main(["-v", "-s", __file__])
