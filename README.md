# TradeUnifox WhatsApp Module

This module allows developers to send and receive WhatsApp messages easily using the TradeUnifox API.

---

## 🚀 Features
- Authentication system with auto token refresh  
- Message sending and receiving  
- Logging support  
- Error handling for API and network issues  

---

## 📦 Installation
After building the wheel:
```bash
pip install Tradeunifox-0.0.1-py3-none-any.whl
```

---

## 🔐 Token Manager Example
```python
from Tradeunifox.Whatsapp import TokenManager

USERNAME = "test"
PASSWORD = "123abc"
API_KEY = "API_1234567890"

tm = TokenManager(username=USERNAME, api_key=API_KEY)

# Refresh or generate new token
new_token = tm.refresh_token()
print("✅ New Token:", new_token)
```

---

## 💬 Message Sender Example
```python
from Tradeunifox.Whatsapp import MessageSender

token = "TOKEN_GNVN0ZI83RMmh7o6l9t"

sender = MessageSender(username="test", token=token, api_key="API_1234567890")
response = sender.send_message("919876543210", "Hello! This message is sent via TradeUnifox.")
print(response)
```

---

## 📥 Message Receiver Example
```python
from Tradeunifox.Whatsapp import MessageReceiver

receiver = MessageReceiver(username="test", token="TOKEN_GNVN0ZI83RMmh7o6l9t")

@receiver.on_message
def handle_message(message):
    print("📩 New message received:", message)

receiver.start()
```

---

## 🧾 License
This project is developed and maintained by **Trade Unifox**.  
© 2025 Trade Unifox. All rights reserved.
