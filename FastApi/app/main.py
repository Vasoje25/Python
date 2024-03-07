#imoprting library
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

#creating class and testing fields in same time
#testing existance and type of fiels
class Post(BaseModel):
    title: str
    content: str
    published: bool = True

#connection with database
try:
    conn= psycopg2.connect(host='localhost', database='fastapi', user='postgres', 
                           password='pgadmin4', cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print("Database connection was succesfull!")
except Exception as error:
    print("Connecting to database failed")
    print("Error: ", error)

#hard-coded data for testing get requests
my_posts = [{"title": "title of post 1", "content": "contentn of pos 1", "id": 1}, {
    "title":"favourites foods", "content": "i like pizza", "id": 2}]

#find post function
def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p
        
#finding a index
def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i
        

#creating a live app over:  uvicorn main:app
#("/") is root path goes after domain
#request Get method from root (url) "/"
@app.get("/")
async def root():
    return {"message": "Hello my api World!"}


#app.get for getting data from host /posts
@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts;""")
    posts= cursor.fetchall()
    return{"data": posts}


#creating post and sending data
#creating body and calling class
# title str, content str
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute("""INSERT INTO posts (title, content, published) 
                   VALUES (%s, %s, %s) RETURNING *; """, (post.title, post.content, post.published))
    new_post = cursor.fetchone()

    #commiting changes into table
    conn.commit()

    return{"data": new_post}


#function for geting single post
#getting ID of type and coverting it to int
#since we are getting STR type
@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
    post = cursor.fetchone()
    
    #Error chache if there is no post with specific ID
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"post with id: {id} was not found")
        #2nd way of showing error code
        #response.status_code = status.HTTP_404_NOT_FOUND
        #return {"message": f"Post with {id} was not found."}

    return {"post_detail": post}


#finction for geting latest post
#this function have to be in order above any
#function that goes with host posts/<something>
@app.get("/posts/latest")
def get_latest_post():
    post = my_posts[len(my_posts)-1]
    return{"detail": post}


#deleting a post
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):

    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *;""", (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit() 

    #finding the Index in array that has requited ID
    #my_posts.pop(index)
    
    #making sure that error dont occure if there is no required ID
    #if index == None:
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with that id {id} does not exist")

    #my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


#updateing post
#getting all data from the front end
@app.put("/posts/{id}")
def update_post(id: int, post: Post):

    cursor.execute("""UPDATE posts SET title = %s, content= %s, published=%s WHERE id= %s RETURNING *; """,
                   (post.title, post.content, post.published, str(id)))
    
    updated_post = cursor.fetchone()
    conn.commit()
    
    #making sure that error dont occure if there is no required ID
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with that id {id} does not exist")

    return {"data": updated_post}



