import requests
import logging
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class TokenManager:
    """Handles single token generation and management for TradeUnifox WhatsApp"""

    BASE_URL = "https://whatsapp.tradeunifox.com/api"

    def __init__(self, username: str, password: str, api_key: str, log_level=logging.INFO):
        """
        Initializes the TokenManager with user credentials and logging level.

        Args:
            username (str): Your TradeUnifox username.
            password (str): Your TradeUnifox password.
            api_key (str): Your TradeUnifox API key.
            log_level (int, optional): The logging level (e.g., logging.INFO, logging.DEBUG).
                                     Defaults to logging.INFO.
        """
        self.username = username
        self.password = password
        self.api_key = api_key
        self.token: Optional[str] = None
        self.expires_at: Optional[datetime] = None
        self.logger = self._setup_logger(log_level)

    def _setup_logger(self, level):
        """Sets up and returns a logger instance."""
        logger = logging.getLogger("TradeUnifoxToken")
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                                          datefmt="%Y-%m-%d %H:%M:%S")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.setLevel(level)
        return logger

    def generate_token(self) -> Dict[str, Any]:
        """
        Generates a new token from the API.

        Returns:
            Dict[str, Any]: A dictionary containing the new token, its expiry in minutes,
                            and the expiry timestamp in ISO format.

        Raises:
            requests.exceptions.RequestException: If the API request fails.
        """
        url = f"{self.BASE_URL}/get-token"
        payload = {
            "username": self.username,
            "password": self.password,
            "api_key": self.api_key
        }

        try:
            self.logger.info("Generating new token...")
            response = requests.post(url, json=payload)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            # डीबगिंग के लिए पूरा API रिस्पॉन्स प्रिंट करें
            print(f"DEBUG: Full API Response: {data}")

            # टोकन को विभिन्न संभावित कुंजी नामों से निकालने का प्रयास करें
            token = data.get("token") or data.get("access_token") or data.get("auth_token") or data.get("key")

            if not token:
                self.logger.error("Token not found in API response")
                self.logger.error(f"Available keys in response: {list(data.keys())}")
                raise ValueError("Token not found in API response")

            # टोकन और एक्सपायरी जानकारी निकालें
            self.token = token
            expires_in_minutes = data.get("expires_in_minutes", 60)  # Default to 60 minutes

            # एक्सपायरी टाइम की गणना करें
            self.expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)

            self.logger.info(f"Token generated successfully")
            self.logger.info(
                f"Token expires in {expires_in_minutes} minutes at {self.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")

            return {
                "token": self.token,
                "expires_in_minutes": expires_in_minutes,
                "expires_at": self.expires_at.isoformat()
            }
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to generate token: {e}")
            raise
        except ValueError as e:
            self.logger.error(f"Token extraction error: {e}")
            raise

    def check_token_status(self) -> Dict[str, Any]:
        """
        Checks the current token status from the server.

        Returns:
            Dict[str, Any]: A dictionary with the token's status, including whether it exists,
                            its value, and expiry details.
        """
        try:
            self.logger.info("Checking token status from server...")
            url = f"{self.BASE_URL}/check-token"
            payload = {
                "username": self.username,
                "password": self.password,
                "api_key": self.api_key
            }

            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            # डीबगिंग के लिए पूरा API रिस्पॉन्स प्रिंट करें
            print(f"DEBUG: Token Status Response: {data}")

            if data.get("has_token"):
                # टोकन मौजूद है, उसकी जानकारी लौटाएं
                expires_at_str = data.get("expires_at")
                expires_at = datetime.fromisoformat(expires_at_str) if expires_at_str else None

                # टोकन को विभिन्न संभावित कुंजी नामों से निकालने का प्रयास करें
                token = data.get("token") or data.get("access_token") or data.get("auth_token") or data.get("key")

                if expires_at:
                    time_remaining = expires_at - datetime.now()
                    expires_in_minutes = int(
                        time_remaining.total_seconds() / 60) if time_remaining.total_seconds() > 0 else 0

                    self.token = token
                    self.expires_at = expires_at

                    return {
                        "has_token": True,
                        "token": self.token,
                        "expires_in_minutes": expires_in_minutes,
                        "expires_at": expires_at.isoformat()
                    }
                else:
                    return {
                        "has_token": True,
                        "token": token,
                        "expires_in_minutes": 0,
                        "expires_at": None
                    }
            else:
                # कोई टोकन मौजूद नहीं है
                self.token = None
                self.expires_at = None
                return {
                    "has_token": False,
                    "token": None,
                    "expires_in_minutes": 0,
                    "expires_at": None
                }
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to check token status: {e}")
            # जांच करने में विफल होने पर, मान लें कि कोई टोकन मौजूद नहीं है
            return {
                "has_token": False,
                "token": None,
                "expires_in_minutes": 0,
                "expires_at": None,
                "error": str(e)
            }

    def get_token_info(self) -> Dict[str, Any]:
        """
        Gets current token information. If a valid token exists, it's returned.
        Otherwise, a new token is generated.

        Returns:
            Dict[str, Any]: A dictionary with comprehensive token information.
        """
        # पहले सर्वर से टोकन की स्थिति जांचें
        token_status = self.check_token_status()

        if token_status.get("has_token") and token_status.get("expires_in_minutes", 0) > 0:
            # टोकन मौजूद है और वैध है
            return {
                "has_token": True,
                "token": token_status["token"],
                "expires_in_minutes": token_status["expires_in_minutes"],
                "expires_at": token_status["expires_at"],
                "is_new_token": False
            }
        else:
            # टोकन मौजूद नहीं है या एक्सपायर हो गया है, नया टोकन जेनरेट करें
            if token_status.get("has_token"):
                self.logger.info("Token has expired, generating a new one")
            else:
                self.logger.info("No token found, generating a new one")

            token_info = self.generate_token()
            token_info["has_token"] = False
            token_info["is_new_token"] = True

            return token_info

    def is_token_valid(self) -> bool:
        """Checks if the current token is valid (not expired)."""
        if not self.token or not self.expires_at:
            return False
        return datetime.now() < self.expires_at

    def get_minutes_until_expiry(self) -> Optional[int]:
        """Gets the minutes remaining until the token expires."""
        if not self.expires_at:
            return None

        time_remaining = self.expires_at - datetime.now()
        if time_remaining.total_seconds() <= 0:
            return 0

        return int(time_remaining.total_seconds() / 60)

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Gets the authorization headers required for API requests.
        Generates a new token if the current one is invalid.
        """
        if not self.is_token_valid():
            self.get_token_info()  # This will generate a new token if needed

        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }


# Example usage
if __name__ == "__main__":
    # Initialize with your credentials
    token_manager = TokenManager(
        username="ssc",
        password="your_password",
        api_key="your_api_key"
    )

    # Get token information
    token_info = token_manager.get_token_info()

    if token_info["has_token"]:
        print(f"Existing token found, expires in {token_info['expires_in_minutes']} minutes")
    else:
        print(f"New token generated, expires in {token_info['expires_in_minutes']} minutes")

    print(f"Token: {token_info['token']}")
    print(f"Expires at: {token_info['expires_at']}")

    # Use the token for API requests
    headers = token_manager.get_auth_headers()
    print(f"Authorization headers: {headers}")