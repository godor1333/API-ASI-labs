from selenium.webdriver.common.by import By
from .base_page import BasePage


class GamePage(BasePage):
    # Локаторы
    BALANCE_ELEMENT = (By.CSS_SELECTOR, ".user-info h2")
    BET_AMOUNT_INPUT = (By.CSS_SELECTOR, ".bet-amount input")
    HEADS_BUTTON = (By.XPATH, "//button[contains(text(), 'Орел')]")
    TAILS_BUTTON = (By.XPATH, "//button[contains(text(), 'Решка')]")
    FLIP_BUTTON = (By.CSS_SELECTOR, ".flip-button")
    QUICK_BET_CHECKBOX = (By.CSS_SELECTOR, ".mode-selection input[type='checkbox']")
    QUICK_BET_BUTTONS = (By.CSS_SELECTOR, ".quick-bet-btn")
    COIN_ELEMENT = (By.CSS_SELECTOR, ".coin")
    RESULT_ELEMENT = (By.CSS_SELECTOR, ".result")
    NAVIGATION_LINKS = (By.CSS_SELECTOR, ".nav-links a")

    def get_balance(self):
        balance_text = self.find_element(self.BALANCE_ELEMENT).text
        return float(balance_text.replace("💰 Баланс: $", ""))

    def set_bet_amount(self, amount):
        bet_input = self.find_element(self.BET_AMOUNT_INPUT)
        bet_input.clear()
        bet_input.send_keys(str(amount))

    def select_side(self, side):
        if side.lower() == "heads":
            self.find_clickable_element(self.HEADS_BUTTON).click()
        else:
            self.find_clickable_element(self.TAILS_BUTTON).click()

    def click_flip(self):
        self.find_clickable_element(self.FLIP_BUTTON).click()

    def enable_quick_bet(self):
        checkbox = self.find_element(self.QUICK_BET_CHECKBOX)
        if not checkbox.is_selected():
            checkbox.click()

    def disable_quick_bet(self):
        checkbox = self.find_element(self.QUICK_BET_CHECKBOX)
        if checkbox.is_selected():
            checkbox.click()

    def click_quick_bet(self, amount):
        quick_bet_buttons = self.find_elements(self.QUICK_BET_BUTTONS)
        for button in quick_bet_buttons:
            if f"${amount}" in button.text:
                button.click()
                break

    def wait_for_coin_flip_complete(self):
        self.wait_for_element_to_disappear((By.CSS_SELECTOR, ".coin.flipping"))

    def get_result(self):
        result_element = self.find_element(self.RESULT_ELEMENT)
        return {
            'text': result_element.text,
            'is_win': 'win' in result_element.get_attribute('class'),
            'is_lose': 'lose' in result_element.get_attribute('class')
        }

    def is_coin_flipping(self):
        try:
            coin = self.find_element(self.COIN_ELEMENT)
            return 'flipping' in coin.get_attribute('class')
        except:
            return False

    def go_to_leaderboard(self):
        links = self.find_elements(self.NAVIGATION_LINKS)
        for link in links:
            if "Топ игроков" in link.text or "leaderboard" in link.get_attribute('href'):
                link.click()
                break