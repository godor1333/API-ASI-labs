from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time


class BasePage:
    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 15)  # Увеличено время ожидания

    def open(self, url=""):
        full_url = self.base_url + url
        self.driver.get(full_url)
        self.wait_for_page_loaded()

    def find_element(self, locator, timeout=15):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )

    def find_clickable_element(self, locator, timeout=15):
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )

    def find_elements(self, locator, timeout=15):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_all_elements_located(locator)
        )

    def wait_for_element_to_disappear(self, locator, timeout=15):
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located(locator)
        )

    def wait_for_page_loaded(self, timeout=15):
        """Ожидание загрузки страницы"""
        WebDriverWait(self.driver, timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )

    def click_with_retry(self, locator, retries=3):
        """Клик с повторными попытками"""
        for attempt in range(retries):
            try:
                element = self.find_clickable_element(locator)
                element.click()
                return True
            except Exception as e:
                if attempt == retries - 1:
                    raise e
                time.sleep(1)

    def safe_send_keys(self, locator, text, clear_first=True):
        """Безопасный ввод текста"""
        element = self.find_clickable_element(locator)
        if clear_first:
            element.clear()
        element.send_keys(text)

    def get_current_url(self):
        return self.driver.current_url