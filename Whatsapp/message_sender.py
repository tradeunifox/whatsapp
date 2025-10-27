import requests
import logging
import sys

class MessageSender:
    """Handles sending WhatsApp messages using TradeUnifox"""

    BASE_URL = "https://whatsapp.tradeunifox.com/api"

    def __init__(self, username: str, token: str, api_key: str, log_level=logging.INFO):
        self.username = username
        self.token = token
        self.api_key = api_key
        self.logger = self._setup_logger(log_level)

    def _setup_logger(self, level):
        logger = logging.getLogger("TradeUnifoxMsg")
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                                          datefmt="%Y-%m-%d %H:%M:%S")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.setLevel(level)
        return logger

    def send_message(self, to: str, message: str):
        url = f"{self.BASE_URL}/send"
        payload = {
            "to": to,
            "message": message,
            "api_key": self.api_key
        }

        try:
            self.logger.info(f"Sending message to {to}")
            response = requests.post(url, auth=(self.username, self.token), json=payload)
            response.raise_for_status()
            self.logger.info("Message sent successfully")
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to send message: {e}")
            raise
