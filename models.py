from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    repos = relationship("Repository", back_populates="owner")
    issues = relationship("Issue", back_populates="author")
    prs = relationship("PullRequest", back_populates="author")

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="repos")
    files = relationship("File", back_populates="repo")
    issues = relationship("Issue", back_populates="repo")
    prs = relationship("PullRequest", back_populates="repo")

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"))
    path = Column(String, index=True)
    content = Column(Text)

    repo = relationship("Repository", back_populates="files")

class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"))
    title = Column(String, index=True)
    body = Column(Text)
    status = Column(String, default="open") # open, closed
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    repo = relationship("Repository", back_populates="issues")
    author = relationship("User", back_populates="issues")

class PullRequest(Base):
    __tablename__ = "pull_requests"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"), index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=True)
    title = Column(String, index=True)
    body = Column(Text)
    state = Column(String, default="open") # open, merged, closed
    branch_name = Column(String)
    
    # New fields for PR review and merge logic
    target_path = Column(String)
    original_code = Column(Text)
    proposed_code = Column(Text)
    ai_review = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    repo = relationship("Repository", back_populates="prs")
    author = relationship("User", back_populates="prs")
    issue = relationship("Issue")
