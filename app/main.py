from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi import Request

from app.config import settings
from app.database.database import init_db

# Import all routers (legacy)
from app.auth.routes import router as auth_router
from app.dashboard.routes import router as dashboard_router
from app.jobs.routes import router as jobs_router
from app.logs.routes import router as logs_router
from app.users.routes import router as users_router
from app.workflows.routes import router as workflows_router
from app.workspaces.routes import router as workspaces_router

# Import SignalForge routers
from app.providers.routes import router as providers_router
from app.projects.routes import router as projects_router
from app.sources.routes import router as sources_router
from app.registries.routes import router as registry_router
from app.agents.routes import router as agents_router
from app.tools.routes import router as tools_router
from app.executions.routes import router as executions_router
from app.artifacts.routes import router as artifacts_router
from app.approvals.routes import router as approvals_router
from app.pipeline_templates.routes import router as pipeline_templates_router
from app.exports.routes import router as exports_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database on startup and clean up on shutdown."""
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    description="AI Opportunity Intelligence Factory — Multi-agent research and decision system.",
    version=settings.app_version,
    lifespan=lifespan,
)

# CORS
cors_origins = settings.cors_origins
if cors_origins == "*":
    cors_origins_list = ["*"]
else:
    cors_origins_list = [o.strip() for o in cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register legacy API routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(workspaces_router)
app.include_router(workflows_router)
app.include_router(jobs_router)
app.include_router(logs_router)
app.include_router(dashboard_router)

# Register SignalForge routers
app.include_router(providers_router)
app.include_router(projects_router)
app.include_router(sources_router)
app.include_router(registry_router)
app.include_router(agents_router)
app.include_router(tools_router)
app.include_router(executions_router)
app.include_router(artifacts_router)
app.include_router(approvals_router)
app.include_router(pipeline_templates_router)
app.include_router(exports_router)

# Frontend
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/")
def serve_frontend(request: Request):
    """Serve the main SPA frontend."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.app_name, "version": settings.app_version}


@app.get("/ready")
def readiness_check():
    """Readiness check - verifies critical dependencies."""
    from sqlalchemy import text
    from app.database.database import SessionLocal
    db_ok = False
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db_ok = True
        db.close()
    except Exception:
        pass
    return {
        "ready": db_ok,
        "database": "connected" if db_ok else "disconnected",
        "service": settings.app_name,
        "version": settings.app_version,
    }