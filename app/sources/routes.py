from typing import List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.service import get_current_user
from app.database.database import get_db
from app.sources.models import SourceDocument
from app.sources.schemas import SourceCreate, SourceResponse
from app.workspaces.service import get_workspace

router = APIRouter(prefix="/projects/{project_id}/sources", tags=["sources"])


@router.post("/", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
def create(project_id: int, data: SourceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.projects.models import OpportunityProject
    project = db.query(OpportunityProject).filter(OpportunityProject.id == project_id).first()
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")
    get_workspace(db, project.workspace_id, current_user)

    source = SourceDocument(
        workspace_id=project.workspace_id,
        project_id=project_id,
        source_type=data.source_type,
        title=data.title,
        raw_text=data.raw_text,
        structured_data="{}",
        checksum=SourceDocument.compute_checksum(data.raw_text),
        created_by=current_user.id,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.get("/", response_model=List[SourceResponse])
def list_all(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.projects.models import OpportunityProject
    project = db.query(OpportunityProject).filter(OpportunityProject.id == project_id).first()
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")
    get_workspace(db, project.workspace_id, current_user)
    return db.query(SourceDocument).filter(SourceDocument.project_id == project_id).all()


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(project_id: int, source_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    source = db.query(SourceDocument).filter(SourceDocument.id == source_id).first()
    if not source:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Source not found")
    from app.projects.models import OpportunityProject
    project = db.query(OpportunityProject).filter(OpportunityProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    get_workspace(db, project.workspace_id, current_user)
    db.delete(source)
    db.commit()
