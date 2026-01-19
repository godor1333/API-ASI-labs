from selenium.webdriver.common.by import By
from .base_page import BasePage


class LoginPage(BasePage):
    # Локаторы
    USERNAME_INPUT = (By.CSS_SELECTOR, "input[type='text']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type='password']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    REGISTER_LINK = (By.LINK_TEXT, "Зарегистрируйтесь")
    REGISTER_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".error-message")

    def open_login_page(self):
        self.open("/login")

    def enter_username(self, username):
        username_input = self.find_element(self.USERNAME_INPUT)
        username_input.clear()
        username_input.send_keys(username)

    def enter_password(self, password):
        password_input = self.find_element(self.PASSWORD_INPUT)
        password_input.clear()
        password_input.send_keys(password)

    def click_login(self):
        self.find_clickable_element(self.LOGIN_BUTTON).click()

    def click_register_link(self):
        self.find_clickable_element(self.REGISTER_LINK).click()

    def click_register_button(self):
        self.find_clickable_element(self.REGISTER_BUTTON).click()

    def login(self, username, password):
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

    def register(self, username, password):
        self.click_register_link()
        self.enter_username(username)
        self.enter_password(password)
        self.click_register_button()

    def get_error_message(self):
        try:
            return self.find_element(self.ERROR_MESSAGE).text
        except:
            return None