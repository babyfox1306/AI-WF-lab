# SignalForge 🧠⚡

**AI Opportunity Intelligence Factory**

A multi-agent research and decision system for freelancers, consultants, founders, and small teams.

SignalForge runs structured, auditable AI pipelines. Feed in source material (job posts, client metrics, portfolio evidence) and get back decision packages with scored assessments, proposal drafts, and exportable reports.

---

## ✨ Features

### Core Pipeline
- **Source Intake** — Job posts, client metrics, portfolio evidence, project briefs
- **Ground Truth Registry** — Locked facts with provenance tracking
- **Multi-Agent Analysis** — Specialized AI agents extract, analyze, validate, and synthesize
- **Human Approval Gates** — Pause-and-resume at key decision points
- **Final Decision Package** — JSON, Markdown, or plain text export

### First Template: Upwork Opportunity Assessment
Analyzes an Upwork job post and produces:
- Structured job brief
- Client quality assessment
- Technical fit score
- Competition/risk assessment
- Portfolio evidence mapping
- Bid/no-bid recommendation
- Proposal draft
- Confidence score

### Technical Features
- ✅ JWT authentication with bcrypt password hashing
- ✅ Workspace isolation with resource-level authorization
- ✅ 17 database entities with Alembic migrations
- ✅ LLM provider abstraction (OpenAI, Ollama, OpenRouter)
- ✅ Fernet-encrypted API key storage
- ✅ Durable background execution worker with crash recovery
- ✅ Weighted scoring system with configurable thresholds
- ✅ Pipeline graph validation (cycle detection, topological sort)
- ✅ Comprehensive test suite (74 tests)
- ✅ Swagger UI at `/docs`
- ✅ Dark-mode SPA dashboard

---

## 🏗️ Architecture

```
app/
├── auth/              # JWT authentication & user management
├── users/             # User profiles
├── workspaces/        # Workspace CRUD
├── workflows/         # Legacy workflow pipeline definitions
├── jobs/              # Legacy job execution
├── logs/              # Execution logs
├── dashboard/         # Aggregated statistics
│
├── providers/         # LLM provider connections (encrypted keys)
├── agents/            # AI agent definitions (versioned)
├── tools/             # HTTP and internal tools
├── sources/           # Input material management
├── registries/        # Ground truth facts with provenance
├── projects/          # Opportunity projects
├── pipeline_templates/# Versioned pipeline graph definitions
├── executions/        # Pipeline execution state machine
├── execution_nodes/   # Per-node execution tracking
├── artifacts/         # Immutable output storage
├── approvals/         # Human-in-the-loop approval gates
├── compiler/          # Context assembly for agent nodes
├── scoring/           # Weighted score calculator
├── validators/        # Machine validation (schema, forbidden phrases)
├── exports/           # Decision package export (JSON, Markdown)
├── worker/            # Durable background execution worker
├── templates/         # Frontend SPA
└── main.py            # FastAPI entry point
```

---

## 💻 Quick Start

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

# 4. Copy environment config
cp .env.example .env
# Edit .env with your settings

# 5. Run database migrations
alembic upgrade head

# 6. (Optional) Seed demo data
python -m app.seed_demo

