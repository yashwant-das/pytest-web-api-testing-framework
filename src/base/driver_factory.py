from selenium import webdriver

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
            # Use system-installed chromedriver (assumes it's in PATH)
            return webdriver.Chrome(options=options)
        elif browser_name == "firefox":
            options = webdriver.FirefoxOptions()
            if headless:
                options.add_argument("--headless")
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
            # Use system-installed geckodriver (assumes it's in PATH)
            return webdriver.Firefox(options=options)
        elif browser_name == "edge":
            options = webdriver.EdgeOptions()
            if headless:
                options.add_argument("--headless")  # Edge uses "headless" too
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            # Use system-installed edgedriver (assumes it's in PATH)
            return webdriver.Edge(options=options)
        # elif browser_name == "safari":
        #     # Safari does not support headless mode via Selenium options directly
        #     # and typically requires enabling 'Allow Remote Automation' in Safari's Develop menu.
        #     # No webdriver_manager for Safari, assumes safari driver is in PATH or use service.
        #     # options = webdriver.SafariOptions() # Safari options are limited
        #     # return webdriver.Safari(options=options)
        #     raise ValueError("Safari driver setup is manual and not fully automated here.")
        else:
            raise ValueError(f"Browser '{browser_name}' is not supported or implemented yet.")
