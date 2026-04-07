from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter(prefix="/api/v1", tags=["Projects"])


def _get_project_or_404(project_id: int, db: Session) -> Project:
    """
    Retrieve a Project by its ID or raise a 404 HTTPException.
    
    Parameters:
        project_id (int): Primary key of the project to fetch.
    
    Returns:
        project (Project): The matching Project instance.
    
    Raises:
        HTTPException: If no Project with the given id exists (status 404).
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


def _assert_owner(project: Project, current_user: User) -> None:
    """
    Verify that the given user is the owner of the project.
    
    Parameters:
        project (Project): The project to check ownership of.
        current_user (User): The authenticated user to verify as the owner.
    
    Raises:
        HTTPException: with status 403 and detail "Not the project owner" if `current_user.id` does not match `project.owner_id`.
    """
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not the project owner")


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new Project associated with the authenticated user.
    
    Parameters:
        payload (ProjectCreate): Fields used to create the project.
    
    Returns:
        Project: The persisted Project instance owned by the current user.
    """
    project = Project(**payload.model_dump(), owner_id=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/projects", response_model=list[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return all Project records owned by the authenticated user.
    
    Returns:
        list[Project]: ORM Project instances whose `owner_id` equals the authenticated user's `id`.
    """
    return db.query(Project).filter(Project.owner_id == current_user.id).all()


@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve a Project by its ID and verify that the authenticated user owns it.
    
    Parameters:
        project_id (int): ID of the project to fetch.
    
    Returns:
        Project: The project matching `project_id`.
    
    Raises:
        HTTPException: 404 if the project does not exist.
        HTTPException: 403 if the authenticated user is not the project's owner.
    """
    project = _get_project_or_404(project_id, db)
    _assert_owner(project, current_user)
    return project


@router.put("/projects/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing project with the fields provided in the payload.
    
    The payload's present fields (those set on the `ProjectUpdate` model) are applied to the project, the change is committed, and the project is refreshed before being returned.
    
    Parameters:
        project_id (int): ID of the project to update.
        payload (ProjectUpdate): Fields to update; only attributes included in the payload are changed.
    
    Returns:
        Project: The updated project instance.
    
    Raises:
        HTTPException: 404 if the project does not exist.
        HTTPException: 403 if the current user is not the project owner.
    """
    project = _get_project_or_404(project_id, db)
    _assert_owner(project, current_user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a project owned by the authenticated user.
    
    Parameters:
        project_id (int): ID of the project to delete.
    
    Returns:
        Response: Empty response with HTTP status 204 (No Content).
    """
    project = _get_project_or_404(project_id, db)
    _assert_owner(project, current_user)
    db.delete(project)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
