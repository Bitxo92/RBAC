from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models
from .. import crud, schemas
from ..dependencies import get_db, require_role, get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=schemas.UserRead, summary="Create user (register)")
def register_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_username(db, payload.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    user = crud.create_user(db, payload.username, payload.email, payload.password, role_name="user")
    return user

@router.get("/me", response_model=schemas.UserRead)
def read_current_user(current_user = Depends(get_current_user)):
    return current_user

@router.get("/", response_model=List[schemas.UserRead], dependencies=[Depends(require_role("admin"))])
def list_users(db: Session = Depends(get_db)):
    from .. import models
    users = db.query(models.User).all()
    return users

@router.post("/{user_id}/roles/{role_name}", dependencies=[Depends(require_role("admin"))])
def assign_role_to_user(user_id: int, role_name: str, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
 
    role = db.query(models.Role).filter(models.Role.name == role_name).first()
 

    user.role = role
    db.add(user)
    db.commit()
    return {"message": f"Role {role_name} assigned to {user.username}"}
