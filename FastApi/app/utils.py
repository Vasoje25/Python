from datetime import datetime, timezone
from passlib.context import CryptContext
from fastapi import File, UploadFile, HTTPException, status



# creating a daefault(what we want to use) algorithm that we want to use (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


#hashing password in database
def hash(password: str):
    return pwd_context.hash(password)


#comparing hashed pass and login password for validation
def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


#receive and save file
def file_write(file: File, destination_path: str):
    url_folder_path="/static/Images/"
    
    image_name = str(datetime.now(timezone.utc).now()) + '_' +file.filename

    file_path = f"{destination_path}{image_name}"

    with open(file_path, "wb") as f:
        f.write(file.file.read())
        image_location_relative_path= f"{url_folder_path}{image_name}"

    return image_location_relative_path

