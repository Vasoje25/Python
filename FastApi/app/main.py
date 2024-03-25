import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
#from . import models
#from .database import engine
from .routers import post, user, auth, vote, image
from .config import settings

print(settings.database_username)

# creating all models (before alembic)
# models.Base.metadata.create_all(bind=engine)


# defaine main word for FastAPI
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)
app.include_router(image.router)



# creating a live app over:  uvicorn main:app
# ("/") is root path goes after domain
# request Get method from root (url) "/"
@app.get("/")
async def root():
    return {"message": "Hello my api World!"}



