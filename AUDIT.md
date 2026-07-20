# Repository Audit: AI Workflow Lab → SignalForge

**Date:** 2026-07-20
**Baseline Tests:** 34/34 passing

---

## Current Architecture

### Stack
- **FastAPI** 0.115.6 — Web framework
- **SQLAlchemy** 2.0.36 — ORM
- **SQLite** — Database
- **PyJWT** 2.13.0 — JWT auth
- **passlib 1.7.4 + bcrypt 4.0.1** — Password hashing
- **Jinja2** — Frontend templates (dark SPA)

### Module Structure (current)
```
app/
├── auth/            User model, register/login, JWT service
├── users/           Profile endpoints (GET/PATCH /users/me)
├── database/        Engine, session, Base, init_db()
├── workspaces/      Workspace CRUD with owner-based isolation
├── workflows/       Workflow CRUD with status (draft/running/completed/failed)
├── jobs/            Job lifecycle (pending→running→completed/failed) + simulated execution
├── logs/            Job execution logs with level/message/timestamp
├── dashboard/       Aggregated stats (total_workflows, running/completed/failed jobs, recent_activity)
├── templates/       Jinja2 dark SPA frontend
└── main.py          FastAPI app with CORS, lifespan, all routers

tests/ → 34 tests (auth 10, workspaces 10, workflows 5, jobs 5, dashboard 4)
```

### Database Entities
| Entity | Table | Key Fields | Relationships |
|--------|-------|------------|---------------|
| User | users | id, email*, username*, hashed_password, is_active | → workspaces (1:N) |
| Workspace | workspaces | id, name, owner_id* | → users, → workflows (1:N) |
| Workflow | workflows | id, workspace_id*, name, status* | → workspaces, → jobs (1:N) |
| Job | jobs | id, workflow_id*, name, status*, input/output_data(JSON) | → workflows, → logs (1:N) |
| Log | logs | id, job_id*, level*, message, timestamp | → jobs |

### API Routes (current)
| Module | Prefix | Endpoints |
|--------|--------|-----------|
| Auth | /auth | POST register, POST login |
| Users | /users | GET/PATCH me |
| Workspaces | /workspaces | POST, GET list, GET by id, PATCH, DELETE |
| Workflows | /workspaces/{ws}/workflows | POST, GET list, GET by id, PATCH, DELETE |
| Jobs | /workflows/{wf}/jobs | POST, GET list, GET by id, POST execute |
| Logs | /jobs/{id}/logs | GET list |
| Dashboard | /dashboard | GET stats |
| Health | /health | GET alive check |
| Root | / | GET frontend SPA |

### Auth Approach
- JWT with HS256, configurable expiry (default 60 min)
- bcrypt password hashing via passlib
- OAuth2PasswordBearer token extraction
- User ID in JWT `sub` claim
- Workspace-level ownership checks (`owner_id == user.id`)
- Cascade: workspace → workflow → job → log access control

### Job Execution (current)
- Simple synchronous execution within HTTP request
- Random simulated AI processing (90% success)
- Creates 4-6 log entries per execution
- Status transitions: pending → running → completed/failed
- Not durable; not resumable; not persisted incrementally

### Frontend
- Single Jinja2 template (`index.html`) with embedded CSS/JS
- Dark theme, sidebar layout with dashboard/workspaces/workflows/jobs pages
- Modal-based CRUD, toast notifications
- Calls API directly from browser

### Test Coverage (34 tests)
| Category | Tests | Coverage |
|----------|-------|----------|
| Registration | 4 | success, duplicate email, duplicate username, short password |
| Login | 3 | success, wrong password, nonexistent user |
| Profile | 3 | get, unauthorized, update |
| Workspaces | 10 | create/success/empty/unauthorized, list/empty/multiple, get/found/not_found, update, delete/success/not_found |
| Workflows | 5 | create/success/unauthorized, list/empty/multiple, update/status, delete |
| Jobs | 5 | create, execute/logs, already_completed, failed/error_message |
| Dashboard | 4 | empty, with_data, user_isolation |

### Technical Debt / Risks
1. No database migrations (direct `create_all`)
2. SQLite-only assumptions (`check_same_thread`)
3. No secret encryption for API keys (not yet needed)
4. Synchronous blocking job execution
5. Wildcard CORS (`*`)
6. Hardcoded product name "AI Workflow Lab"
7. No pagination on list endpoints
8. No rate limiting
9. Duplicate schemas (UserResponse in auth + users)

### Reusable Modules
- **auth/** — Full JWT auth system (reuse as-is)
- **database/** — Session management (extend, don't replace)
- **workspaces/** — Ownership isolation pattern (reuse pattern)
- **logs/** — Simple log model (extend for new observability)

### Modules Needing Extension
- **workflows/** → PipelineTemplates (new engine alongside)
- **jobs/** → PipelineExecutions + NodeExecutions (evolution)
- **dashboard/** → Extended stats (projects, executions, token usage)
- **templates/** → New SignalForge screens (extend, don't replace)

### Modules to Keep Untouched Unless Necessary
- **auth/** — Fully functional, no changes needed
- **database/database.py** — Session management, minor extension only

---

## Migration Strategy: Option B

**Maintain legacy API + introduce new SignalForge engine alongside.**

Legacy entities (Workspace, Workflow, Job, Log) remain fully operational.
New entities are added as separate tables with their own service layer.
The frontend adds new pages alongside existing ones.

This is the safest approach because:
- Zero risk to existing functionality
- Existing tests continue passing without modification
- Users can transition gradually
- Easy rollback if needed

---

## New Domain Model (12 entities)

See architecture plan below.

---

## Implementation Plan

1. ✅ Audit repo + run baseline tests (34/34 pass)
2. ⬜ Rename product to SignalForge (config, main.py, templates)
3. ⬜ Add config for encryption + Alembic setup
4. ⬜ Create new module directories and __init__ files
5. ⬜ Add 12 new data models
6. ⬜ Create Alembic migration
7. ⬜ Build provider abstraction
8. ⬜ Build agent/tool registry
9. ⬜ Build source documents + ground truth registry
10. ⬜ Build pipeline graph model + validator
11. ⬜ Build context compiler
12. ⬜ Build execution engine + durable worker
13. ⬜ Build validators + scoring
14. ⬜ Seed Upwork template
15. ⬜ Build approval gates
16. ⬜ Build artifacts + exports
17. ⬜ Extend API routes
18. ⬜ Extend frontend
19. ⬜ Add demo seed
20. ⬜ Run full tests + fix regressions
21. ⬜ Update documentation
22. ⬜ Run end-to-end mocked demo
