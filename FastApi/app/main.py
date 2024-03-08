# imoprting library
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from . import models
from .database import engine, get_db
from sqlalchemy.orm import Session


#creating all models
models.Base.metadata.create_all(bind=engine)


app = FastAPI()



# creating class and testing fields in same time
# testing existance and type of fiels
class Post(BaseModel):
    title: str
    content: str
    published: bool = True


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


# Test gitting data from database over library
@app.get("/sqlalchemy")
def get_tests(db: Session = Depends(get_db)):

    posts= db.query(models.Post).all()
    return {"data": posts}


# app.get for getting data from host /posts
@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts;""")
    # posts = cursor.fetchall()
    posts= db.query(models.Post).all()
    return {"data": posts}


# creating post and sending data
# creating body and calling class
# title str, content str
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post, db: Session = Depends(get_db)):
    # cursor.execute(
    #     """INSERT INTO posts (title, content, published) 
    #                VALUES (%s, %s, %s) RETURNING *; """,
    #     (post.title, post.content, post.published),
    # )
    # new_post = cursor.fetchone()

    # # commiting changes into table
    # conn.commit()
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return {"data": new_post}


# app.get for getting data from host /posts
@app.get("/posts/latest")
def get_post():
    cursor.execute("""SELECT * FROM posts ORDER BY created_at DESC;""")
    posts = cursor.fetchone()
    return {"data": posts}


# function for geting single post
# getting ID of type and coverting it to int
# since we are getting STR type
@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):

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

    return {"post_detail": id_post}


# deleting a post
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):

    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with that id {id} does not exist")    

    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


#TODO nastaviti u ponedeljak 5:25:31
# updateing post
# getting all data from the front end
@app.put("/posts/{id}")
def update_post(id: int, post: Post, db: Session = Depends(get_db)):

    # cursor.execute(
    #     """UPDATE posts SET title = %s, content= %s, published=%s WHERE id= %s RETURNING *; """,
    #     (post.title, post.content, post.published, str(id)),
    # )

    # updated_post = cursor.fetchone()
    # conn.commit()

    post_querry = db.query(models.Post).filter(models.Post.id == id)
    post= post_querry.first()

    # making sure that error dont occure if there is no required ID
    if post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with that id {id} does not exist",
        )
    
    post_querry.update(post.model_dump() , synchronize_session=False)
    db.commit()

    return {"data": post_querry.first()}


# updateing post over patch
# getting all data from the front end
@app.patch("/posts/{id}")
def update_post_patch(id: int, post: Post):

    cursor.execute(
        """UPDATE posts SET title = %s, content= %s, published=%s WHERE id= %s RETURNING *; """,
        (post.title, post.content, post.published, str(id)),
    )

    patch_updated_post = cursor.fetchone()
    conn.commit()

    # making sure that error dont occure if there is no required ID
    if post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with that id {id} does not exist",
        )

    return {"data": patch_updated_post}

