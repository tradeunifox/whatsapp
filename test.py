# test_tradeunifox.py

try:
    import tradeunifox.whatsapp as w
except ModuleNotFoundError:
    print("❌ tradeunifox module not found. Check if wheel is installed correctly.")
    exit(1)

print("✅ tradeunifox module imported successfully!")
print("Available classes/functions in whatsapp module:")
print(dir(w))

# Optional: test creating an object
try:
    sender = w.MessageSender(username="ssc", token="YOUR_TOKEN")
    print("✅ MessageSender class works:", sender)
except Exception as e:
    print("⚠️ Could not initialize MessageSender:", e)
