from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from . import database, crud, security, models, schemas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

def require_role(*allowed_roles: str):
    def role_checker(user: models.User = Depends(get_current_user)):
        user_role_name = user.role.name if user.role is not None else None
        if user_role_name is None or user_role_name not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted")
        return user
    return role_checker

def is_admin_or_owner(post_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    post = crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if current_user.role is not None and current_user.role.name == "admin":
        return {"post": post, "user": current_user}
   
    if current_user.role is not None and current_user.role.name == "author" and post.author_id == current_user.id:
        return {"post": post, "user": current_user}
    raise HTTPException(status_code=403, detail="Not allowed to modify this post")
