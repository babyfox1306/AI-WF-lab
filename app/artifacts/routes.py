from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.artifacts.models import Artifact
from app.artifacts.schemas import ArtifactResponse
from app.auth.models import User
from app.auth.service import get_current_user
from app.database.database import get_db
from app.projects.models import OpportunityProject
from app.workspaces.service import get_workspace

router = APIRouter(prefix="/projects/{project_id}/artifacts", tags=["artifacts"])


@router.get("/", response_model=List[ArtifactResponse])
def list_all(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(OpportunityProject).filter(OpportunityProject.id == project_id).first()
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")
    get_workspace(db, project.workspace_id, current_user)
    return db.query(Artifact).filter(Artifact.project_id == project_id).order_by(Artifact.created_at.desc()).all()


@router.get("/{artifact_id}", response_model=ArtifactResponse)
def get(project_id: int, artifact_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
    if not artifact:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Artifact not found")
    project = db.query(OpportunityProject).filter(OpportunityProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    get_workspace(db, project.workspace_id, current_user)
    return artifact
