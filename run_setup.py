"""
run_setup.py - ဒီ file ကို တစ်ကြိမ်သာ run ပါ။
Appwrite မှာ collections တွေ အလိုအလျောက် create လုပ်ပေးမည်။
"""
from appwrite.client import Client
from appwrite.services.databases import Databases
from config import *

client = Client()
client.set_endpoint(APPWRITE_ENDPOINT)
client.set_project(APPWRITE_PROJECT_ID)
client.set_key(APPWRITE_API_KEY)

db = Databases(client)

def create_collection_safe(col_id, col_name):
    try:
        db.create_collection(APPWRITE_DATABASE_ID, col_id, col_name)
        print(f"✅ Collection created: {col_name}")
    except Exception as e:
        print(f"⚠️ {col_name} already exists or error: {e}")

def create_attr_safe(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except Exception as e:
        print(f"  ⚠️ Attr skip: {e}")

def setup():
    print("🔧 Setting up Appwrite collections...\n")

    # USERS
    create_collection_safe(COLLECTION_USERS, "Users")
    create_attr_safe(db.create_integer_attribute, APPWRITE_DATABASE_ID, COLLECTION_USERS, "user_id", required=True)
    create_attr_safe(db.create_string_attribute, APPWRITE_DATABASE_ID, COLLECTION_USERS, "username", size=100, required=False)
    create_attr_safe(db.create_string_attribute, APPWRITE_DATABASE_ID, COLLECTION_USERS, "full_name", size=200, required=False)
    create_attr_safe(db.create_integer_attribute, APPWRITE_DATABASE_ID, COLLECTION_USERS, "credits", required=False, default=0)
    create_attr_safe(db.create_integer_attribute, APPWRITE_DATABASE_ID, COLLECTION_USERS, "referred_by", required=False)
    create_attr_safe(db.create_boolean_attribute, APPWRITE_DATABASE_ID, COLLECTION_USERS, "registered", required=False, default=False)

    # KEYS (user ထုတ်ထားသော keys)
    create_collection_safe(COLLECTION_KEYS, "Keys")
    create_attr_safe(db.create_integer_attribute, APPWRITE_DATABASE_ID, COLLECTION_KEYS, "user_id", required=True)
    create_attr_safe(db.create_string_attribute, APPWRITE_DATABASE_ID, COLLECTION_KEYS, "key_type", size=20, required=True)
    create_attr_safe(db.create_string_attribute, APPWRITE_DATABASE_ID, COLLECTION_KEYS, "key_value", size=500, required=True)

    # OUTLINE POOL
    create_collection_safe(COLLECTION_OUTLINE_POOL, "Outline Pool")
    create_attr_safe(db.create_string_attribute, APPWRITE_DATABASE_ID, COLLECTION_OUTLINE_POOL, "key_value", size=500, required=True)
    create_attr_safe(db.create_boolean_attribute, APPWRITE_DATABASE_ID, COLLECTION_OUTLINE_POOL, "is_used", required=False, default=False)

    # V2RAY POOL
    create_collection_safe(COLLECTION_V2RAY_POOL, "V2RAY Pool")
    create_attr_safe(db.create_string_attribute, APPWRITE_DATABASE_ID, COLLECTION_V2RAY_POOL, "key_value", size=500, required=True)
    create_attr_safe(db.create_boolean_attribute, APPWRITE_DATABASE_ID, COLLECTION_V2RAY_POOL, "is_used", required=False, default=False)

    # CREDIT REQUESTS
    create_collection_safe(COLLECTION_CREDIT_REQUESTS, "Credit Requests")
    create_attr_safe(db.create_integer_attribute, APPWRITE_DATABASE_ID, COLLECTION_CREDIT_REQUESTS, "user_id", required=True)
    create_attr_safe(db.create_integer_attribute, APPWRITE_DATABASE_ID, COLLECTION_CREDIT_REQUESTS, "amount", required=True)
    create_attr_safe(db.create_string_attribute, APPWRITE_DATABASE_ID, COLLECTION_CREDIT_REQUESTS, "status", size=20, required=False, default="pending")

    print("\n✅ Setup complete! Now run: python bot.py")

if __name__ == "__main__":
    setup()
