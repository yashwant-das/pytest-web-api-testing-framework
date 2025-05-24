from selenium.webdriver.common.by import By

from src.base.web_base import WebBase
from src.utils.logger import get_logger

logger = get_logger(__name__)


class HomePage(WebBase):  # Or rename to InventoryPage for SauceDemo context
    # Locators for SauceDemo Inventory Page
    PAGE_TITLE = (By.XPATH, "//span[@class='title' and text()='Products']")  # "Products" title
    SHOPPING_CART_ICON = (By.ID, "shopping_cart_container")
    BURGER_MENU_BUTTON = (By.ID, "react-burger-menu-btn")  # For logout etc.

    def __init__(self, driver, config):
        super().__init__(driver, config)

    def is_inventory_page_displayed(self, timeout: int = None) -> bool:
        logger.info("Checking if inventory page (Products title) is displayed")
        # Check for a unique element on the inventory page
        return self._is_displayed(self.PAGE_TITLE, timeout=timeout)

    def is_shopping_cart_icon_displayed(self, timeout: int = None) -> bool:
        logger.info("Checking if shopping cart icon is displayed")
        return self._is_displayed(self.SHOPPING_CART_ICON, timeout=timeout)

    # Add more methods for interacting with inventory items if needed for tests
