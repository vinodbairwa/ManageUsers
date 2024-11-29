# # app/hashing.py
import bcrypt
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # Generate a salt and hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

class Hashing:
    @staticmethod
    # def hash_password(password: str) -> str:
    #     # Hash the password
    #     return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def hash_password(plain_password):
       salt = bcrypt.gensalt()  # Generates a random salt
       hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
       return hashed_password

    
    @staticmethod
    # def verify_password(password: str, hashed_password: str) -> bool:
    #     # Check if the password matches the hashed password
    #     return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def verify_password(plain_password, hashed_password):
       return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)