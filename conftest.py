import json
import os

import pytest
from dotenv import load_dotenv

from src.base.driver_factory import DriverFactory
from src.utils.logger import get_logger  # Assuming you have a logger utility

logger = get_logger(__name__)

# Load .env file from the config directory
dotenv_path = os.path.join(os.path.dirname(__file__), "config", ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    logger.warning(
        f".env file not found at {dotenv_path}. Relying on environment variables if set elsewhere."
    )


def load_config_file(config_path):
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_path}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from config file: {config_path}")
        return {}


@pytest.fixture(scope="session")
def config():
    env = os.getenv("TEST_ENV", "dev")  # Default to 'dev' if not set
    base_config_path = os.path.join("config", "config.json")
    env_config_path = os.path.join("config", f"config_{env}.json")

    cfg = load_config_file(base_config_path)
    if os.path.exists(env_config_path):
        env_cfg = load_config_file(env_config_path)
        cfg.update(env_cfg)  # Override base config with environment specific

    # Load credentials from environment variables if defined in config
    if "credentials" in cfg:
        for user_type, creds_config in cfg["credentials"].items():
            if isinstance(creds_config, dict):  # Ensure creds_config is a dictionary
                username_env_var = creds_config.get("username_env")
                password_env_var = creds_config.get("password_env")
                if username_env_var:
                    cfg["credentials"][user_type]["username"] = os.getenv(username_env_var)
                if password_env_var:
                    cfg["credentials"][user_type]["password"] = os.getenv(password_env_var)
            else:
                logger.warning(f"Credentials for '{user_type}' are not configured correctly in config.json.")
    return cfg


@pytest.fixture(scope="function")
def web_driver(config):
    browser_name = config.get("browser", "chrome")  # Default to chrome if not specified
    headless_mode = config.get("headless", False)
    logger.info(f"Initializing WebDriver: {browser_name}, Headless: {headless_mode}")
    try:
        driver = DriverFactory.get_driver(browser_name, headless_mode)
        driver.maximize_window()
        yield driver
        logger.info("Quitting WebDriver.")
        driver.quit()
    except Exception as e:
        logger.error(f"Error during WebDriver setup or teardown: {e}")
        pytest.fail(f"WebDriver initialization failed: {e}")


@pytest.fixture(scope="session")
def api_base_client(config):
    from src.base.api_base import APIBase

    return APIBase(config)


@pytest.fixture(scope="session")  # Changed from user_service_client
def booking_service_client(config):
    from src.api_clients.booking_service import BookingService  # Ensure this import is correct

    client = BookingService(config)
    # Optional: Authenticate once per session if all tests need it.
    # Or let individual tests/methods call client.authenticate() if needed.
    # if not client.authenticate():
    #     pytest.skip("API Authentication failed for BookingService, skipping API tests that require auth.")
    return client


@pytest.fixture(scope="session", autouse=True)
def write_allure_environment(config):
    allure_results_dir = "reports/allure-results"
    if not os.path.exists(allure_results_dir):
        os.makedirs(allure_results_dir, exist_ok=True)
    env_file_path = os.path.join(allure_results_dir, "environment.properties")

    try:
        with open(env_file_path, "w") as f:
            f.write(f"Browser={config.get('browser', 'N/A')}\n")
            f.write(f"BaseWebURL={config.get('base_web_url', 'N/A')}\n")
            f.write(f"BaseApiURL={config.get('base_api_url', 'N/A')}\n")
            f.write(f"TestEnvironment={os.getenv('TEST_ENV', 'dev')}\n")
        logger.info(f"Allure environment properties written to {env_file_path}")
    except Exception as e:
        logger.error(f"Failed to write Allure environment properties: {e}")
