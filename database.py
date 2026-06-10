import asyncio
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.id import ID
from config import *

# ===== CLIENT SETUP =====
client = Client()
client.set_endpoint(APPWRITE_ENDPOINT)
client.set_project(APPWRITE_PROJECT_ID)
client.set_key(APPWRITE_API_KEY)

db = Databases(client)

def _run(coro):
    """Sync wrapper for Appwrite SDK (sync SDK)"""
    return coro

# ===== USER FUNCTIONS =====
def get_user(user_id: int):
    try:
        result = db.list_documents(
            APPWRITE_DATABASE_ID, COLLECTION_USERS,
            queries=[Query.equal("user_id", user_id)]
        )
        docs = result["documents"]
        return docs[0] if docs else None
    except:
        return None

def create_user(user_id: int, username: str, full_name: str, referred_by=None):
    try:
        existing = get_user(user_id)
        if existing:
            return existing
        data = {
            "user_id": user_id,
            "username": username or "",
            "full_name": full_name or "",
            "credits": REGISTER_CREDITS,
            "registered": True
        }
        if referred_by:
            data["referred_by"] = referred_by
        return db.create_document(APPWRITE_DATABASE_ID, COLLECTION_USERS, ID.unique(), data)
    except Exception as e:
        print(f"create_user error: {e}")
        return None

def add_credits(user_id: int, amount: int):
    try:
        user = get_user(user_id)
        if user:
            new_credits = user["credits"] + amount
            db.update_document(APPWRITE_DATABASE_ID, COLLECTION_USERS, user["$id"], {"credits": new_credits})
    except Exception as e:
        print(f"add_credits error: {e}")

def deduct_credits(user_id: int, amount: int):
    try:
        user = get_user(user_id)
        if user:
            new_credits = max(0, user["credits"] - amount)
            db.update_document(APPWRITE_DATABASE_ID, COLLECTION_USERS, user["$id"], {"credits": new_credits})
    except Exception as e:
        print(f"deduct_credits error: {e}")

def get_user_keys(user_id: int):
    try:
        result = db.list_documents(
            APPWRITE_DATABASE_ID, COLLECTION_KEYS,
            queries=[Query.equal("user_id", user_id), Query.limit(20)]
        )
        return result["documents"]
    except:
        return []

def save_key(user_id: int, key_type: str, key_value: str):
    try:
        db.create_document(APPWRITE_DATABASE_ID, COLLECTION_KEYS, ID.unique(), {
            "user_id": user_id,
            "key_type": key_type,
            "key_value": key_value
        })
    except Exception as e:
        print(f"save_key error: {e}")

# ===== KEY POOL =====
def get_outline_key():
    try:
        result = db.list_documents(
            APPWRITE_DATABASE_ID, COLLECTION_OUTLINE_POOL,
            queries=[Query.equal("is_used", False), Query.limit(1)]
        )
        docs = result["documents"]
        if docs:
            doc = docs[0]
            db.update_document(APPWRITE_DATABASE_ID, COLLECTION_OUTLINE_POOL, doc["$id"], {"is_used": True})
            return doc["key_value"]
        return None
    except Exception as e:
        print(f"get_outline_key error: {e}")
        return None

def get_v2ray_key():
    try:
        result = db.list_documents(
            APPWRITE_DATABASE_ID, COLLECTION_V2RAY_POOL,
            queries=[Query.equal("is_used", False), Query.limit(1)]
        )
        docs = result["documents"]
        if docs:
            doc = docs[0]
            db.update_document(APPWRITE_DATABASE_ID, COLLECTION_V2RAY_POOL, doc["$id"], {"is_used": True})
            return doc["key_value"]
        return None
    except Exception as e:
        print(f"get_v2ray_key error: {e}")
        return None

def add_outline_key(key_value: str):
    try:
        db.create_document(APPWRITE_DATABASE_ID, COLLECTION_OUTLINE_POOL, ID.unique(), {
            "key_value": key_value,
            "is_used": False
        })
    except Exception as e:
        print(f"add_outline_key error: {e}")

def add_v2ray_key(key_value: str):
    try:
        db.create_document(APPWRITE_DATABASE_ID, COLLECTION_V2RAY_POOL, ID.unique(), {
            "key_value": key_value,
            "is_used": False
        })
    except Exception as e:
        print(f"add_v2ray_key error: {e}")

def count_keys():
    try:
        outline = db.list_documents(
            APPWRITE_DATABASE_ID, COLLECTION_OUTLINE_POOL,
            queries=[Query.equal("is_used", False)]
        )["total"]
        v2ray = db.list_documents(
            APPWRITE_DATABASE_ID, COLLECTION_V2RAY_POOL,
            queries=[Query.equal("is_used", False)]
        )["total"]
        return outline, v2ray
    except:
        return 0, 0

def count_users():
    try:
        result = db.list_documents(APPWRITE_DATABASE_ID, COLLECTION_USERS)
        return result["total"]
    except:
        return 0

def get_all_users():
    try:
        result = db.list_documents(
            APPWRITE_DATABASE_ID, COLLECTION_USERS,
            queries=[Query.limit(500)]
        )
        return result["documents"]
    except:
        return []

# ===== CREDIT REQUESTS =====
def create_credit_request(user_id: int, amount: int):
    try:
        db.create_document(APPWRITE_DATABASE_ID, COLLECTION_CREDIT_REQUESTS, ID.unique(), {
            "user_id": user_id,
            "amount": amount,
            "status": "pending"
        })
    except Exception as e:
        print(f"create_credit_request error: {e}")

def get_pending_requests():
    try:
        result = db.list_documents(
            APPWRITE_DATABASE_ID, COLLECTION_CREDIT_REQUESTS,
            queries=[Query.equal("status", "pending")]
        )
        return result["documents"]
    except:
        return []

def approve_credit_request(doc_id: str):
    try:
        doc = db.get_document(APPWRITE_DATABASE_ID, COLLECTION_CREDIT_REQUESTS, doc_id)
        user_id = doc["user_id"]
        amount = doc["amount"]
        add_credits(user_id, amount)
        db.update_document(APPWRITE_DATABASE_ID, COLLECTION_CREDIT_REQUESTS, doc_id, {"status": "approved"})
        return user_id, amount
    except Exception as e:
        print(f"approve_credit_request error: {e}")
        return None, None

def reject_credit_request(doc_id: str):
    try:
        db.update_document(APPWRITE_DATABASE_ID, COLLECTION_CREDIT_REQUESTS, doc_id, {"status": "rejected"})
    except Exception as e:
        print(f"reject_credit_request error: {e}")
