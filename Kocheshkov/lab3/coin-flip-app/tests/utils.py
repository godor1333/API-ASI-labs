from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def wait_for_app_ready(driver, timeout=10):
    WebDriverWait(driver, timeout).until_not(
        EC.presence_of_element_located((By.CLASS_NAME, "app-loading"))
    )

def wait_for_auth_check(driver, timeout=10):
    WebDriverWait(driver, timeout).until_not(
        EC.presence_of_element_located((By.CLASS_NAME, "loading"))
    )
