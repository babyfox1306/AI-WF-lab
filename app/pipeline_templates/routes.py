from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.service import get_current_user
from app.database.database import get_db
from app.pipeline_templates.models import PipelineTemplate
from app.pipeline_templates.schemas import TemplateResponse

router = APIRouter(prefix="/pipeline-templates", tags=["pipeline-templates"])


@router.get("/", response_model=List[TemplateResponse])
def list_all(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(PipelineTemplate).filter(PipelineTemplate.is_active == True).order_by(PipelineTemplate.name).all()


@router.get("/{template_id}", response_model=TemplateResponse)
def get(template_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    template = db.query(PipelineTemplate).filter(PipelineTemplate.id == template_id).first()
    if not template:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Template not found")
    return template
