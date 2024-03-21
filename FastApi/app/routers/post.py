from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func
from .. import models, schemas, oauth2
from ..database import get_db


router = APIRouter(prefix="/posts", tags=["Posts"])


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
    # cursor.execute("""SELECT * FROM posts;""")
    # posts = cursor.fetchall()
    #posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).all()

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
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    # # commiting changes into table
    # conn.commit()

    print(current_user.id)
    print(current_user.email)
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


# get latest post
@router.get("/latest", response_model=schemas.PostOut)
def latest_post(
    db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)
):

    #post_query = db.query(models.Post).order_by(models.Post.id.desc()).first()

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

    # id_post = db.query(models.Post.title.__dict__).filter(models.Post.id == id).first()
    #id_post = db.query(models.Post).filter(models.Post.id == id).first()

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
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post_update = post_query.first()

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
    db.commit()

    return post_query.first()


# updateing post over patch
# getting all data from the front end
@router.patch("/{id}", response_model=schemas.PostResponse)
def update_post_patch(
    id: int,
    post_patch: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    post_query = db.query(models.Post).filter(models.Post.id == id)
    patch_post = post_query.first()

    # making sure that error dont occure if there is no required ID
    if patch_post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with that id {id} does not exist",
        )

    if patch_post.owner_id != oauth2.get_current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    post_query.update(post_patch.model_dump(), synchronize_session=False)

    db.commit()
    db.refresh(patch_post)

    return patch_post
