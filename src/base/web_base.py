from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.utils.logger import get_logger

logger = get_logger(__name__)


class WebBase:
    def __init__(self, driver: WebDriver, config: dict):
        self.driver = driver
        self.config = config
        self.default_timeout = config.get("default_timeout", 10)
        self.wait = WebDriverWait(self.driver, self.default_timeout)

    def _find_element(self, locator: tuple, timeout: int = None):
        current_wait = WebDriverWait(self.driver, timeout if timeout else self.default_timeout)
        logger.debug(f"Finding element with locator: {locator}")
        try:
            return current_wait.until(EC.presence_of_element_located(locator))
        except TimeoutException:
            logger.error(f"Element with locator {locator} not found within timeout.")
            raise NoSuchElementException(f"Element not found: {locator}")

    def _find_elements(self, locator: tuple, timeout: int = None):
        current_wait = WebDriverWait(self.driver, timeout if timeout else self.default_timeout)
        logger.debug(f"Finding elements with locator: {locator}")
        try:
            return current_wait.until(EC.presence_of_all_elements_located(locator))
        except TimeoutException:
            logger.warning(f"Elements with locator {locator} not found within timeout. Returning empty list.")
            return []

    def _click(self, locator: tuple, timeout: int = None):
        current_wait = WebDriverWait(self.driver, timeout if timeout else self.default_timeout)
        logger.info(f"Clicking on element with locator: {locator}")
        try:
            element = current_wait.until(EC.element_to_be_clickable(locator))
            element.click()
        except TimeoutException:
            logger.error(f"Element {locator} not clickable within timeout.")
            raise TimeoutException(f"Element not clickable: {locator}")

    def _type(self, locator: tuple, text: str, timeout: int = None):
        logger.info(f"Typing '{text}' into element with locator: {locator}")
        element = self._find_element(locator, timeout)
        element.clear()
        element.send_keys(text)

    def _get_text(self, locator: tuple, timeout: int = None) -> str:
        logger.debug(f"Getting text from element with locator: {locator}")
        return self._find_element(locator, timeout).text

    def _is_displayed(self, locator: tuple, timeout: int = 1) -> bool:  # Shorter timeout for checks
        logger.debug(f"Checking if element {locator} is displayed.")
        try:
            return self._find_element(locator, timeout).is_displayed()
        except (TimeoutException, NoSuchElementException):
            return False

    def navigate_to_url(self, url_path: str = ""):
        full_url = self.config["base_web_url"] + url_path
        logger.info(f"Navigating to URL: {full_url}")
        self.driver.get(full_url)

    def get_current_url(self) -> str:
        return self.driver.current_url

    def wait_for_url_contains(self, text_fragment: str, timeout: int = None):
        current_wait = WebDriverWait(self.driver, timeout if timeout else self.default_timeout)
        logger.info(f"Waiting for URL to contain: {text_fragment}")
        try:
            current_wait.until(EC.url_contains(text_fragment))
        except TimeoutException:
            logger.error(
                f"URL did not contain '{text_fragment}' within timeout. Current URL: {self.driver.current_url}"
            )
            raise TimeoutException(
                f"URL did not contain '{text_fragment}'. Current URL: {self.driver.current_url}"
            )
