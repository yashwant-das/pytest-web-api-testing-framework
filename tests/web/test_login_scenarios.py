import pytest

from src.pages.home_page import HomePage  # Or InventoryPage
from src.pages.login_page import LoginPage
from src.utils.logger import get_logger

logger = get_logger(__name__)


@pytest.mark.web
@pytest.mark.smoke
class TestLogin:
    @pytest.fixture(autouse=True)
    def setup_pages(self, web_driver, config):
        self.login_page = LoginPage(web_driver, config)
        self.home_page = HomePage(web_driver, config)  # Or InventoryPage
        # Navigate to login page before each test in this class
        self.login_page.navigate_to_url(config.get("login_path", "/"))  # SauceDemo login is at root

    def test_successful_login(self, config):
        logger.info("Starting test_successful_login for SauceDemo")
        user_creds = config["credentials"].get("standard_user")
        if not user_creds or not user_creds.get("username") or not user_creds.get("password"):
            pytest.skip("SauceDemo standard_user credentials not configured.")
            return

        self.login_page.login(user_creds["username"], user_creds["password"])

        self.home_page.wait_for_url_contains(config.get("home_path_indicator", "inventory.html"), timeout=10)
        assert self.home_page.is_inventory_page_displayed(
            timeout=5
        ), "Inventory page title not displayed after login"
        assert self.home_page.is_shopping_cart_icon_displayed(timeout=2), "Shopping cart icon not displayed"
        logger.info("test_successful_login for SauceDemo completed successfully.")

    @pytest.mark.parametrize(
        "username, password, error_substring",
        [
            ("locked_out_user", "secret_sauce", "locked out"),
            ("invalid_user", "secret_sauce", "Username and password do not match"),
            ("standard_user", "wrong_password", "Username and password do not match"),
            ("", "secret_sauce", "Username is required"),
            ("standard_user", "", "Password is required"),
        ],
    )
    def test_invalid_login_scenarios(self, config, username, password, error_substring):
        logger.info(f"Starting test_invalid_login_scenarios for user: {username}")
        # If username is from config (e.g. for locked_out_user if its creds are stored)
        # you might fetch it like:
        # actual_username = config['credentials'].get(username, {}).get('username', username)
        # actual_password = config['credentials'].get(username, {}).get('password', password)
        # self.login_page.login(actual_username, actual_password)

        self.login_page.login(username, password)  # Using parametrized direct values

        error_message = self.login_page.get_error_message()
        assert error_message, f"Error message not displayed for user '{username}'."
        assert (
            error_substring.lower() in error_message.lower()
        ), f"Expected error message for '{username}' to contain '{error_substring}', but got '{error_message}'"
        logger.info(f"test_invalid_login_scenarios for '{username}' completed. Error: {error_message}")