# 7. Run the server
uvicorn app.main:app --reload
```

### Access
- **Web App**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧪 Running Tests

```bash
pytest -v
```

**74 tests** covering:
- User registration & authentication (10 tests)
- Workspace CRUD & authorization (10 tests)
- Workflow management (5 tests)
- Job lifecycle & execution (4 tests)
- Dashboard statistics (3 tests)
- **Encryption** — Roundtrip, masking, key derivation (5 tests)
- **Graph validation** — Cycle detection, topological sort (9 tests)
- **State machines** — Valid/invalid transitions (2 tests)
- **Scoring** — Weighted calculation, boundaries, thresholds (10 tests)
- **Exports** — JSON, Markdown, plain text (5 tests)
- **Provider adapter** — Mock, connection, structured output (5 tests)
- **Authorization** — Workspace isolation pattern (1 test)
- **Model imports** — All 17 tables discovered (1 test)

---

## 🔌 Commands & Operations

| Command | Description |
|---------|-------------|
| `uvicorn app.main:app --reload` | Run API server |
| `python -m app.worker.runner` | Start execution worker |
| `alembic upgrade head` | Run database migrations |
| `alembic revision --autogenerate -m "message"` | Create new migration |
| `python -m app.seed_demo` | Create demo data |
| `pytest -v` | Run all tests |
| `pytest tests/test_signalforge.py -v` | Run SignalForge-specific tests |

---

## 🔌 LLM Provider Setup

### OpenAI / OpenRouter / OmniRoute

Configure a provider with:
```json
{
  "name": "My Provider",
  "provider_type": "openai_compatible",
  "base_url": "https://api.openai.com/v1",
  "api_key": "sk-...",
  "default_model": "gpt-4o-mini"
}
```

### Ollama

```json
{
  "name": "Local Ollama",
  "provider_type": "ollama",
  "base_url": "http://localhost:11434",
  "api_key": "",
  "default_model": "llama3.2"
}
```

### Mock Provider (for testing)

The demo seed uses the mock provider, which runs through the same provider abstraction and doesn't require any paid API.

---

## 🔐 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | SignalForge | Application name |
| `DATABASE_URL` | sqlite:///./signalforge.db | Database connection string |
| `SECRET_KEY` | (change me) | JWT signing key |
| `MASTER_ENCRYPTION_KEY` | (32 chars) | Fernet encryption key for API keys |
| `CORS_ORIGINS` | * | Allowed CORS origins |
| `WORKER_POLL_INTERVAL_SECONDS` | 2 | Worker polling interval |

---

## 📚 API Overview

| Resource | Endpoints | Purpose |
|----------|-----------|---------|
| Auth | `POST /auth/register`, `POST /auth/login` | User management |
| Workspaces | `GET/POST/PATCH/DELETE /workspaces/` | Workspace CRUD |
| Providers | `GET/POST/PATCH/DELETE /providers/` | LLM provider management |
| Projects | `GET/POST/PATCH /projects/` | Opportunity projects |
| Sources | `GET/POST/DELETE /projects/{id}/sources/` | Source documents |
| Registry | `GET/POST/PUT /projects/{id}/registry/` | Ground truth facts |
| Executions | `POST /projects/{id}/executions/` | Pipeline runs |
| Approvals | `GET /approvals/`, `POST /approvals/{id}/resolve` | Human approval gates |
| Exports | `GET /projects/{id}/exports` | Decision package export |

See [API_EXAMPLES.md](./API_EXAMPLES.md) for detailed usage.

---

## 📄 Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) — System architecture and component boundaries
- [API_EXAMPLES.md](./API_EXAMPLES.md) — Complete API usage examples
- [MIGRATION_NOTES.md](./MIGRATION_NOTES.md) — Migration strategy and backward compatibility
- [DEVELOPMENT_REPORT.md](./DEVELOPMENT_REPORT.md) — Full development report
- [AUDIT.md](./AUDIT.md) — Original repository audit

---

## 🔒 Security Notes

- API keys encrypted at rest using AES-256 (Fernet)
- Never expose decrypted keys in API responses
- Workspace-level resource isolation enforced in service layer
- HTTP tools restricted to prevent SSRF
- Authorization headers masked in logs
- CORS configurable (not wildcard in production)

---

## 🚧 Current Limitations

- SQLite (not production-ready for high concurrency)
- Single-worker execution (no Redis/Celery yet)
- Static frontend (no real-time updates)
- Mock provider returns short responses

---

## 🗺️ Roadmap

- [ ] PostgreSQL support with JSONB columns
- [ ] Real-time execution updates (WebSocket)
- [ ] Drag-and-drop pipeline builder
- [ ] OAuth2 and social login
- [ ] Billing and usage quotas
- [ ] Team collaboration with roles
- [ ] More pipeline templates (SaaS validation, competitor research)

---

## License

MIT
