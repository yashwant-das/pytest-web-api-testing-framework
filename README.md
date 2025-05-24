# pytest-web-api-testing-framework

A robust and scalable Python framework for Web (Selenium) and API (Requests) testing, built with Pytest. Designed for clarity, maintainability, and ease of extension.

**Showcasing:**

- Web UI testing for **SauceDemo** (`https://www.saucedemo.com/`)
- API testing for **Restful-booker** (`https://restful-booker.herokuapp.com/`), including authentication.

## Core Principles

- **Separation of Concerns:** Distinct responsibilities for different framework components.
- **Readability & Maintainability:** Clean, understandable, and easy-to-modify code.
- **Scalability:** Easily accommodate new tests, pages, and API endpoints.
- **Reusability:** Shared common functionalities and base classes.
- **Configuration Driven:** Externalized settings for URLs, credentials, and browser types.

## Prerequisites

- Python 3.9+ (`python3 --version`)
- pip (Python package installer)
- Git (for cloning the repository)
- (Optional, for Allure reports) [Allure Commandline](https://allurereport.org/docs/gettingstarted-installation/) installed and in your system's PATH.

## Setup Instructions

1. **Clone the Repository:**

  ```bash
    git clone <your-repo-url> # This will create a 'pytest-web-api-testing-framework' directory
    cd pytest-web-api-testing-framework
    ```

2. **Create and Activate a Virtual Environment (Recommended):**
  - On macOS/Linux:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
  - On Windows:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
  *(You should see `(venv)` at the beginning of your command prompt.)*

3. **Install Dependencies:**
  ```bash
  pip install -r requirements.txt
  ```

  If there's a `requirements-dev.txt` for development tools:

  ```bash
  pip install -r requirements-dev.txt
  ```

4. **Set Up Environment Variables:**

  ```bash
  cp config/.env.example config/.env
  ```

  Edit `config/.env` and replace placeholders with actual credentials:

- `SAUCE_USERNAME`: `standard_user` (for SauceDemo)
- `SAUCE_PASSWORD`: `secret_sauce` (for SauceDemo)
- `BOOKER_USERNAME`: `admin` (for Restful-booker API)
- `BOOKER_PASSWORD`: `password123` (for Restful-booker API)
- `TEST_ENV`: (Optional) Set to `dev`, `staging`, etc. Defaults to `dev` if not set.

## Running Tests

This framework uses Pytest as its test runner.

- **Run All Tests:**

  ```bash
  pytest
  ```

- **Run Specific Test Types (using markers):**
  - Web UI tests:

   ```bash
   pytest -m web
   ```

  - API tests:

   ```bash
   pytest -m api
   ```

  - Smoke tests:

   ```bash
   pytest -m smoke
   ```

  - Regression tests:

   ```bash
   pytest -m regression
   ```

- **Run Tests in a Specific File or Directory:**

  ```bash
  pytest tests/web/test_login_scenarios.py
  pytest tests/api/
  ```

- **Run Tests with More Verbosity and Output:**

  ```bash
  pytest -v -s
  ```

  (`-v` for verbose, `-s` to show print statements and logs)

- **Run Tests in Parallel (if `pytest-xdist` is installed):**

  ```bash
  pytest -n auto  # Use all CPU cores
  pytest -n 4     # Run with 4 workers
  ```

## Generating Test Reports

1. **Basic HTML Report (pytest-html):**

  ```bash
  pytest --html=reports/pytest_report.html --self-contained-html
  ```

  Open `reports/pytest_report.html` in your browser.

2. **Allure Report (Recommended):**

- **Step 1:** Run tests and generate Allure results:

    ```bash
    pytest --alluredir=reports/allure-results
    ```

- **Step 2:** Generate the HTML report:

    ```bash
    allure generate reports/allure-results -o reports/allure-report --clean
    ```

- **Step 3:** Open the Allure report:

    ```bash
    allure open reports/allure-report
    ```

## Framework Architecture & Directory Structure

The framework is organized for separation of concerns and maintainability.

```
pytest-web-api-testing-framework//
├── .github/
│   └── workflows/
│       └── ci.yml
├── .gitignore
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── pyproject.toml
├── .pre-commit-config.yaml
├── conftest.py
│
├── config/
│   ├── config.json
│   ├── config_dev.json
│   ├── config_staging.json
│   ├── .env.example
│   └── .env
│
├── src/
│   ├── base/
│   │   ├── api_base.py
│   │   ├── web_base.py
│   │   └── driver_factory.py
│   │
│   ├── pages/
│   │   ├── login_page.py
│   │   └── home_page.py
│   │
│   ├── api_clients/
│   │   └── booking_service.py
│   │
│   └── utils/
│       ├── logger.py
│       ├── data_generator.py
│       └── assertions.py
│
├── tests/
│   ├── conftest.py
│   ├── web/
│   │   └── test_login_scenarios.py
│   │
│   └── api/
│       └── test_booking_api.py
│
└── reports/
   ├── allure-results/
   ├── allure-report/
   └── pytest_report.html
```

### Key Components

- **`config/`**: Manages all external configurations, including URLs, browser settings, and credentials. Uses `.env` for sensitive data.
- **`src/base/`**: Foundational classes. `DriverFactory` provides WebDriver instances. `WebBase` offers common Selenium interactions. `APIBase` provides common API methods and authentication.
- **`src/pages/`**: Page Object Model (POM) for web UI interactions.
- **`src/api_clients/`**: Classes for interacting with specific API services/endpoints.
- **`src/utils/`**: Shared utilities like logging and test data generation.
- **`tests/`**: Test scripts, organized by type (web, api). Uses Pytest fixtures for setup/teardown.
- **`conftest.py`**: Shared Pytest fixtures, e.g., WebDriver and API client instances, and the main `config` fixture.

## Configuration System

Configuration is loaded in this order:

1. **`config/.env`**: Loaded into environment variables using `python-dotenv`.
2. **`TEST_ENV` Environment Variable**: Determines which environment-specific config to use. Defaults to `dev`.
3. **`config/config.json`**: Base configuration.
4. **`config/config_<TEST_ENV>.json`**: Environment-specific overrides.
5. **Credential Injection**: The `config` fixture resolves credential placeholders in JSON configs using environment variables.

This layered approach enables flexible and secure management of test settings across environments.

## Code Quality: Linting and Formatting

Uses **Black** (formatting), **isort** (import sorting), and **Flake8** (linting). Configurations are in `pyproject.toml`.

### Manual Usage

1. Sort imports:

  ```bash
  isort .
  ```

2. Format code:

  ```bash
  black .
  ```

3. Check for style and logical errors:

  ```bash
  flake8 .
  ```

### Using Pre-commit Hooks (Recommended)

1. Install pre-commit:

  ```bash
  pip install pre-commit
  ```

2. Set up Git hooks:

  ```bash
  pre-commit install
  ```

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Make your changes.
4. Ensure all tests pass (`pytest`).
5. Ensure code is formatted and linted.
6. Commit your changes (`git commit -m 'Add some feature'`).
7. Push to the branch (`git push origin feature/YourFeature`).
8. Open a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.
