# from fastapi import FastAPI, Depends, Form, HTTPException, Response
# from fastapi.responses import HTMLResponse
# from fastapi_jwt_auth import AuthJWT
# from fastapi_jwt_auth.exceptions import AuthJWTException
# from pydantic import BaseModel
# import redis
# from requests import Session

# from app import hashing
# from app.database import get_db
# from .models import User
# # from jwt import SomeModuleOrFunction
# from fastapi.responses import JSONResponse
# # Initialize FastAPI app
# app = FastAPI()

# # Initialize Redis
# redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# # Settings for JWT
# class Settings(BaseModel):
#     authjwt_secret_key: str = "your-secret-key"
#     authjwt_access_token_expires: int = 3600  # 1 hour
#     authjwt_refresh_token_expires: int = 86400  # 24 hours

# @AuthJWT.load_config
# def get_config():
#     return Settings()


# @app.post("/login/",response_class= HTMLResponse)
# def login(
#     response: Response,
#     username: str = Form(...),
#     password: str = Form(...),
#     db: Session = Depends(get_db),
#     Authorize: AuthJWT = Depends()
# ):
#     db_user = db.query(User).filter(User.username == username).first()

#     # Check if db_user exists
#     if not db_user:
#         raise HTTPException(status_code=400, detail="User not found")

#     # Verify password (replace with your hashing logic)
#     if not hashing.verify_password(password, db_user.password):
#         raise HTTPException(status_code=400, detail="Invalid credentials")


#     # Create the JWT token
#     access_token = Authorize.create_access_token(subject=db_user.username)
#     if not access_token:
#         raise HTTPException(status_code=500, detail="Token creation failed")
    
#     refresh_token = Authorize.create_refresh_token(subject=db_user.username)
#       # Store refresh token in Redis with expiration
#     redis_client.set(f"refresh_token:{db_user.username}", refresh_token, ex=Settings().authjwt_refresh_token_expires)
    
#     return JSONResponse(content={"access_token": access_token, "refresh_token": refresh_token})
# # Refresh token route
# @app.post("/refresh")
# def refresh(Authorize: AuthJWT = Depends()):
#     try:
#         # Check if the refresh token is valid
#         Authorize.jwt_refresh_token_required()
#         current_user = Authorize.get_jwt_subject()
        
#         # Retrieve refresh token from Redis
#         redis_token = redis_client.get(f"refresh_token:{current_user}")
#         if not redis_token or redis_token != Authorize.get_raw_jwt()["jti"]:
#             raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
        
#         # Create a new access token
#         new_access_token = Authorize.create_access_token(subject=current_user)
#         return {"access_token": new_access_token}
#     except AuthJWTException as e:
#         raise HTTPException(status_code=401, detail=str(e))

# # Protect route with JWT
# @app.get("/protected")
# def protected(Authorize: AuthJWT = Depends()):
#     try:
#         Authorize.jwt_required()
#         current_user = Authorize.get_jwt_subject()
#         return {"message": f"Hello {current_user}"}
#     except AuthJWTException as e:
#         raise HTTPException(status_code=401, detail=str(e))









import random
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List, Dict, Set
from .database import redis_client  # Ensure this import is correct
import redis

app  = FastAPI()
# Redis Hash key
hash_key = "subscription_hash"

# Initialize Redis hash with sample data only if needed
def initialize_redis_hash():
    # Use a conditional to avoid re-initializing
    if not redis_client.hgetall(hash_key):
        redis_client.hset(hash_key, "key1", "value1")
        redis_client.hset(hash_key, "key2", "value2")
        redis_client.hset(hash_key, "key3", "value3")
        redis_client.hset(hash_key, "key4", "value4")

initialize_redis_hash()

# WebSocket Manager class to manage connections and subscriptions
class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[WebSocket, Set[str]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.subscriptions[websocket] = set()

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    def subscribe(self, websocket: WebSocket, keys: Set[str]):
        self.subscriptions[websocket].update(keys)

    def get_subscribers_for_key(self, key: str) -> List[WebSocket]:
        return [ws for ws, keys in self.subscriptions.items() if key in keys]

# Create an instance of WebSocketManager
manager = WebSocketManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send all available keys to the client on connection
        all_keys = get_all_key_values()
        key_value_pairs = {key.decode(): value.decode() for key, value in all_keys.items()}
        await manager.send_personal_message(json.dumps(key_value_pairs), websocket)

        while True:
            message = await websocket.receive_text()
            print(f"Received message: {message}")

            if message.startswith("subscribe:"):
                try:
                    keys = json.loads(message[len("subscribe:"):].strip())
                    if isinstance(keys, list):
                        manager.subscribe(websocket, set(keys))
                        await manager.send_personal_message(f"Subscribed to keys: {', '.join(keys)}", websocket)
                        print(f"WebSocket subscribed to keys: {keys}")
                    else:
                        await manager.send_personal_message("Invalid subscription format", websocket)
                except json.JSONDecodeError:
                    await manager.send_personal_message("Invalid JSON format for subscription", websocket)
                    print(f"Invalid subscription message received: {message}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")

# Function to randomly change a key-value pair in the Redis hash
def change_random_value():
    try:
        all_keys = redis_client.hkeys(hash_key)
        if not all_keys:
            return None, None  # No keys available
        random_key = random.choice(all_keys)
        new_value = f"new_value_{random.randint(1000, 9999)}"
        redis_client.hset(hash_key, random_key, new_value)
        return random_key.decode(), new_value
    except redis.RedisError as e:
        print(f"Redis error while changing value: {e}")
        return None, None

# Function to get all key-value pairs from Redis
def get_all_key_values():
    try:
        return redis_client.hgetall(hash_key)
    except redis.RedisError as e:
        print(f"Error retrieving data from Redis: {e}")
        return {}

# Background task to periodically change Redis values and notify subscribers
async def periodically_change_values():
    while True:
        try:
            key, new_value = change_random_value()
            if key and new_value:
                subscribers = manager.get_subscribers_for_key(key)
                for subscriber in subscribers:
                    await manager.send_personal_message(
                        json.dumps({key: new_value}), subscriber
                    )
        except Exception as e:
            print(f"Error during value update: {e}")
        
        await asyncio.sleep(1)

@app.on_event("startup")
async def start_periodic_updates():
    asyncio.create_task(periodically_change_values())
