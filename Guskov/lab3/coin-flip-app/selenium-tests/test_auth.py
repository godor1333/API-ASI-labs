import pytest
from pages.login_page import LoginPage
from utils.helpers import generate_random_username, generate_random_email


class TestAuthentication:
    def test_successful_registration(self, browser, base_url):
        """Тест успешной регистрации"""
        login_page = LoginPage(browser, base_url)
        username = generate_random_username()
        password = "testpassword123"
        
        login_page.open_login_page()
        login_page.register(username, password)
        
        # Проверяем, что произошел редирект на игровую страницу
        assert "/game" in browser.current_url
        assert browser.current_url == f"{base_url}/game"

    def test_successful_login(self, browser, base_url):
        """Тест успешного входа"""
        login_page = LoginPage(browser, base_url)
        username = "testuser"
        password = "testpassword"
        
        login_page.open_login_page()
        login_page.login(username, password)
        
        # Проверяем редирект на игровую страницу
        assert "/game" in browser.current_url

    def test_invalid_login(self, browser, base_url):
        """Тест входа с неверными данными"""
        login_page = LoginPage(browser, base_url)
        
        login_page.open_login_page()
        login_page.login("nonexistent", "wrongpassword")
        
        # Проверяем, что остались на странице логина
        assert "/login" in browser.current_url

    def test_navigation_after_login(self, browser, base_url):
        """Тест навигации после входа"""
        login_page = LoginPage(browser, base_url)
        
        # Логинимся
        login_page.open_login_page()
        login_page.login("testuser", "testpassword")
        
        # Проверяем, что видим элементы игровой страницы
        assert "/game" in browser.current_url
        
        # Проверяем наличие основных элементов
        from pages.game_page import GamePage
        game_page = GamePage(browser, base_url)
        
        assert game_page.get_balance() >= 0
        assert game_page.find_element(game_page.BET_AMOUNT_INPUT) is not None