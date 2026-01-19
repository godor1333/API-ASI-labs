from selenium.webdriver.common.by import By
from .base_page import BasePage


class LeaderboardPage(BasePage):
    # Локаторы
    LEADERBOARD_ITEMS = (By.CSS_SELECTOR, ".leaderboard-item")
    PLAYER_USERNAME = (By.CSS_SELECTOR, ".username")
    PLAYER_BALANCE = (By.CSS_SELECTOR, ".balance")
    REFRESH_BUTTON = (By.CSS_SELECTOR, ".refresh-btn")

    def get_leaderboard_data(self):
        items = self.find_elements(self.LEADERBOARD_ITEMS)
        leaderboard = []
        
        for item in items:
            try:
                username = item.find_element(*self.PLAYER_USERNAME).text
                balance_text = item.find_element(*self.PLAYER_BALANCE).text
                balance = float(balance_text.replace('$', ''))
                leaderboard.append({'username': username, 'balance': balance})
            except:
                continue
        
        return leaderboard

    def click_refresh(self):
        self.find_clickable_element(self.REFRESH_BUTTON).click()

    def is_leaderboard_loaded(self):
        try:
            items = self.find_elements(self.LEADERBOARD_ITEMS)
            return len(items) > 0
        except:
            return False