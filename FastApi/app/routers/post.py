import os
from fastapi import FastAPI, File, Response, UploadFile, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional, Dict

from alembic import op
import sqlalchemy as sa

from sqlalchemy import func
from .. import models, schemas, oauth2, utils
from ..database import get_db


router = APIRouter(prefix="/posts", tags=["Posts"])
image_folder_path="/home/dev-222/FOLDAAA/Praksa/Python/FastApi/static/Images/"


# app.get for getting data from host /posts
@router.get("/", response_model=List[schemas.PostOut])
#@router.get("/")
def get_posts(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):
    posts = db.query(models.Post,  func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
        models.Post.title.contains(search)).limit(limit).all()

    return posts


# creating post and sending data
# creating body and calling class
# title str, content str
@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse
)
def create_posts(
    file: UploadFile= File(None),
    post: schemas.PostCreate = Depends(),
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    print(current_user.id)
    print(current_user.email)
    
    url=None
    #check if file exist and format of it
    if file:
        if utils.is_file_type_valid(file) == True:
            url=utils.file_write(file,image_folder_path)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported media!")
            
    #write data in data base
    try:                   
        new_post = models.Post(owner_id=current_user.id, **post.model_dump())
        new_post.image_url = url

        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        
        return new_post
    except Exception as e:
        print(e.args)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="post is not created")










#===========================================================================================
@router.post(
    "/test/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse
)
def create_posts(
    files: list[UploadFile]= File(None),
    post: schemas.PostCreate = Depends(),
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    # print(current_user.id)
    # print(current_user.email)
    
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(new_post)

    db.commit()
    # get_post_id = db.query(models.Post).group_by(models.Post.id).order_by(models.Post.id.desc()).first()

    images = sa.sql.table('images',
        sa.Column('post_id', sa.Integer, nullable=False),
        sa.Column('image_url', sa.String(), nullable=False),)


    for file in files:
        url=utils.files_write(file,image_folder_path)
        print("======================================")
        print(file.filename)

        new_image = models.Image(post_id=new_post.id, image_url=url)
        #new_image.image_url=url

        new_images = new_image

    image_urls = [{{new_image.post_id}: r[0], {new_image.image_url}: r[1]} for r in new_images]
    op.bulk_insert(images, image_urls)


    db.refresh(new_post)
        
    return new_post
    # except Exception as e:
    #     print(e.args)
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST, detail="post is not created")
#===========================================================================================
#probati resenje sa bulk_insert








# get latest post
@router.get("/latest", response_model=schemas.PostOut)
def latest_post(
    db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)
):

    post_query= db.query(models.Post,  func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).order_by(
        models.Post.id.desc()).first()

    if post_query == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="there is no any posts!"
        )

    return post_query


# function for geting single post
# getting ID of type and coverting it to int
# since we are getting STR type
@router.get("/{id}", response_model=schemas.PostOut)
def get_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    id_post = db.query(models.Post,  func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
        models.Post.id == id).first()

    # Error chache if there is no post with specific ID
    if not id_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )
        # 2nd way of showing error code
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"Post with {id} was not found."}

    return id_post


# deleting a post
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post_delete = post_query.first()

    if post_delete == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with that id {id} does not exist",
        )

    if post_delete.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# updateing post
# getting all data from the front end
@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(
    id: int,
    file: UploadFile = File(None),
    post: schemas.PostCreate=Depends(),
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post_update = post_query.first()

    url=None
    #check if file exist and format of it
    if file:
            if utils.is_file_type_valid(file) == True:
                url=utils.file_write(file,image_folder_path)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported media!")

    # making sure that error dont occure if there is no required ID
    if post_update == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with that id {id} does not exist",
        )

    if post_update.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    post_query.update(post.model_dump(), synchronize_session=False)
    post_update.image_url = url
    db.commit()

    return post_query.first()


# updateing post over patch
# getting all data from the front end
@router.patch("/{id}", response_model=schemas.PostResponse)
def update_post_patch(
    id: int,
    file: UploadFile = File(None),
    post_update: schemas.PatchBase = Depends(),
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    
    post_query = db.query(models.Post).filter(models.Post.id == id)
    returned_post = post_query.first()


    url=None
    #check if file exist and format of it
    if file:
            if utils.is_file_type_valid(file) == True:
                url=utils.file_write(file,image_folder_path)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported media!")


    # making sure that error dont occure if there is no required ID
    if returned_post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with that id {id} does not exist",)

    if returned_post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",)
    

    if post_update.content != None: 
        returned_post.content = post_update.content  

    if post_update.title != None: 
        returned_post.title = post_update.title

    if url != None: 
       returned_post.image_url=url
  

    db.commit()
    db.refresh(returned_post)

    return returned_post
