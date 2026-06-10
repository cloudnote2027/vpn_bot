import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT")
APPWRITE_PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID")
APPWRITE_API_KEY = os.getenv("APPWRITE_API_KEY")
APPWRITE_DATABASE_ID = os.getenv("APPWRITE_DATABASE_ID")

COLLECTION_USERS = "users"
COLLECTION_KEYS = "keys"
COLLECTION_OUTLINE_POOL = "outline_pool"
COLLECTION_V2RAY_POOL = "v2ray_pool"
COLLECTION_CREDIT_REQUESTS = "credit_requests"

REGISTER_CREDITS = int(os.getenv("REGISTER_CREDITS", 1))      # 1 credit for new user
REFER_CREDITS = int(os.getenv("REFER_CREDITS", 10))
OUTLINE_KEY_COST = int(os.getenv("OUTLINE_KEY_COST", 5))
V2RAY_KEY_COST = int(os.getenv("V2RAY_KEY_COST", 8))

SERVER_NAME = os.getenv("SERVER_NAME", "Lord Kazuma VPN")
SERVER_LOCATION = os.getenv("SERVER_LOCATION", "Singapore")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/yourchannel")

# Static refer base URL (without ?start=...)
REFER_BASE_URL = "https://t.me/bug303"
