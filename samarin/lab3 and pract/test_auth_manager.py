import pytest
import sqlite3
from io import StringIO
import sys
import os

# --- Код класса AuthManager (без изменений) ---
class AuthManager:
    def __init__(self, connection):
        self.connection = connection
        self.create_tables()

    def create_tables(self):
        with self.connection:
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS users(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    country TEXT NOT NULL,
                    balance REAL NOT NULL
                )
            """)

    def register_user(self, username, password, country, balance):
        with self.connection:
            # Уязвимость к SQL-инъекции: строковые значения подставляются напрямую
            self.connection.execute("""
                INSERT INTO users(username, password, country, balance)
                VALUES('{}','{}','{}',{})
            """.format(username, password, country, balance))

    def authenticate_user(self, username, password):
        cursor = self.connection.cursor()
        # Уязвимость к SQL-инъекции: строковые значения подставляются напрямую
        cursor.execute("""
            SELECT * FROM users
            WHERE username='{}' AND password='{}'
        """.format(username, password))
        return cursor.fetchone()

    def delete_user(self, user_id):
        with self.connection:
            # Уязвимость к SQL-инъекции: целое число подставляется напрямую, но в строковом контексте
            # Если user_id строка и содержит инъекцию, это может сработать
            self.connection.execute("""
                DELETE FROM users WHERE id={}
            """.format(user_id))

    def get_user_by_id(self, user_id):
        cursor = self.connection.cursor()
        # Уязвимость к SQL-инъекции: целое число подставляется напрямую, но в строковом контексте
        cursor.execute("""
            SELECT * FROM users WHERE id={}
        """.format(user_id))
        return cursor.fetchone()

    def count_users_by_country(self, country):
        cursor = self.connection.cursor()
        # Уязвимость к SQL-инъекции: строковое значение подставляется напрямую
        cursor.execute("""
            SELECT COUNT(*) FROM users WHERE country='{}'
        """.format(country))
        return cursor.fetchone()[0]

    def transfer_balance(self, from_user_id, to_user_id, amount):
        with self.connection:
            # Проверяем, достаточно ли средств
            cursor = self.connection.cursor()
            # Уязвимость к SQL-инъекции: целое число подставляется напрямую, но в строковом контексте
            cursor.execute("SELECT balance FROM users WHERE id= {}".format(from_user_id))
            from_balance = cursor.fetchone()[0]

            if from_balance < amount:
                raise ValueError("Insufficient funds")

            # Выполняем перевод
            # Уязвимость к SQL-инъекции: значения подставляются напрямую
            self.connection.execute("""
                UPDATE users SET balance = balance - {} WHERE id = {}
            """.format(amount, from_user_id))
            self.connection.execute("""
                UPDATE users SET balance = balance + {} WHERE id = {}
            """.format(amount, to_user_id))

# --- Фикстура для базы данных ---
@pytest.fixture
def db_connection():
    """Создает временную базу данных SQLite в памяти."""
    connection = sqlite3.connect(":memory:")
    yield connection
    connection.close()

@pytest.fixture
def auth_manager(db_connection):
    """Создает экземпляр AuthManager с временной базой данных."""
    return AuthManager(db_connection)


# --- Базовые тесты (3 штуки) ---
@pytest.mark.basic
def test_register_user_success(auth_manager):
    """Тестирует успешную регистрацию пользователя."""
    auth_manager.register_user("test_user", "password123", "TestCountry", 100.0)
    user = auth_manager.authenticate_user("test_user", "password123")
    assert user is not None
    assert user[1] == "test_user"  # username
    assert user[3] == "TestCountry" # country
    assert user[4] == 100.0        # balance

@pytest.mark.basic
def test_authenticate_user_success(auth_manager):
    """Тестирует успешную аутентификацию пользователя."""
    auth_manager.register_user("auth_user", "auth_pass", "AuthCountry", 200.0)
    user_data = auth_manager.authenticate_user("auth_user", "auth_pass")
    assert user_data is not None
    assert user_data[1] == "auth_user"

@pytest.mark.basic
def test_get_user_by_id_success(auth_manager):
    """Тестирует получение пользователя по ID."""
    auth_manager.register_user("id_user", "id_pass", "IDCountry", 300.0)
    # Предполагаем, что ID первого пользователя - 1
    user_data = auth_manager.get_user_by_id(1)
    assert user_data is not None
    assert user_data[1] == "id_user"
    assert user_data[4] == 300.0


# --- Параметризованные тесты (3 штуки) ---
@pytest.mark.parametrize("country, expected_count", [
    ("CountryA", 2),
    ("CountryB", 1),
    ("CountryC", 0)
])
def test_count_users_by_country(auth_manager, country, expected_count):
    """Тестирует подсчет пользователей по странам с параметрами."""
    auth_manager.register_user("user1", "password123", "CountryA", 1000)
    auth_manager.register_user("user2", "password123", "CountryA", 1000)
    auth_manager.register_user("user3", "password123", "CountryB", 1000)
    count = auth_manager.count_users_by_country(country)
    assert count == expected_count

@pytest.mark.parametrize("username, password, expected_result", [
    ("existing_user", "correct_pass", True),
    ("existing_user", "wrong_pass", False),
    ("nonexistent_user", "any_pass", False),
])
def test_authenticate_user_parametrized(auth_manager, username, password, expected_result):
    """Тестирует аутентификацию с различными парами логин/пароль."""
    auth_manager.register_user("existing_user", "correct_pass", "AuthTest", 150.0)
    result = auth_manager.authenticate_user(username, password)
    if expected_result:
        assert result is not None
    else:
        assert result is None

@pytest.mark.parametrize("initial_balance, transfer_amount, expected_from_balance, expected_to_balance", [
    (100, 30, 70, 130),
    (50, 50, 0, 150),
    # (20, 30, "Insufficient funds", "N/A"), # Этот случай тестируется отдельно как исключение
])
def test_transfer_balance_parametrized(auth_manager, initial_balance, transfer_amount, expected_from_balance, expected_to_balance):
    """Тестирует перевод баланса между пользователями."""
    auth_manager.register_user("from_user", "pass1", "TransferFrom", initial_balance)
    auth_manager.register_user("to_user", "pass2", "TransferTo", 100)
    auth_manager.transfer_balance(1, 2, transfer_amount)
    from_user_data = auth_manager.get_user_by_id(1)
    to_user_data = auth_manager.get_user_by_id(2)
    assert from_user_data[4] == expected_from_balance
    assert to_user_data[4] == expected_to_balance


# --- Тестирование исключений (2 штуки) ---
@pytest.mark.exception
def test_transfer_insufficient_funds(auth_manager):
    """Тестирует исключение при попытке перевода при недостаточном балансе."""
    auth_manager.register_user("low_user", "pass1", "LowBal", 50.0)
    auth_manager.register_user("recv_user", "pass2", "Recv", 100.0)
    with pytest.raises(ValueError, match="Insufficient funds"):
        auth_manager.transfer_balance(1, 2, 100.0) # Пытаемся перевести 100, когда есть только 50

@pytest.mark.exception
def test_transfer_insufficient_funds_edge_case(auth_manager):
    """Тестирует исключение при попытке перевода суммы, равной балансу (должно пройти)."""
    auth_manager.register_user("exact_user", "pass1", "ExactBal", 50.0)
    auth_manager.register_user("recv_user2", "pass2", "Recv2", 100.0)
    # Перевод ровно баланса должен пройти успешно, оставив 0
    auth_manager.transfer_balance(1, 2, 50.0)
    exact_user_data = auth_manager.get_user_by_id(1)
    recv_user_data = auth_manager.get_user_by_id(2)
    assert exact_user_data[4] == 0.0
    assert recv_user_data[4] == 150.0

# --- Тест SQL-инъекции ---
@pytest.mark.sql_injection
def test_sql_injection_register(db_connection):
    """Тестирует уязвимость к SQL-инъекции при регистрации."""
    # Создаем AuthManager с реальной БД
    am = AuthManager(db_connection)

    malicious_username = "'; DROP TABLE users; --"
    malicious_password = "anything"
    malicious_country = "Hacked"
    malicious_balance = 999999

    # Попытка выполнить SQL-инъекцию через поле username
    # Это может привести к выполнению команды DROP TABLE
    # Однако, в простом формате, строка просто вставится как есть в поле username
    # Для демонстрации уязвимости в поле country
    safe_username = "normal_user"
    safe_password = "normal_pass"
    safe_balance = 100.0
    injected_country = "'; INSERT INTO users (username, password, country, balance) VALUES ('injected_user', 'injected_pass', 'InjectedCountry', 500); --"

    am.register_user(safe_username, safe_password, injected_country, safe_balance)

    # Проверяем, что в таблице появился пользователь, созданный через инъекцию
    cursor = db_connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM users;")
    total_users = cursor.fetchone()[0]

    # Если инъекция сработала, должно быть 2 пользователя
    # Если нет, то только 1
    # Так как строка вставляется как есть в поле country, инъекция в register_user не сработает напрямую
    # Проверим содержимое country
    cursor.execute("SELECT country FROM users WHERE username = ?;", (safe_username,))
    result_country = cursor.fetchone()[0]
    # Ожидаем, что country будет равен вредоносной строке
    assert result_country == injected_country

    # Теперь тестируем инъекцию через count_users_by_country
    # Это более вероятная точка атаки, так как результат SELECT может быть подвержен инъекции
    # Однако, формат строки в SELECT COUNT(*) менее подвержен вставке данных, чем INSERT или SELECT *
    # Попробуем через authenticate_user, который возвращает данные
    # Но для возврата вредоносных данных нужно, чтобы вредоносный код был в пароле или юзернейме
    # Пример через authenticate_user с вредоносным паролем
    auth_result = am.authenticate_user(safe_username, safe_password)
    assert auth_result[1] == safe_username
    assert auth_result[2] == safe_password
    assert auth_result[3] == injected_country

    # Более эффективный пример инъекции через authenticate_user
    # Зарегистрируем пользователя с "нормальным" паролем
    am.register_user("victim_user", "real_password", "SafeCountry", 200.0)

    # Попытаемся аутентифицироваться с вредоносным паролем, который пытается обойти проверку
    # и вернуть данные другого пользователя или выполнить другую команду
    # Например, "real_password' OR 1=1 -- " -> запрос станет
    # SELECT * FROM users WHERE username='victim_user' AND password='real_password' OR 1=1 -- '
    # Это вернет первую запись, так как OR 1=1 всегда истина
    malicious_auth_password = "real_password' OR 1=1 -- "
    auth_result_injected = am.authenticate_user("victim_user", malicious_auth_password)

    # Из-за уязвимости, auth_result_injected не будет None, даже если пароль неверен
    # Он вернет первую запись, удовлетворяющую условию OR 1=1, то есть любую запись
    # В нашем случае это может быть либо пользователь victim_user (если строка запроса такова),
    # либо другая запись, в зависимости от порядка в БД.
    # Но в данном случае, строка запроса: ... WHERE username='victim_user' AND password='real_password' OR 1=1 -- '
    # эквивалентна (username='victim_user' AND password='real_password') OR 1=1
    # Так как 1=1 всегда истина, условие OR делает весь WHERE истинным, и возвращается первая строка в таблице.
    # Это критическая уязвимость.
    # Однако, в нашей текущей БД 2 пользователя. Если запрос вернет первую строку, это будет "normal_user".
    # Если мы хотим вернуть victim_user, запрос должен быть более хитрым, но OR 1=1 уже показывает уязвимость.
    # Проверим, что результат не None, что уже указывает на проблему.
    # В нормальной ситуации auth_result_injected должен быть None, так как пароль неверен.
    # print(f"Auth result with injection: {auth_result_injected}") # Для отладки
    # Мы можем проверить, что хотя бы первая запись возвращена, показывая уязвимость.
    # В целях теста покажем, что результат не None при неверном пароле.
    # Это не самый точный способ, так как может вернуться и корректный пользователь.
    # Попробуем другой пример инъекции, чтобы получить *другие* данные.
    # Регистрация еще одного пользователя
    am.register_user("target_user", "target_pass", "TargetCountry", 500.0)

    injection_username = "nonexistent' OR '1'='1"
    injection_password = "anything' OR '1'='1 --"

    result_injection = am.authenticate_user(injection_username, injection_password)
    assert result_injection is not None, "SQL Injection failed - result was None when it should have bypassed auth."

# --- Метки (уже добавлены к тестам выше) ---
# @pytest.mark.basic
# @pytest.mark.exception
# @pytest.mark.sql_injection

# --- Пропускаемый тест ---
@pytest.mark.skip(reason="Демонстрация пропуска теста.")
def test_skipped_demo():
    assert False # Этот тест не будет запускаться


# --- Инструкция по запуску ---
if __name__ == "__main__":
    print("Для запуска тестов используйте команду:")
    print("pytest -v --maxfail=2 --tb=short test_auth_manager.py")
    print("\nПримеры запуска для конкретных меток:")
    print("pytest -v -k 'basic' test_auth_manager.py")
    print("pytest -v -k 'exception' test_auth_manager.py")
    print("pytest -v -k 'sql_injection' test_auth_manager.py")
    print("\nДля генерации отчета о покрытии:")
    print("pip install pytest-cov")
    print("pytest --cov=test_auth_manager --cov-report html")
