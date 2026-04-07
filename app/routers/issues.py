from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_db
from app.models.issue import Issue
from app.models.project import Project
from app.models.user import User
from app.schemas.issue import IssueCreate, IssueResponse, IssueUpdate

router = APIRouter(prefix="/api/v1", tags=["Issues"])


def _get_project_or_404(project_id: int, db: Session) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


def _get_issue_or_404(issue_id: int, project_id: int, db: Session) -> Issue:
    issue = db.query(Issue).filter(Issue.id == issue_id, Issue.project_id == project_id).first()
    if issue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
    return issue


@router.post(
    "/projects/{project_id}/issues",
    response_model=IssueResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_issue(
    project_id: int,
    payload: IssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _get_project_or_404(project_id, db)
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the project owner")

    issue = Issue(
        **payload.model_dump(),
        project_id=project_id,
        reporter_id=current_user.id,
        status="open",
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


@router.get("/projects/{project_id}/issues", response_model=list[IssueResponse])
def list_issues(
    project_id: int,
    issue_status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, db)

    query = db.query(Issue).filter(Issue.project_id == project_id)
    if issue_status is not None:
        query = query.filter(Issue.status == issue_status)
    return query.order_by(Issue.created_at.desc()).all()


@router.put("/projects/{project_id}/issues/{issue_id}", response_model=IssueResponse)
def update_issue(
    project_id: int,
    issue_id: int,
    payload: IssueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, db)
    issue = _get_issue_or_404(issue_id, project_id, db)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(issue, field, value)
    issue.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(issue)
    return issue


@router.delete(
    "/projects/{project_id}/issues/{issue_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_issue(
    project_id: int,
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(project_id, db)
    issue = _get_issue_or_404(issue_id, project_id, db)

    db.delete(issue)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
