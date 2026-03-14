from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from datetime import timedelta
from database import get_db

import models
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
import services.db_service as db_service
from agents.issue_agent import process_issue

router = APIRouter()

@router.get("/api/health")
def health():
    return {"status": "ok"}

# --- Pydantic Models ---
class UserCreate(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    class Config:
        from_attributes = True

class RepoCreate(BaseModel):
    name: str
    description: str = ""

class IssueCreate(BaseModel):
    title: str
    body: str

# --- Auth Routes ---
@router.post("/api/auth/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        print(f"DEBUG: Signup request for {user.username}")
        db_user = db.query(models.User).filter(models.User.username == user.username).first()
        if db_user:
            print(f"DEBUG: Signup failed - user exists: {user.username}")
            raise HTTPException(status_code=400, detail="Username already registered")
        
        hashed_password = get_password_hash(user.password)
        new_user = models.User(username=user.username, hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"DEBUG: Signup success for {user.username}")
        return {"message": "User created successfully"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"DEBUG: Signup EXCEPTION: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        print(f"DEBUG: Login request for {form_data.username}")
        user = db.query(models.User).filter(models.User.username == form_data.username).first()
        if not user or not verify_password(form_data.password, user.hashed_password):
            print(f"DEBUG: Login failed - invalid credentials: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        print(f"DEBUG: Login success for {form_data.username}")
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"DEBUG: Login EXCEPTION: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/me", response_model=UserRead)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    print(f"DEBUG: Serving /api/me for {current_user.username}")
    return current_user

# --- Repo Routes ---
@router.get("/api/repos")
def list_repos(db: Session = Depends(get_db)):
    # In a real app we'd paginate. Here we return all repos
    repos = db_service.get_all_repos(db)
    return [{
        "id": r.id, 
        "name": r.name, 
        "full_name": f"{r.owner.username}/{r.name}",
        "description": r.description,
        "owner": r.owner.username,
        "stars": 0,
        "forks": 0,
        "language": "Python",
        "visibility": "Public",
        "updated_at": r.created_at.strftime("%b %d, %Y")
    } for r in repos]

@router.post("/api/repos")
def create_repository(repo: RepoCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Check if user already has a repo with this name
    existing = db.query(models.Repository).filter(
        models.Repository.owner_id == current_user.id,
        models.Repository.name == repo.name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Repository name already exists for this user")

    new_repo = db_service.create_repo(db, name=repo.name, description=repo.description, owner_id=current_user.id)
    return {"id": new_repo.id, "name": new_repo.name, "full_name": f"{current_user.username}/{new_repo.name}"}

@router.get("/api/repos/{owner}/{repo_name}")
def get_repo_details(owner: str, repo_name: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == owner).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    repo = db.query(models.Repository).filter(
        models.Repository.owner_id == user.id,
        models.Repository.name == repo_name
    ).first()
    
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
        
    return {
        "id": repo.id,
        "name": repo.name,
        "full_name": f"{owner}/{repo.name}",
        "description": repo.description,
        "created_at": repo.created_at
    }

@router.get("/api/repos/{owner}/{repo_name}/files")
def get_files(owner: str, repo_name: str, db: Session = Depends(get_db)):
    repo = get_repo_details(owner, repo_name, db)
    files = db_service.get_repo_files(db, repo["id"])
    return [f.path for f in files]

@router.get("/api/repos/{owner}/{repo_name}/issues")
def get_issues(owner: str, repo_name: str, db: Session = Depends(get_db)):
    repo = get_repo_details(owner, repo_name, db)
    issues = db_service.get_repo_issues(db, repo["id"])
    return [{
        "id": i.id,
        "title": i.title,
        "body": i.body,
        "status": i.status,
        "author": i.author.username
    } for i in issues]

@router.post("/api/repos/{owner}/{repo_name}/issues")
def create_issue(owner: str, repo_name: str, issue: IssueCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    repo = get_repo_details(owner, repo_name, db)
    new_issue = db_service.create_issue(db, repo["id"], issue.title, issue.body, current_user.id)
    return {"id": new_issue.id, "title": new_issue.title, "status": "open"}

@router.get("/api/repos/{owner}/{repo_name}/prs")
def get_prs(owner: str, repo_name: str, db: Session = Depends(get_db)):
    repo = get_repo_details(owner, repo_name, db)
    prs = db_service.get_repo_prs(db, repo["id"])
    return [{
        "id": pr.id,
        "title": pr.title,
        "state": pr.state,
        "author": pr.author.username,
        "branch": pr.branch_name,
        "proposed_code": pr.proposed_code,
        "target_path": pr.target_path,
        "ai_review": pr.ai_review,
        "description": pr.description
    } for pr in prs]

@router.post("/api/repos/{owner}/{repo_name}/generate-pr")
def generate_ai_pr(owner: str, repo_name: str, issue: IssueCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Trigger the AI to fix a given issue and create a PR natively."""
    repo = get_repo_details(owner, repo_name, db)
    
    # First create the issue record so we have an ID
    new_issue = db_service.create_issue(db, repo["id"], issue.title, issue.body, current_user.id)
    
    try:
        result = process_issue(
            db=db,
            repo_id=repo["id"],
            issue_title=issue.title,
            issue_body=issue.body,
            author_id=current_user.id,
            issue_number=new_issue.id
        )
        return {"status": "success", "data": result, "issue_id": new_issue.id}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

class AiChatRequest(BaseModel):
    prompt: str
    image: Optional[str] = None

@router.post("/api/ai/chat")
def ai_chat(request: AiChatRequest, current_user: models.User = Depends(get_current_user)):
    from services.llm_service import ask_llm
    response = ask_llm(request.prompt, request.image)
    return {"response": response}

@router.post("/api/repos/{owner}/{repo_name}/prs/{pr_id}/merge")
def merge_pull_request(owner: str, repo_name: str, pr_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Verify repo belongs to owner if necessary, for now we just merge by ID
    merged_pr = db_service.merge_pr(db, pr_id)
    if not merged_pr:
        raise HTTPException(status_code=400, detail="PR not found or already merged")
    return {"status": "success", "message": "Pull Request merged successfully"}