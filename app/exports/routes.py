from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.service import get_current_user
from app.database.database import get_db
from app.exports.service import ExportService
from app.projects.models import OpportunityProject
from app.workspaces.service import get_workspace

router = APIRouter(prefix="/projects/{project_id}/exports", tags=["exports"])

svc = ExportService()


@router.get("")
def export_package(
    project_id: int,
    format: str = Query(default="json", pattern="^(json|markdown|proposal)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(OpportunityProject).filter(OpportunityProject.id == project_id).first()
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")
    get_workspace(db, project.workspace_id, current_user)

    from app.artifacts.models import Artifact
    artifacts = db.query(Artifact).filter(Artifact.project_id == project_id, Artifact.is_final == True).all()

    # Build package from artifacts
    package = svc.build_package(
        project={"id": project.id, "name": project.name, "project_type": project.project_type},
        scorecard={},
        assessment={},
        sources=[],
        execution_metadata={"status": project.status},
    )

    if format == "json":
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(
            content=svc.export_json(package),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="decision-package-{project_id}.json"'},
        )
    elif format == "markdown":
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(
            content=svc.export_markdown(package),
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="decision-package-{project_id}.md"'},
        )
    else:
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(
            content=svc.export_plain_text_proposal(package),
            media_type="text/plain",
            headers={"Content-Disposition": f'attachment; filename="proposal-{project_id}.txt"'},
        )
