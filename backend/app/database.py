"""
database.py - MongoDB Connection Manager
=========================================
This file manages our connection to MongoDB using Motor (async driver).

WHY ASYNC (Motor) INSTEAD OF SYNC (PyMongo)?
- FastAPI is built for async programming
- With Motor, while one request waits for MongoDB, other requests can be handled
- This makes our API much faster under load

MOTOR vs PYMONGO:
- PyMongo: db.collection.find_one({"_id": id})  ← blocking
- Motor:  await db.collection.find_one({"_id": id})  ← non-blocking
"""

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

# Global database client — created once, reused for all requests
client: AsyncIOMotorClient = None


async def connect_to_mongo():
    """
    Creates a connection to MongoDB.
    Called when the FastAPI app starts up (see main.py lifespan).
    
    Motor connection pooling: Motor maintains a pool of connections
    so we don't create/destroy a connection for every request.
    """
    global client
    client = AsyncIOMotorClient(settings.mongodb_url)
    
    # Test the connection
    try:
        await client.admin.command('ping')
        print(f"✅ Connected to MongoDB at {settings.mongodb_url}")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        raise


async def close_mongo_connection():
    """
    Closes the MongoDB connection gracefully.
    Called when the FastAPI app shuts down.
    """
    global client
    if client:
        client.close()
        print("📴 MongoDB connection closed")


def get_database():
    """
    Returns the database instance.
    
    Usage in route handlers:
        db = get_database()
        users = await db.users.find_one({"username": "admin"})
    """
    return client[settings.database_name]


def get_collection(collection_name: str):
    """
    Returns a specific collection from the database.
    
    MongoDB Collections ≈ SQL Tables
    
    Usage:
        users_col = get_collection("users")
        resume_col = get_collection("resumes")
    """
    db = get_database()
    return db[collection_name]
