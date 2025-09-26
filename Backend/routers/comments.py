from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas
from ..dependencies import get_db, require_role, get_current_user

router = APIRouter(prefix="/posts/{post_id}/comments", tags=["comments"])

@router.get("/", response_model=List[schemas.CommentRead])
def list_comments(post_id: int, db: Session = Depends(get_db)):
    return crud.list_comments_for_post(db, post_id)


@router.post("/", response_model=schemas.CommentRead, dependencies=[Depends(require_role("author","admin"))])
def create_comment(post_id: int, payload: schemas.CommentCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    post = crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return crud.create_comment(db, post, payload.content, author=current_user)
