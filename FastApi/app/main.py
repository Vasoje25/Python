# imoprting library
from typing import Optional, List
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from . import models, schemas, utils
from .database import engine, get_db
from sqlalchemy.orm import Session
from datetime import datetime 
from .routers import post, user


# creating all models
models.Base.metadata.create_all(bind=engine)


#defaine main word for FastAPI
app = FastAPI()


# connection with database
try:
    conn = psycopg2.connect(
        host="localhost",
        database="fastapi",
        user="postgres",
        password="pgadmin4",
        cursor_factory=RealDictCursor,
    )
    cursor = conn.cursor()
    print("Database connection was succesfull!")
except Exception as error:
    print("Connecting to database failed")
    print("Error: ", error)


# hard-coded data for testing get requests
my_posts = [
    {"title": "title of post 1", "content": "contentn of pos 1", "id": 1},
    {"title": "favourites foods", "content": "i like pizza", "id": 2},
]


# find post function
def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


# finding a index
def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i


app.include_router(post.router)
app.include_router(user.router)


# creating a live app over:  uvicorn main:app
# ("/") is root path goes after domain
# request Get method from root (url) "/"
@app.get("/")
async def root():
    return {"message": "Hello my api World!"}








