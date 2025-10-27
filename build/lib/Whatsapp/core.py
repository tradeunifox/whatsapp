import requests
import time
from .config import BASE_URL, DEFAULT_TIMEOUT
from .exceptions import AuthenticationError, APIError, NetworkError
from .utils import setup_logger
import base64

class BaseService:
    """Base class for all TradeUnifox services"""

    def __init__(self, username, password, api_key, auto_refresh=True, log_level="INFO"):
        self.username = username
        self.password = password
        self.api_key = api_key
        self.token = None
        self.token_expiry = 0
        self.auto_refresh = auto_refresh
        self.logger = setup_logger(level=log_level)

    def authenticate(self):
        url = f"{BASE_URL}/get-token"
        payload = {
            "username": self.username,
            "password": self.password,
            "api_key": self.api_key
        }

        try:
            self.logger.debug(f"Authenticating user {self.username}")
            res = requests.post(url, json=payload, timeout=DEFAULT_TIMEOUT)
            res.raise_for_status()
            data = res.json()

            # Handle API response safely
            if data.get("token"):
                self.token = data["token"]
                self.token_expiry = time.time() + int(data.get("expires_in", 3600))
                self.logger.info(f"Authentication successful: {data.get('message', 'Token acquired')}")
                return self.token
            else:
                raise AuthenticationError(data.get("message", "Authentication failed"))

        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error during authentication: {e}")

    def _ensure_token(self):
        if not self.token or time.time() >= self.token_expiry:
            self.logger.info("Refreshing token...")
            self.authenticate()

    def request(self, endpoint, method="GET", **kwargs):
        self._ensure_token()
        url = f"{BASE_URL}/{endpoint.lstrip('/')}"

        try:
            self.logger.debug(f"{method.upper()} {url} with payload={kwargs.get('json')}")
            response = requests.request(
                method,
                url,
                auth=(self.username, self.token),  # <-- Automatic Basic Auth
                headers={"Content-Type": "application/json"},
                timeout=DEFAULT_TIMEOUT,
                **kwargs
            )

            if response.status_code == 401 and self.auto_refresh:
                self.logger.warning("Unauthorized. Refreshing token and retrying once...")
                self.authenticate()
                response = requests.request(
                    method,
                    url,
                    auth=(self.username, self.token),
                    headers={"Content-Type": "application/json"},
                    timeout=DEFAULT_TIMEOUT,
                    **kwargs
                )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed with status {getattr(e.response, 'status_code', None)}")
            raise APIError(f"Request failed: {e}")

