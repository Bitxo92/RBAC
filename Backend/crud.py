from sqlalchemy.orm import Session
from . import models, security
from typing import Optional, List


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, username: str, email: str, password: str, role_name: str | None = None):
    hashed = security.hash_password(password)
    user = models.User(username=username, email=email, password_hash=hashed)
    if role_name:
        role = db.query(models.Role).filter(models.Role.name == role_name).first()
        if role:
            user.role = role
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not security.verify_password(password, user.password_hash):
        return None
    return user

def create_role_if_not_exists(db: Session, name: str):
    r = db.query(models.Role).filter(models.Role.name == name).first()
    if not r:
        r = models.Role(name=name)
        db.add(r)
        db.commit()
        db.refresh(r)
    return r


def create_post(db: Session, author: models.User, title: str, content: str):
    post = models.Post(title=title, content=content, author=author)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()

def list_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Post).order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()

def update_post(db: Session, post: models.Post, title: str, content: str):
    post.title = title
    post.content = content
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

def delete_post(db: Session, post: models.Post):
    db.delete(post)
    db.commit()


def create_comment(db: Session, post: models.Post, content: str, author: Optional[models.User] = None):
    comment = models.Comment(content=content, post=post, author=author)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

def list_comments_for_post(db: Session, post_id: int):
    return db.query(models.Comment).filter(models.Comment.post_id == post_id).order_by(models.Comment.created_at).all()
