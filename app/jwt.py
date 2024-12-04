from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Dict, Union
from fastapi import Depends, HTTPException, Request
from app.database import get_db
from .models import User
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from fastapi import HTTPException, Security, status
# from .database import redis_client
from fastapi_jwt_auth.exceptions import AuthJWTException

# OAuth2 scheme to extract token from the request header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Secret key for encoding and decoding JWT
SECRET_KEY = "vinod"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Function to create access token

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

    
class Settings(BaseModel):
    authjwt_secret_key: str = "vinod"
    authjwt_token_location:set= {"headers"}
    authjwt_cookies_secure:bool = False
    authjwt_cookies_csrf_protect:bool = False
    authjwt_access_token_expires: int = 3600  # 1 hour
    authjwt_refresh_token_expires: int = 86400  # 24 hours

@AuthJWT.load_config
def get_config():
    return Settings()
   


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=403, detail="Token is invalid")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")
















# async def validate_token(Authorize: AuthJWT = Depends()):
#     try:
#         # Validate the token using FastAPI-JWT-Auth
#         Authorize.jwt_required()
#         token_subject = Authorize.get_jwt_subject()

#         # Construct the Redis key based on the token subject (e.g., username)
#         redis_key = f"token:{token_subject}"
        
#         # Check if the token exists in Redis
#         if not redis_client.exists(redis_key):
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid or expired token"
#             )
        
#         # Optionally return the subject for further use
#         return token_subject
#     except JWTError as e:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Token validation failed"
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="An unexpected error occurred"
#         )
