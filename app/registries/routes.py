from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.service import get_current_user
from app.database.database import get_db
from app.registries.models import GroundTruthRegistry
from app.registries.schemas import RegistryCreate, RegistryResponse, RegistryUpdate
from app.workspaces.service import get_workspace

router = APIRouter(prefix="/projects/{project_id}/registry", tags=["registry"])


@router.post("/", response_model=RegistryResponse, status_code=status.HTTP_201_CREATED)
def create(project_id: int, data: RegistryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.projects.models import OpportunityProject
    project = db.query(OpportunityProject).filter(OpportunityProject.id == project_id).first()
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")
    get_workspace(db, project.workspace_id, current_user)

    import json
    item = GroundTruthRegistry(
        project_id=project_id,
        key=data.key,
        value=json.dumps(data.value) if data.value else "{}",
        category=data.category,
        source_document_id=data.source_document_id,
        confidence=data.confidence,
        locked=data.locked,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=List[RegistryResponse])
def list_all(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.projects.models import OpportunityProject
    project = db.query(OpportunityProject).filter(OpportunityProject.id == project_id).first()
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")
    get_workspace(db, project.workspace_id, current_user)
    return db.query(GroundTruthRegistry).filter(GroundTruthRegistry.project_id == project_id).all()


@router.patch("/{item_id}", response_model=RegistryResponse)
def update(project_id: int, item_id: int, data: RegistryUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(GroundTruthRegistry).filter(GroundTruthRegistry.id == item_id).first()
    if not item:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Registry item not found")
    from app.projects.models import OpportunityProject
    project = db.query(OpportunityProject).filter(OpportunityProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    get_workspace(db, project.workspace_id, current_user)

    if data.locked is not None:
        item.locked = data.locked
    if data.confidence is not None:
        item.confidence = data.confidence
    if data.value is not None:
        import json
        item.value = json.dumps(data.value)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}/lock", response_model=RegistryResponse)
def toggle_lock(project_id: int, item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(GroundTruthRegistry).filter(GroundTruthRegistry.id == item_id).first()
    if not item:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Registry item not found")
    from app.projects.models import OpportunityProject
    project = db.query(OpportunityProject).filter(OpportunityProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    get_workspace(db, project.workspace_id, current_user)
    item.locked = not item.locked
    db.commit()
    db.refresh(item)
    return item
