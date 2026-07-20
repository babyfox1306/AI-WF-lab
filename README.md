# AI Workflow Lab 🤖

A **SaaS MVP** for creating and monitoring AI workflows. Built with FastAPI, SQLAlchemy, SQLite, and JWT authentication.

## Features

### Core Features
- ✅ **User Management** — Register, login, JWT authentication, profile management
- ✅ **Workspace System** — Multiple workspaces per user with access isolation
- ✅ **Workflow Management** — AI automation pipelines with status tracking (draft, running, completed, failed)
- ✅ **Job Execution** — Create and execute jobs with simulated AI processing
- ✅ **Logging System** — Automatic execution logs for every job run
- ✅ **Dashboard** — Real-time statistics and activity feed

### Technical Features
- ✅ Modular architecture with clear separation of concerns
- ✅ JWT-based authentication with bcrypt password hashing
- ✅ SQLAlchemy ORM with SQLite (easy to switch to PostgreSQL)
- ✅ Comprehensive test suite (34 tests)
- ✅ Swagger UI at `/docs`
- ✅ Beautiful dark-mode SPA dashboard

## Architecture

```
ai-workflow-lab/
├── app/
│   ├── auth/          # User model, JWT auth, register/login/profile
│   ├── database/      # SQLAlchemy engine, session, Base
│   ├── workspaces/    # CRUD for workspaces
│   ├── workflows/     # CRUD for workflows
│   ├── jobs/          # Job lifecycle (pending → running → completed/failed)
│   ├── logs/          # Job execution logs
│   ├── dashboard/     # Aggregated statistics
│   ├── templates/     # Frontend SPA
│   └── main.py        # FastAPI app entry point
├── tests/             # 34 pytest tests
├── requirements.txt
└── README.md
```

## Database Schema

```
users ──1:N── workspaces ──1:N── workflows ──1:N── jobs ──1:N── logs
```

| Entity | Fields |
|--------|--------|
| **User** | id, email (unique), username (unique), hashed_password, is_active, created_at |
| **Workspace** | id, name, owner_id (FK), created_at |
| **Workflow** | id, workspace_id (FK), name, description, status (draft/running/completed/failed), created_at |
| **Job** | id, workflow_id (FK), name, input_data (JSON), output_data (JSON), status (pending/running/completed/failed), error_message, started_at, finished_at |
| **Log** | id, job_id (FK), level (info/warning/error), message, timestamp |

## API Endpoints

### Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login, returns JWT token |
| GET | `/auth/me` | Get current user profile |
| PATCH | `/auth/me` | Update user profile |

### Workspaces
| Method | Path | Description |
|--------|------|-------------|
| POST | `/workspaces/` | Create workspace |
| GET | `/workspaces/` | List user's workspaces |
| GET | `/workspaces/{id}` | Get workspace |
| PATCH | `/workspaces/{id}` | Update workspace |
| DELETE | `/workspaces/{id}` | Delete workspace |

### Workflows
| Method | Path | Description |
|--------|------|-------------|
| POST | `/workspaces/{ws_id}/workflows/` | Create workflow |
| GET | `/workspaces/{ws_id}/workflows/` | List workflows in workspace |
| GET | `/workspaces/{ws_id}/workflows/{id}` | Get workflow |
| PATCH | `/workspaces/{ws_id}/workflows/{id}` | Update workflow |
| DELETE | `/workspaces/{ws_id}/workflows/{id}` | Delete workflow |

### Jobs
| Method | Path | Description |
|--------|------|-------------|
| POST | `/workflows/{wf_id}/jobs/` | Create job |
| GET | `/workflows/{wf_id}/jobs/` | List jobs in workflow |
| GET | `/workflows/{wf_id}/jobs/{id}` | Get job |
| POST | `/workflows/{wf_id}/jobs/{id}/execute` | Execute job |

### Logs
| Method | Path | Description |
|--------|------|-------------|
| GET | `/jobs/{id}/logs/` | List logs for a job |

### Dashboard
| Method | Path | Description |
|--------|------|-------------|
| GET | `/dashboard/` | Get aggregated statistics |

## Quick Start

### Prerequisites
- Python 3.10+
- pip

### Setup

```bash
# 1. Navigate to project
cd ai-workflow-lab

# 2. (Recommended) Create virtual environment
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
uvicorn app.main:app --reload
```

### Access

- **Web App**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Running Tests

```bash
pytest -v
```

**34 tests** covering:
- User registration & validation (duplicate email/username, short passwords)
- Login with correct/wrong credentials
- User profile retrieval & update
- Workspace CRUD & authorization
- Workflow CRUD within workspaces
- Job lifecycle (create, execute, logs, re-execution prevention)
- Failed job handling with error messages
- Dashboard statistics & user isolation

## User Flow

1. **Register** — Create an account with email, username, password
2. **Create Workspace** — Organize your AI projects
3. **Create Workflow** — Define an AI automation pipeline
4. **Create Job** — Add a job with input data to a workflow
5. **Execute Job** — Run the job (simulated AI processing)
6. **View Results** — See output data and execution logs
7. **Monitor Dashboard** — Track total workflows, running/completed/failed jobs

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Web framework |
| **SQLAlchemy** | ORM |
| **SQLite** | Database |
| **PyJWT** | JWT authentication |
| **passlib + bcrypt** | Password hashing |
| **Pydantic** | Data validation |
| **pytest** | Testing |
| **Jinja2** | Frontend templates |

## License

MIT
