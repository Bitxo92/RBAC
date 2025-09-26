import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL="postgresql://root:root@localhost:5432/rbac_db"


engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def create_db_and_tables():
    from .models import User, Role, Post, Comment  
    Base.metadata.create_all(bind=engine)
