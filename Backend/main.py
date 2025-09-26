import os
from fastapi import FastAPI
from .database import create_db_and_tables
from .routers import auth, users, posts, comments
from . import crud

app = FastAPI(title="RBAC Prototype App")

@app.on_event("startup")
def on_startup():
    
    create_db_and_tables()
    
    from .database import SessionLocal
    db = SessionLocal()
    try:
        crud.create_role_if_not_exists(db, "admin")
        crud.create_role_if_not_exists(db, "author")
        crud.create_role_if_not_exists(db, "user")
        # NOTE:creates default admin if not exists, for testing purposes
        from . import models
        admin = db.query(models.User).filter(models.User.username == "admin").first()
        if not admin:
            admin = crud.create_user(db, "admin", "admin@example.com", "adminpass", role_name="admin")
    finally:
        db.close()

# include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(comments.router)
