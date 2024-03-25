import pathlib

from fastapi import FastAPI, Response, requests, status, HTTPException, Depends, APIRouter
from fastapi import File, UploadFile, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import HTTPException

from sqlalchemy.orm import Session
from typing import Annotated, List, Optional

from sqlalchemy import func
from .. import models
from ..database import get_db


router = APIRouter(prefix="/images", tags=["Images"])

image_folder_path="/home/dev-222/FOLDAAA/Praksa/Python/FastApi/static/Images/"
url_folder_path="127.0.0.1:8000/static/Images/"


# creating post and sending data
# creating body and calling class
# title str, content str


@router.post("/upload")
def upload_file(file: UploadFile, db: Session = Depends(get_db),):
    data= file.file
    image_name = file.filename

    print(file)
    print(data)
    try:
        file_path = f"{image_folder_path}{image_name}"
        with open(file_path, "wb") as f:
            f.write(file.file.read())
            create_url= f"{url_folder_path}{image_name}"
            print(create_url)
          

            new_image = models.Image()
            new_image.name = image_name
            new_image.image_url = create_url
            db.add(new_image)
            db.commit()
            db.refresh(new_image)


        return {"message": "File saved successfully"}
    except Exception as e:
        return {"message": e.args}
    

# creating post and sending data
# creating body and calling class
# title str, content str