# app/crud.py
from sqlalchemy.orm import Session
from .models import User
from . import models, hashing


def get_user_by_username(username: str, db: Session):
    try:
        return db.query(User).filter(User.username == username).first()
    except Exception as e:
        # Handle or log the exception as needed
        return None
      
      
def save_user(user: User, db: Session):
    db.add(user)
    db.commit()
    db.refresh(user)  # Optional: Refresh the instance to get the latest state from the DB


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def update_user_password(db: Session, user: models.User, new_password: str):
    user.password = hashing.hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user




# #######
# def update_user_password(db: Session, user: models.User, hashed_password: str):
#     user.password = hashed_password  # Update the password field
#     db.commit()  # Commit the changes to the database
#     db.refresh(user)  # Refresh the user instance to get the updated data
#     return user
