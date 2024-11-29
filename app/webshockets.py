
import random
from .database import redis_client
import redis
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from typing import List, Dict, Set
from .main import app

# Redis Hash key
hash_key = "subscription_hash"

# Initialize Redis hash with sample data
def initialize_redis_hash():
    redis_client.hset(hash_key, "key1", "value1")
    redis_client.hset(hash_key, "key2", "value2")
    redis_client.hset(hash_key, "key3", "value3")
    redis_client.hset(hash_key, "key4", "value4")

initialize_redis_hash()

# WebSocket Manager to handle active connections
class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[WebSocket, Set[str]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.subscriptions[websocket] = set()

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    def subscribe(self, websocket: WebSocket, keys: Set[str]):
        self.subscriptions[websocket].update(keys)

    def get_subscribers_for_key(self, key: str) -> List[WebSocket]:
        return [ws for ws, keys in self.subscriptions.items() if key in keys]

# Create WebSocketManager instance
manager = WebSocketManager()

# Function to randomly change a key-value pair in the Redis hash
def change_random_value():
    all_keys = redis_client.hkeys(hash_key)
    random_key = random.choice(all_keys)
    new_value = f"new_value_{random.randint(1000, 9999)}"
    redis_client.hset(hash_key, random_key, new_value)
    return random_key.decode(), new_value

# Function to get the current key-value pairs from Redis
def get_all_key_values():
    try:
        return redis_client.hgetall(hash_key)
    except redis.RedisError as e:
        print(f"Error retrieving data from Redis: {e}")
        return {}



# Function to periodically change key-values and notify subscribers
async def periodically_change_values():
    while True:
        # Simulate key-value change and notify relevant subscribers
        try:
            key, new_value = change_random_value()
            # print(f"Changed {key} to {new_value}")

            # Notify only the subscribers of the changed key
            subscribers = manager.get_subscribers_for_key(key)
            for subscriber in subscribers:
                await manager.send_personal_message(
                    json.dumps({key: new_value}), subscriber
                )

        except Exception as e:
            print(f"Error during value update: {e}")
        
        # Wait 1 second before changing again
        await asyncio.sleep(1)

# Start the periodic updates in the background
@app.on_event("startup")
async def start_periodic_updates():
    asyncio.create_task(periodically_change_values())

