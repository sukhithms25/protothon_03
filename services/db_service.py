from sqlalchemy.orm import Session
import models

def get_repo(db: Session, repo_id: int):
    return db.query(models.Repository).filter(models.Repository.id == repo_id).first()

def get_user_repos(db: Session, user_id: int):
    return db.query(models.Repository).filter(models.Repository.owner_id == user_id).all()

def get_all_repos(db: Session):
    return db.query(models.Repository).all()

def create_repo(db: Session, name: str, description: str, owner_id: int):
    db_repo = models.Repository(name=name, description=description, owner_id=owner_id)
    db.add(db_repo)
    db.commit()
    db.refresh(db_repo)

    # Automatically seed the repository with some initial dummy files so the AI has something to read
    seed_files = [
        models.File(repo_id=db_repo.id, path="README.md", content=f"# {name}\n\n{description}\n\nThis is a mock repository."),
        models.File(repo_id=db_repo.id, path="main.py", content='def hello_world():\n    print("Hello from AI clone!")\n\nif __name__ == "__main__":\n    hello_world()'),
        models.File(repo_id=db_repo.id, path="utils.py", content='def add(a, b):\n    return a + b\n')
    ]
    db.add_all(seed_files)
    db.commit()
    return db_repo

def get_repo_files(db: Session, repo_id: int):
    return db.query(models.File).filter(models.File.repo_id == repo_id).all()

def get_file_content(db: Session, repo_id: int, file_path: str):
    file = db.query(models.File).filter(models.File.repo_id == repo_id, models.File.path == file_path).first()
    return file.content if file else None

def update_file_content(db: Session, repo_id: int, file_path: str, new_content: str):
    file = db.query(models.File).filter(models.File.repo_id == repo_id, models.File.path == file_path).first()
    if file:
        file.content = new_content
        db.commit()

def get_repo_issues(db: Session, repo_id: int):
    return db.query(models.Issue).filter(models.Issue.repo_id == repo_id).all()

def create_issue(db: Session, repo_id: int, title: str, body: str, author_id: int):
    db_issue = models.Issue(repo_id=repo_id, title=title, body=body, author_id=author_id)
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue

def get_repo_prs(db: Session, repo_id: int):
    return db.query(models.PullRequest).filter(models.PullRequest.repo_id == repo_id).all()

def create_pull_request(db: Session, repo_id: int, title: str, body: str, branch_name: str, author_id: int):
    db_pr = models.PullRequest(
        repo_id=repo_id,
        title=title,
        body=body,
        branch_name=branch_name,
        author_id=author_id
    )
    db.add(db_pr)
    db.commit()
    db.refresh(db_pr)
    return db_pr
