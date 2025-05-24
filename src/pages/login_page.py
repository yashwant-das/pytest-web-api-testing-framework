from selenium.webdriver.common.by import By

from src.base.web_base import WebBase
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LoginPage(WebBase):
    # Locators for SauceDemo
    USERNAME_FIELD = (By.ID, "user-name")
    PASSWORD_FIELD = (By.ID, "password")
    LOGIN_BUTTON_SUBMIT = (By.ID, "login-button")
    ERROR_MESSAGE_DISPLAY = (By.XPATH, "//div[contains(@class, 'error-message-container')]/h3")

    def __init__(self, driver, config):
        super().__init__(driver, config)
        # Navigation to login page will be handled by the test fixture or test itself using config['login_path']

    def enter_username(self, username: str):
        logger.info(f"Entering username: {username}")  # SauceDemo usernames aren't super sensitive
        self._type(self.USERNAME_FIELD, username)

    def enter_password(self, password: str):
        logger.info("Entering password: ***")
        self._type(self.PASSWORD_FIELD, password)

    def click_login_button(self):
        logger.info("Clicking login button")
        self._click(self.LOGIN_BUTTON_SUBMIT)

    def login(self, username: str, password: str):
        logger.info(f"Attempting login for user: {username}")
        self.enter_username(username)
        self.enter_password(password)
        self.click_login_button()

    def get_error_message(self) -> str:
        if self._is_displayed(self.ERROR_MESSAGE_DISPLAY, timeout=2):  # Error messages appear quickly
            message = self._get_text(self.ERROR_MESSAGE_DISPLAY)
            logger.info(f"Retrieved error message: {message}")
            return message
        logger.warning("Error message element not found or not displayed.")
        return ""

    def is_login_page(self, timeout: int = 5) -> bool:
        try:
            return self._is_displayed(self.USERNAME_FIELD, timeout) and self._is_displayed(
                self.LOGIN_BUTTON_SUBMIT, timeout
            )
        except Exception:
            return False
