import requests
import random
import string


def generate_random_username(length=8):
    """Генерация случайного имени пользователя"""
    letters = string.ascii_lowercase
    return 'test_' + ''.join(random.choice(letters) for i in range(length))


def generate_random_email():
    """Генерация случайного email"""
    return f"test_{random.randint(1000, 9999)}@test.com"


def cleanup_user_via_api(api_url, username):
    """Очистка тестового пользователя через API"""
    try:
        # Этот эндпоинт нужно будет добавить в бэкенд для тестов
        response = requests.delete(f"{api_url}/api/test/cleanup", 
                                 json={"username": username})
        return response.status_code == 200
    except:
        return False


def get_user_balance_via_api(api_url, username):
    """Получение баланса пользователя через API"""
    try:
        response = requests.get(f"{api_url}/api/test/user", 
                              params={"username": username})
        if response.status_code == 200:
            return response.json().get('balance')
    except:
        return None