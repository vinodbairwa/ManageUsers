from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import mysql.connector
import redis
import os
import pymysql

# DATABASE_URL = 'mysql+mysqlconnector://root:vinod@localhost/xyz'

# engine = create_engine(DATABASE_URL)


engine = create_engine('mysql+pymysql://root:vinod@localhost/xyz')
connection = engine.connect()
print("Connected to the database successfully!")
connection.close()

SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db. close()
 

# redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)
