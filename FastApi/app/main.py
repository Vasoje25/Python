#imoprting library
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange

app = FastAPI()

#creating class and testing fields in same time
#testing existance and type of fiels
class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int]= None


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
    return{"data": my_posts}


#creating post and sending data
#creating body and calling class
# title str, content str
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict = post.dict()
    post_dict['id']=randrange(0, 1000000)
    my_posts.append(post_dict)
    return{"data": post_dict}

#finction for geting latest post
#this function have to be in order above any
#function that goes with host posts/<something>
@app.get("/posts/latest")
def get_latest_post():
    post = my_posts[len(my_posts)-1]
    return{"detail": post}

#function for geting single post
#getting ID of type and coverting it to int
#since we are getting STR type
@app.get("/posts/{id}")
def get_post(id: int, response: Response):
     
    #print(type(id))

    post = find_post(int(id))
    #Error chache if there is no post with specific ID
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
        #2nd way of showing error code
        #response.status_code = status.HTTP_404_NOT_FOUND
        #return {"message": f"Post with {id} was not found."}

    return {"post_detail": post}

#deleting a post
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    #finding the Index in array that has requited ID
    # my_posts.pop(index)
    index = find_index_post(id)
    
    #making sure that error dont occure if there is no required ID
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with that id {id} does not exist")

    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

#updateing post
@app.put("/posts/{id}")

#getting all data from the front end
def update_post(id: int, post: Post):
    
    index = find_index_post(id)
    
    #making sure that error dont occure if there is no required ID
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with that id {id} does not exist")
    
    #converting data to regular py dict
    post_dict = post.dict()

    #adding ID so final dict have ID in it
    post_dict['id']= id

    #repleacing existing post within index repleacing with new updated post
    my_posts[index] = post_dict
    
    print(post)
    return {"message": "updated post"}



