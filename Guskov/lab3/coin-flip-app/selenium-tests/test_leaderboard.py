import pytest
from pages.login_page import LoginPage
from pages.leaderboard_page import LeaderboardPage
from pages.game_page import GamePage


class TestLeaderboard:
    @pytest.fixture(autouse=True)
    def login(self, browser, base_url):
        """Автоматический вход перед каждым тестом"""
        login_page = LoginPage(browser, base_url)
        login_page.open_login_page()
        login_page.login("testuser", "testpassword")
        yield

    def test_leaderboard_access(self, browser, base_url):
        """Тест доступа к таблице лидеров"""
        game_page = GamePage(browser, base_url)
        leaderboard_page = LeaderboardPage(browser, base_url)
        
        # Переходим на страницу лидерборда
        game_page.go_to_leaderboard()
        
        # Проверяем, что загрузилась страница лидерборда
        assert "/leaderboard" in browser.current_url
        assert leaderboard_page.is_leaderboard_loaded()

    def test_leaderboard_content(self, browser, base_url):
        """Тест содержимого таблицы лидеров"""
        leaderboard_page = LeaderboardPage(browser, base_url)
        
        # Переходим на страницу лидерборда
        leaderboard_page.open("/leaderboard")
        
        # Получаем данные лидерборда
        leaderboard_data = leaderboard_page.get_leaderboard_data()
        
        # Проверяем, что данные есть
        assert len(leaderboard_data) > 0
        
        # Проверяем структуру данных
        for player in leaderboard_data:
            assert 'username' in player
            assert 'balance' in player
            assert isinstance(player['balance'], float)
            assert player['balance'] >= 0

    def test_leaderboard_refresh(self, browser, base_url):
        """Тест обновления таблицы лидеров"""
        leaderboard_page = LeaderboardPage(browser, base_url)
        
        leaderboard_page.open("/leaderboard")
        
        # Получаем начальные данные
        initial_data = leaderboard_page.get_leaderboard_data()
        
        # Обновляем лидерборд
        leaderboard_page.click_refresh()
        
        # Ждем обновления
        import time
        time.sleep(2)
        
        # Получаем обновленные данные
        updated_data = leaderboard_page.get_leaderboard_data()
        
        # Проверяем, что данные все еще есть
        assert len(updated_data) > 0

    def test_leaderboard_sorting(self, browser, base_url):
        """Тест сортировки таблицы лидеров"""
        leaderboard_page = LeaderboardPage(browser, base_url)
        
        leaderboard_page.open("/leaderboard")
        leaderboard_data = leaderboard_page.get_leaderboard_data()
        
        # Проверяем, что лидерборд отсортирован по убыванию баланса
        if len(leaderboard_data) > 1:
            balances = [player['balance'] for player in leaderboard_data]
            assert balances == sorted(balances, reverse=True)