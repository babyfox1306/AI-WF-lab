from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

from app.database.database import init_db

# Import all routers
from app.auth.routes import router as auth_router
from app.dashboard.routes import router as dashboard_router
from app.jobs.routes import router as jobs_router
from app.logs.routes import router as logs_router
from app.users.routes import router as users_router
from app.workflows.routes import router as workflows_router
from app.workspaces.routes import router as workspaces_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database on startup and clean up on shutdown."""
    init_db()
    yield


app = FastAPI(
    title="AI Workflow Lab",
    description="A SaaS platform for creating and monitoring AI workflows.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(workspaces_router)
app.include_router(workflows_router)
app.include_router(jobs_router)
app.include_router(logs_router)
app.include_router(dashboard_router)

# Frontend - serve static files and templates
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/")
def serve_frontend(request: Request):
    """Serve the main SPA frontend."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}
