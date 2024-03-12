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


# creating a live app over:  uvicorn main:app
# ("/") is root path goes after domain
# request Get method from root (url) "/"
@app.get("/")
async def root():
    return {"message": "Hello my api World!"}


# app.get for getting data from host /posts
@app.get("/posts", response_model= List[schemas.PostResponse])
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts;""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return posts


# creating post and sending data
# creating body and calling class
# title str, content str
@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model= schemas.PostResponse)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):

    # # commiting changes into table
    # conn.commit()
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


#get latest post
@app.get("/posts/latest", response_model=schemas.PostResponse)
def latest_post(db: Session = Depends(get_db)):

    post_query = db.query(models.Post).order_by(models.Post.id.desc()).first()

    if post_query == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="there is no any posts!"
        )

    return post_query


# function for geting single post
# getting ID of type and coverting it to int
# since we are getting STR type
@app.get('/posts/{id}')
def get_post(id: int, db: Session = Depends(get_db)):

    #id_post = db.query(models.Post.title.__dict__).filter(models.Post.id == id).first()
    id_post = db.query(models.Post).filter(models.Post.id == id).first()

    # Error chache if there is no post with specific ID
    if not id_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )
        # 2nd way of showing error code
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"Post with {id} was not found."}
    print(id_post)
    return id_post


# deleting a post
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post_delete = post_query.first()

    if post_delete == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with that id {id} does not exist",
        )

    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# updateing post
# getting all data from the front end
@app.put("/posts/{id}", response_model= schemas.PostResponse)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post_update = post_query.first()

    # making sure that error dont occure if there is no required ID
    if post_update == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with that id {id} does not exist",
        )

    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()

    return post_query.first()


# updateing post over patch
# getting all data from the front end
@app.patch("/posts/{id}", response_model= schemas.PostResponse)
def update_post_patch(id: int, post_patch: schemas.PostCreate, db: Session = Depends(get_db)):

    post_query = db.query(models.Post).filter(models.Post.id == id)
    patch_post = post_query.first()

    # making sure that error dont occure if there is no required ID
    if patch_post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with that id {id} does not exist",
        )

    post_query.update(post_patch.model_dump(), synchronize_session=False)

    db.commit()
    db.refresh(patch_post)

    return patch_post


#creating a new user
@app.post("/users", status_code= status.HTTP_201_CREATED, response_model= schemas.UserOut)
def create_user(user :schemas.UserCreate ,db: Session= Depends(get_db)):

    #hash the password - user.password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user 


@app.get("/users/{id}")
def get_user(id: int, db: Session = Depends(get_db), response_model=schemas.UserOut):
    
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} does not exist")
    
    return user


