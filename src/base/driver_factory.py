from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# from selenium.webdriver.safari.service import Service as SafariService # Safari setup is more manual


class DriverFactory:
    @staticmethod
    def get_driver(browser_name: str, headless: bool = False):
        browser_name = browser_name.lower()
        if browser_name == "chrome":
            options = webdriver.ChromeOptions()
            if headless:
                options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")  # Standard size
            return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        elif browser_name == "firefox":
            options = webdriver.FirefoxOptions()
            if headless:
                options.add_argument("--headless")
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
            return webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
        elif browser_name == "edge":
            options = webdriver.EdgeOptions()
            if headless:
                options.add_argument("--headless")  # Edge uses "headless" too
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            return webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
        # elif browser_name == "safari":
        #     # Safari does not support headless mode via Selenium options directly
        #     # and typically requires enabling 'Allow Remote Automation' in Safari's Develop menu.
        #     # No webdriver_manager for Safari, assumes safari driver is in PATH or use service.
        #     # options = webdriver.SafariOptions() # Safari options are limited
        #     # return webdriver.Safari(options=options)
        #     raise ValueError("Safari driver setup is manual and not fully automated here.")
        else:
            raise ValueError(f"Browser '{browser_name}' is not supported or implemented yet.")
