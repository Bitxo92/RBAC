from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, DateTime, func
from sqlalchemy.orm import relationship
from .database import Base




class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    role_id = Column(Integer, ForeignKey("roles.id", ondelete="SET NULL"),default=3)
    role = relationship("Role", back_populates="users")

    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), unique=True, nullable=False)

    users = relationship("User", back_populates="role")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"))
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")
