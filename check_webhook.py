import os
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Check webhook status
url = f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo"
response = requests.get(url)
print("Webhook Info:")
print(response.json())

# Delete webhook if exists
delete_url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook"
delete_response = requests.get(delete_url)
print("\nDelete Webhook Response:")
print(delete_response.json())
