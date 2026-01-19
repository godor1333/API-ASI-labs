import pytest
import time
from pages.login_page import LoginPage
from pages.game_page import GamePage


class TestGameFunctionality:
    @pytest.fixture(autouse=True)
    def login(self, browser, base_url):
        """Автоматический вход перед каждым тестом игры"""
        login_page = LoginPage(browser, base_url)
        login_page.open_login_page()
        login_page.login("testuser", "testpassword")
        yield

    def test_balance_display(self, browser, base_url):
        """Тест отображения баланса"""
        game_page = GamePage(browser, base_url)
        
        balance = game_page.get_balance()
        assert isinstance(balance, float)
        assert balance >= 0

    def test_bet_amount_change(self, browser, base_url):
        """Тест изменения суммы ставки"""
        game_page = GamePage(browser, base_url)
        
        initial_amount = 50
        game_page.set_bet_amount(initial_amount)
        
        # Проверяем, что сумма отобразилась на кнопке
        flip_button = game_page.find_element(game_page.FLIP_BUTTON)
        assert f"${initial_amount}" in flip_button.text

    def test_side_selection(self, browser, base_url):
        """Тест выбора стороны монеты"""
        game_page = GamePage(browser, base_url)
        
        # Выбираем орла
        game_page.select_side("heads")
        heads_button = game_page.find_element(game_page.HEADS_BUTTON)
        assert "active" in heads_button.get_attribute("class")
        
        # Выбираем решку
        game_page.select_side("tails")
        tails_button = game_page.find_element(game_page.TAILS_BUTTON)
        assert "active" in tails_button.get_attribute("class")

    def test_normal_bet_flow(self, browser, base_url):
        """Тест обычного процесса ставки"""
        game_page = GamePage(browser, base_url)
        
        initial_balance = game_page.get_balance()
        
        # Устанавливаем ставку и сторону
        game_page.set_bet_amount(10)
        game_page.select_side("heads")
        
        # Делаем ставку
        game_page.click_flip()
        
        # Ждем завершения анимации
        game_page.wait_for_coin_flip_complete()
        
        # Проверяем результат
        result = game_page.get_result()
        assert result is not None
        assert result['text'] != ""
        
        # Проверяем, что баланс изменился
        new_balance = game_page.get_balance()
        assert new_balance != initial_balance

    def test_quick_bet_mode(self, browser, base_url):
        """Тест режима быстрой ставки"""
        game_page = GamePage(browser, base_url)
        
        initial_balance = game_page.get_balance()
        
        # Включаем быструю ставку
        game_page.enable_quick_bet()
        
        # Выбираем сторону
        game_page.select_side("tails")
        
        # Нажимаем на быструю ставку
        game_page.click_quick_bet(25)
        
        # Ждем завершения анимации
        game_page.wait_for_coin_flip_complete()
        
        # Проверяем результат
        result = game_page.get_result()
        assert result is not None
        
        # Проверяем изменение баланса
        new_balance = game_page.get_balance()
        assert new_balance != initial_balance

    def test_multiple_quick_bets(self, browser, base_url):
        """Тест нескольких быстрых ставок подряд"""
        game_page = GamePage(browser, base_url)
        
        # Включаем быструю ставку
        game_page.enable_quick_bet()
        game_page.select_side("heads")
        
        # Делаем несколько ставок с разными суммами
        amounts = [10, 25, 50]
        
        for amount in amounts:
            initial_balance = game_page.get_balance()
            game_page.click_quick_bet(amount)
            game_page.wait_for_coin_flip_complete()
            
            new_balance = game_page.get_balance()
            assert new_balance != initial_balance
            
            # Ждем перед следующей ставкой
            time.sleep(1)

    def test_bet_validation(self, browser, base_url):
        """Тест валидации ставок"""
        game_page = GamePage(browser, base_url)
        
        # Пытаемся поставить больше чем есть на балансе
        large_amount = 1000000
        game_page.set_bet_amount(large_amount)
        
        # Кнопка должна быть disabled
        flip_button = game_page.find_element(game_page.FLIP_BUTTON)
        assert not flip_button.is_enabled()
        
        # Пытаемся поставить 0
        game_page.set_bet_amount(0)
        assert not flip_button.is_enabled()