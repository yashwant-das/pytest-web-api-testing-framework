import os

import requests

from src.utils.logger import get_logger

logger = get_logger(__name__)


class APIBase:
    def __init__(self, config: dict):
        self.base_url = config.get("base_api_url", "")
        if not self.base_url:
            logger.error("base_api_url not found in config. API tests may fail.")
        self.session = requests.Session()  # Use a session for cookie persistence
        self.default_timeout = config.get("default_timeout", 10)
        self.config = config  # Store config for auth endpoint if needed
        self.auth_token = None  # To store the auth token

        common_headers = {"Content-Type": "application/json", "Accept": "application/json"}
        self.session.headers.update(common_headers)

    def authenticate(self):
        """Authenticates with Restful-booker and stores the token."""
        auth_endpoint = self.config.get("api_auth_endpoint")
        api_creds = self.config.get("credentials", {}).get("api_user", {})
        username = api_creds.get("username")
        password = api_creds.get("password")

        if not all([auth_endpoint, username, password]):
            logger.error("API authentication credentials or endpoint not fully configured.")
            return False

        auth_url = f"{self.base_url}{auth_endpoint}"
        payload = {"username": username, "password": password}
        logger.info(f"Attempting API authentication to {auth_url}")
        try:
            response = self.session.post(auth_url, json=payload, timeout=self.default_timeout)
            response.raise_for_status()  # Will raise an HTTPError for bad responses
            token_data = response.json()
            self.auth_token = token_data.get("token")
            if self.auth_token:
                logger.info("API Authentication successful. Token received.")
                # For Restful-booker, token is typically sent as a cookie
                # self.session.cookies.set("token", self.auth_token) # Requests session handles cookies
                return True
            else:
                logger.error(f"API Authentication failed. Token not found in response: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"API Authentication request failed: {e}")
            return False

    def _request(
        self,
        method: str,
        endpoint: str,
        params=None,
        data=None,
        json=None,
        headers=None,
        requires_auth=False,
        **kwargs,
    ):
        if requires_auth and not self.auth_token:
            logger.warning(f"Endpoint {endpoint} requires auth, but no token. Attempting to authenticate...")
            if not self.authenticate():
                logger.error("Authentication failed. Cannot proceed with authenticated request.")
                # Optionally raise an exception here or let the request fail
                # For now, we'll let it proceed and likely fail if token is truly needed by endpoint
                # raise Exception("Authentication required and failed.")
                pass  # Let the request proceed and likely fail at the server if token is missing

        url = f"{self.base_url}{endpoint}"
        request_headers = self.session.headers.copy()  # Start with session headers

        if headers:
            request_headers.update(headers)

        # For Restful-booker, if a token exists, it's often sent via a Cookie header for PUT/DELETE
        # The requests.Session should handle cookies automatically if set via response.
        # However, Restful-booker specifically looks for 'Cookie: token=...' or an Auth header.
        # Let's ensure the token is in headers if needed explicitly by Restful-booker style for PUT/PATCH/DELETE.
        # For many APIs, a Bearer token is more common: request_headers["Authorization"] = f"Bearer {self.auth_token}"
        if requires_auth and self.auth_token:
            # Restful-booker PUT/PATCH/DELETE can use Basic Auth OR Token in Cookie or Auth header
            # Using the token in an "Authorization: Bearer <token>" is a common pattern,
            # but Restful-booker docs also show "Cookie: token=<value>"
            # For simplicity, let's try adding it as a direct cookie header for PUT/DELETE
            # Alternatively, some endpoints might expect Basic Auth with the token as username & no password
            if method.upper() in ["PUT", "PATCH", "DELETE"]:
                # Option 1: Cookie header (if session doesn't manage it as expected by server)
                if "Cookie" not in request_headers and "token" not in self.session.cookies:
                    request_headers["Cookie"] = f"token={self.auth_token}"
                # Option 2: Authorization Bearer Token (more standard for many APIs)
                # request_headers["Authorization"] = f"Bearer {self.auth_token}"
                # Option 3: Basic Auth with token as username (Restful-booker also supports this)
                # kwargs['auth'] = (self.auth_token, '') # username=token, password=''

        logger.info(f"API Request: {method.upper()} {url}")
        if params:
            logger.debug(f"Params: {params}")
        if data:
            logger.debug(f"Data (form-encoded): {data}")
        if json:
            logger.debug(f"JSON Payload: {json}")
        if request_headers:
            logger.debug(f"Effective Headers: {request_headers}")

        try:
            response = self.session.request(
                method,
                url,
                params=params,
                data=data,
                json=json,
                headers=request_headers,  # Use the combined headers
                timeout=kwargs.pop("timeout", self.default_timeout),
                **kwargs,
            )
            logger.info(f"API Response: {response.status_code} for {method.upper()} {url}")
            response_text_preview = response.text[:500] + "..." if len(response.text) > 500 else response.text
            logger.debug(f"Response Body Preview: {response_text_preview}")
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"API Request Exception for {method.upper()} {url}: {e}")
            raise

    # GET, POST, etc. methods can now accept 'requires_auth'
    def get(self, endpoint: str, params=None, requires_auth=False, **kwargs) -> requests.Response:
        return self._request("GET", endpoint, params=params, requires_auth=requires_auth, **kwargs)

    def post(self, endpoint: str, data=None, json=None, requires_auth=False, **kwargs) -> requests.Response:
        # Auth POST is special, doesn't require prior token
        if endpoint == self.config.get("api_auth_endpoint"):
            return self._request("POST", endpoint, data=data, json=json, requires_auth=False, **kwargs)
        return self._request("POST", endpoint, data=data, json=json, requires_auth=requires_auth, **kwargs)

    def put(self, endpoint: str, data=None, json=None, requires_auth=True, **kwargs) -> requests.Response:
        return self._request("PUT", endpoint, data=data, json=json, requires_auth=requires_auth, **kwargs)

    def delete(self, endpoint: str, requires_auth=True, **kwargs) -> requests.Response:
        return self._request("DELETE", endpoint, requires_auth=requires_auth, **kwargs)

    def patch(self, endpoint: str, data=None, json=None, requires_auth=True, **kwargs) -> requests.Response:
        return self._request("PATCH", endpoint, data=data, json=json, requires_auth=requires_auth, **kwargs)
