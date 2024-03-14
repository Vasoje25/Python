from fastapi import FastAPI
from .database import engine
from .routers import post, user, auth
from . import models
from .config import settings

print(settings.database_username)

# creating all models
models.Base.metadata.create_all(bind=engine)


# defaine main word for FastAPI
app = FastAPI()


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)


# creating a live app over:  uvicorn main:app
# ("/") is root path goes after domain
# request Get method from root (url) "/"
@app.get("/")
async def root():
    return {"message": "Hello my api World!"}
