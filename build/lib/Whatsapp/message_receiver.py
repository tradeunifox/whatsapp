import requests
import logging
import sys
import time
import json
from typing import Dict, List, Any, Optional


class MessageReceiver:
    """Handles receiving WhatsApp messages using TradeUnifox"""

    BASE_URL = "https://whatsapp.tradeunifox.com/api"

    def __init__(self, username: str, token: str, api_key: str, log_level=logging.INFO):
        self.username = username
        self.token = token
        self.api_key = api_key
        self.logger = self._setup_logger(log_level)
        self.last_message_id = None  # अंतिम मैसेज ID को ट्रैक करने के लिए

    def _setup_logger(self, level):
        logger = logging.getLogger("TradeUnifoxReceiver")
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                                          datefmt="%Y-%m-%d %H:%M:%S")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.setLevel(level)
        return logger

    def receive_messages(self, limit: int = 10, mark_as_read: bool = False) -> Dict[str, Any]:
        """
        Fetch incoming WhatsApp messages

        Args:
            limit: Maximum number of messages to fetch (default: 10)
            mark_as_read: Whether to mark fetched messages as read (default: False)

        Returns:
            Dict containing messages and metadata
        """
        url = f"{self.BASE_URL}/receive"

        try:
            self.logger.info("Fetching incoming messages...")

            # Prepare request parameters
            params = {
                "api_key": self.api_key,
                "limit": limit
            }

            # अगर अंतिम मैसेज ID है, तो उसे पैरामीटर में जोड़ें
            if self.last_message_id:
                params["after"] = self.last_message_id

            # अगर मैसेज को पढ़े हुए मार्क करना है, तो पैरामीटर जोड़ें
            if mark_as_read:
                params["mark_read"] = "true"

            # अधिकृत समय के लिए टाइमआउट सेट करें
            timeout = 30  # 30 सेकंड

            response = requests.get(
                url,
                auth=(self.username, self.token),
                params=params,
                timeout=timeout
            )
            response.raise_for_status()
            data = response.json()

            messages = data.get('messages', [])
            self.logger.info(f"Received {len(messages)} messages")

            # अंतिम मैसेज ID को अपडेट करें (यदि कोई मैसेज मिला है)
            if messages and len(messages) > 0:
                # सबसे हालिया मैसेज का ID प्राप्त करें (मान लें कि मैसेज समय के अनुसार क्रमबद्ध हैं)
                last_message = messages[0]  # पहला मैसेज सबसे हालिया होता है
                self.last_message_id = last_message.get('id')
                self.logger.info(f"Updated last message ID to: {self.last_message_id}")

            return data
        except requests.exceptions.Timeout:
            self.logger.error("Request timed out while fetching messages")
            return {"messages": [], "error": "timeout"}
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error while fetching messages: {e}")
            # डिटेल्ड एरर लॉग करें
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    self.logger.error(f"Server response: {json.dumps(error_data)}")
                except:
                    self.logger.error(f"Server response: {e.response.text}")
            return {"messages": [], "error": f"HTTP Error: {e}"}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to receive messages: {e}")
            return {"messages": [], "error": str(e)}

    def get_unread_count(self) -> int:
        """
        Get count of unread messages

        Returns:
            Number of unread messages
        """
        try:
            self.logger.info("Checking unread message count...")
            url = f"{self.BASE_URL}/unread-count"

            response = requests.get(
                url,
                auth=(self.username, self.token),
                params={"api_key": self.api_key},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            count = data.get('count', 0)
            self.logger.info(f"Unread message count: {count}")
            return count
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get unread count: {e}")
            return 0

    def mark_messages_as_read(self, message_ids: List[str] = None) -> Dict[str, Any]:
        """
        Mark messages as read

        Args:
            message_ids: List of message IDs to mark as read. If None, all unread messages will be marked as read.

        Returns:
            Dict containing operation result
        """
        try:
            self.logger.info("Marking messages as read...")
            url = f"{self.BASE_URL}/mark-read"

            params = {"api_key": self.api_key}

            # यदि विशिष्ट मैसेज IDs दिए गए हैं, तो उन्हें पैरामीटर में जोड़ें
            if message_ids:
                params["message_ids"] = ",".join(message_ids)

            response = requests.post(
                url,
                auth=(self.username, self.token),
                params=params,
                timeout=15
            )
            response.raise_for_status()
            data = response.json()

            self.logger.info(f"Marked messages as read: {data.get('marked_count', 0)}")
            return data
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to mark messages as read: {e}")
            return {"error": str(e)}

    def start_polling(self, callback, interval_seconds: int = 5, limit: int = 10):
        """
        Start polling for new messages at regular intervals

        Args:
            callback: Function to call when new messages are received
            interval_seconds: Polling interval in seconds (default: 5)
            limit: Maximum number of messages to fetch in each poll (default: 10)
        """
        self.logger.info(f"Starting message polling with {interval_seconds} seconds interval")

        def poll():
            try:
                messages_data = self.receive_messages(limit=limit, mark_as_read=False)
                messages = messages_data.get('messages', [])

                if messages:
                    self.logger.info(f"Found {len(messages)} new messages")
                    callback(messages)
                else:
                    self.logger.debug("No new messages found")

                # अगली पोलिंग को शेड्यूल करें
                threading.Timer(interval_seconds, poll).start()
            except Exception as e:
                self.logger.error(f"Error in polling: {e}")
                # त्रुटि होने पर भी पोलिंग जारी रखें
                threading.Timer(interval_seconds, poll).start()

        import threading
        # पहली पोलिंग शुरू करें
        threading.Timer(0, poll).start()

    def stop_polling(self):
        """
        Stop message polling (Note: This is a placeholder as actual implementation
        would require tracking the timer reference)
        """
        self.logger.info("Message polling stopped")
        # वास्तविक रूप से, आपको पोलिंग टाइमर को ट्रैक करने की आवश्यकता होगी
        # यह एक सरली कार्यान्वयन है और एक वास्तविक टाइमर ट्रैकिंग सिस्टम की आवश्यकता होगी

    def get_message_by_id(self, message_id: str) -> Dict[str, Any]:
        """
        Get a specific message by its ID

        Args:
            message_id: The ID of the message to retrieve

        Returns:
            Dict containing message data
        """
        try:
            self.logger.info(f"Fetching message with ID: {message_id}")
            url = f"{self.BASE_URL}/message/{message_id}"

            response = requests.get(
                url,
                auth=(self.username, self.token),
                params={"api_key": self.api_key},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            self.logger.info(f"Retrieved message: {data.get('body', 'No content')[:50]}...")
            return data
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get message by ID: {e}")
            return {"error": str(e)}

    def debug_connection(self) -> Dict[str, Any]:
        """
        Debug connection by testing API endpoints

        Returns:
            Dict containing debug information
        """
        debug_info = {
            "username": self.username,
            "token_length": len(self.token) if self.token else 0,
            "api_key_length": len(self.api_key) if self.api_key else 0,
            "base_url": self.BASE_URL
        }

        try:
            # Test basic connectivity
            self.logger.info("Testing API connectivity...")
            test_url = f"{self.BASE_URL}/status"
            response = requests.get(test_url, timeout=5)
            debug_info["status_code"] = response.status_code
            debug_info["status_response"] = response.text[:100]  # पहले 100 कैरेक्टर
            self.logger.info(f"API connectivity test successful: {response.status_code}")
        except Exception as e:
            debug_info["connectivity_error"] = str(e)
            self.logger.error(f"API connectivity test failed: {e}")

        return debug_info


