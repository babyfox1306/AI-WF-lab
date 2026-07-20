from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.agents.models import AgentDefinition
from app.agents.schemas import AgentCreate, AgentResponse, AgentUpdate
from app.auth.models import User
from app.auth.service import get_current_user
from app.database.database import get_db
from app.workspaces.service import get_workspace, list_workspaces

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def create(data: AgentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_workspace(db, data.workspace_id, current_user)
    agent = AgentDefinition(
        workspace_id=data.workspace_id,
        name=data.name,
        slug=data.slug,
        description=data.description or "",
        role=data.role,
        system_prompt=data.system_prompt,
        provider_connection_id=data.provider_connection_id,
        model_override=data.model_override,
        temperature=data.temperature,
        max_output_tokens=data.max_output_tokens,
        output_schema=data.output_schema or "{}",
        version=1,
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


@router.get("/", response_model=List[AgentResponse])
def list_all(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ws_ids = [ws.id for ws in list_workspaces(db, current_user)]
    return db.query(AgentDefinition).filter(AgentDefinition.workspace_id.in_(ws_ids)).order_by(AgentDefinition.name).all()


@router.get("/{agent_id}", response_model=AgentResponse)
def get(agent_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    agent = db.query(AgentDefinition).filter(AgentDefinition.id == agent_id).first()
    if not agent:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Agent not found")
    get_workspace(db, agent.workspace_id, current_user)
    return agent


@router.patch("/{agent_id}", response_model=AgentResponse)
def update(agent_id: int, data: AgentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    agent = db.query(AgentDefinition).filter(AgentDefinition.id == agent_id).first()
    if not agent:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Agent not found")
    get_workspace(db, agent.workspace_id, current_user)
    for field in ("name", "slug", "description", "role", "system_prompt", "model_override", "temperature", "max_output_tokens", "is_active"):
        val = getattr(data, field, None)
        if val is not None:
            setattr(agent, field, val)
    if data.output_schema is not None:
        agent.output_schema = data.output_schema
    if data.provider_connection_id is not None:
        agent.provider_connection_id = data.provider_connection_id
    agent.version += 1
    db.commit()
    db.refresh(agent)
    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(agent_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    agent = db.query(AgentDefinition).filter(AgentDefinition.id == agent_id).first()
    if not agent:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Agent not found")
    get_workspace(db, agent.workspace_id, current_user)
    db.delete(agent)
    db.commit()
