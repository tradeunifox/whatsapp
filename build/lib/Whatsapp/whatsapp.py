import requests
import logging
import sys

class WhatsApp:
    """TradeUnifox WhatsApp Service"""

    BASE_URL = "https://whatsapp.tradeunifox.com/api"

    class TokenManager:
        """Handles token generation"""
        def __init__(self, username: str, password: str, api_key: str, logger=None):
            self.username = username
            self.password = password
            self.api_key = api_key
            self.token = None
            self.logger = logger

        def generate_token(self):
            url = f"{WhatsApp.BASE_URL}/get-token"
            payload = {
                "username": self.username,
                "password": self.password,
                "api_key": self.api_key
            }

            try:
                if self.logger:
                    self.logger.info("Generating token...")
                response = requests.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                self.token = data.get("token")
                if self.logger:
                    self.logger.info(f"Token generated successfully: {self.token}")
                return self.token
            except requests.exceptions.RequestException as e:
                if self.logger:
                    self.logger.error(f"Failed to generate token: {e}")
                raise

    class MessageSender:
        """Handles sending WhatsApp messages"""
        def __init__(self, username: str, token: str, api_key: str, logger=None):
            self.username = username
            self.token = token
            self.api_key = api_key
            self.logger = logger

        def send_message(self, to: str, message: str):
            url = f"{WhatsApp.BASE_URL}/send"
            payload = {
                "to": to,
                "message": message,
                "api_key": self.api_key
            }

            try:
                if self.logger:
                    self.logger.info(f"Sending message to {to}")
                response = requests.post(url, auth=(self.username, self.token), json=payload)
                response.raise_for_status()
                if self.logger:
                    self.logger.info("Message sent successfully")
                return response.json()
            except requests.exceptions.RequestException as e:
                if self.logger:
                    self.logger.error(f"Failed to send message: {e}")
                raise

    def __init__(self, username: str, password: str, api_key: str, log_level=logging.INFO):
        self.username = username
        self.password = password
        self.api_key = api_key
        self.logger = self._setup_logger(log_level)

        # Initialize sub-classes
        self.token_manager = self.TokenManager(username, password, api_key, self.logger)
        self.message_sender = None  # Will be initialized after token is generated
        self.token = None

    def _setup_logger(self, level):
        logger = logging.getLogger("TradeUnifox")
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                                          datefmt="%Y-%m-%d %H:%M:%S")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.setLevel(level)
        return logger

    def generate_token(self):
        self.token = self.token_manager.generate_token()
        # Initialize message sender after token is generated
        self.message_sender = self.MessageSender(self.username, self.token, self.api_key, self.logger)

    def send_message(self, to: str, message: str):
        if not self.message_sender:
            raise ValueError("Token not generated. Call generate_token() first.")
        return self.message_sender.send_message(to, message)

    def __str__(self):
        display_token = self.token if self.token else "not set"
        return f"username={self.username}\ntoken={display_token}"
