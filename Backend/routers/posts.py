from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..dependencies import get_db, require_role, get_current_user, is_admin_or_owner

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/", response_model=schemas.PostRead, dependencies=[Depends(require_role("author","admin"))])
def create_post(payload: schemas.PostCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return crud.create_post(db, current_user, payload.title, payload.content)

@router.get("/", response_model=List[schemas.PostRead])
def list_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_posts(db, skip=skip, limit=limit)

@router.get("/{post_id}", response_model=schemas.PostRead)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.put("/{post_id}", response_model=schemas.PostRead)
def update_post(post_id: int, payload: schemas.PostCreate, ctx: dict = Depends(is_admin_or_owner), db: Session = Depends(get_db)):
    post = ctx["post"]
    return crud.update_post(db, post, payload.title, payload.content)

@router.delete("/{post_id}")
def delete_post(post_id: int, ctx: dict = Depends(is_admin_or_owner), db: Session = Depends(get_db)):
    post = ctx["post"]
    crud.delete_post(db, post)
    return {"detail": "Post deleted"}
