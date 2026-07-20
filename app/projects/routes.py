from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.service import get_current_user
from app.database.database import get_db
from app.projects.models import OpportunityProject
from app.projects.schemas import ProjectCreate, ProjectResponse, ProjectUpdate
from app.workspaces.service import get_workspace

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create(data: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_workspace(db, data.workspace_id, current_user)
    project = OpportunityProject(
        workspace_id=data.workspace_id,
        name=data.name,
        project_type=data.project_type,
        status="draft",
        description=data.description or "",
        created_by=current_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/", response_model=List[ProjectResponse])
def list_all(workspace_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.workspaces.service import list_workspaces
    user_ws_ids = [ws.id for ws in list_workspaces(db, current_user)]
    query = db.query(OpportunityProject).filter(OpportunityProject.workspace_id.in_(user_ws_ids))
    if workspace_id:
        query = query.filter(OpportunityProject.workspace_id == workspace_id)
    return query.order_by(OpportunityProject.created_at.desc()).all()


@router.get("/{project_id}", response_model=ProjectResponse)
def get(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(OpportunityProject).filter(OpportunityProject.id == project_id).first()
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")
    get_workspace(db, project.workspace_id, current_user)
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
def update(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(OpportunityProject).filter(OpportunityProject.id == project_id).first()
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")
    get_workspace(db, project.workspace_id, current_user)
    if data.name is not None:
        project.name = data.name
    if data.status is not None:
        project.status = data.status
    if data.description is not None:
        project.description = data.description
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(OpportunityProject).filter(OpportunityProject.id == project_id).first()
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")
    get_workspace(db, project.workspace_id, current_user)
    db.delete(project)
    db.commit()
