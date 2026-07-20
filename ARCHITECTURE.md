# SignalForge Architecture

## Overview

SignalForge is a **multi-agent research and decision system** for freelancers, consultants, founders, and small teams. It provides a structured, auditable AI pipeline that transforms source material (job posts, client metrics, portfolio evidence) into actionable decision packages.

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                    FastAPI App                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  Auth     │  │  Users   │  │  Workspaces      │  │
│  ├──────────┤  ├──────────┤  ├──────────────────┤  │
│  │  Providers│  │  Agents  │  │  Tools           │  │
│  ├──────────┤  ├──────────┤  ├──────────────────┤  │
│  │  Sources  │  │ Registry │  │  PipelineTemplates│  │
│  ├──────────┤  ├──────────┤  ├──────────────────┤  │
│  │Execution │  │  Nodes   │  │  Artifacts       │  │
│  ├──────────┤  ├──────────┤  ├──────────────────┤  │
│  │Approvals │  │ Scoring  │  │  Exports         │  │
│  ├──────────┤  ├──────────┤  ├──────────────────┤  │
│  │ Dashboard│  │ Compiler │  │  Worker          │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │           Database (SQLite/PostgreSQL)       │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │   LLM Providers (OpenAI, Ollama, Mock)      │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## Component Boundaries

### 1. Authentication Layer (`app/auth/`)
- JWT-based authentication with bcrypt password hashing
- Token generation and validation
- Current user dependency injection

### 2. Domain Modules

Each domain module follows this pattern:
```
domain/
├── models.py     # SQLAlchemy ORM models
├── schemas.py    # Pydantic request/response schemas
├── service.py    # Business logic
├── routes.py     # FastAPI REST endpoints
└── __init__.py
```

### 3. Core SignalForge Modules

| Module | Purpose |
|--------|---------|
| **providers/** | LLM provider connections (OpenAI-compatible, Ollama) with encrypted API key storage |
| **agents/** | Reusable AI agent definitions with versioned prompts |
| **tools/** | External/internal tool definitions for agent use |
| **sources/** | Input material (job posts, client metrics, portfolio) |
| **registries/** | Ground-truth facts with provenance tracking |
| **pipeline_templates/** | Versioned pipeline graph definitions |
| **executions/** | Pipeline execution state machine (queued→running→completed/failed) |
| **execution_nodes/** | Per-node execution tracking with retry/attempt history |
| **artifacts/** | Immutable intermediate and final outputs |
| **approvals/** | Human-in-the-loop approval gates |
| **validators/** | Machine validation (JSON schema, forbidden phrases, contradictions) |
| **compiler/** | Context assembly for agent nodes (variables, registry, dependencies) |
| **scoring/** | Weighted score calculation with configurable thresholds |
| **exports/** | Decision package export (JSON, Markdown, plain text) |
| **worker/** | Durable background execution worker |

## Execution Engine

### State Machine

#### Pipeline Execution States
```
queued ──→ running ──→ completed
              │
              ├──→ failed
              │
              └──→ awaiting_approval ──→ running (on approval)
                                              │
                                              ├──→ completed
                                              │
                                              └──→ failed (on rejection)
```

#### Node Execution States
```
pending ──→ running ──→ completed
               │
               ├──→ failed (retryable → new attempt)
               │
               ├──→ skipped
               │
               └──→ cancelled
```

### Durable Worker

The background worker (`python -m app.worker.runner`):
1. Polls for queued executions
2. Atomically claims executions (with idempotency)
3. Processes nodes in topological order
4. Handles approval nodes by pausing execution
5. Recovers stale executions after crashes
6. Persists all progress before moving to the next node

## Context Compiler

The compiler assembles context for agent nodes:

1. **Resolve template variables** from project metadata
2. **Select dependency artifacts** from previous nodes
3. **Include relevant registry items** (locked facts)
4. **Inject forbidden claims** to prevent hallucination
5. **Enforce context-size limits**
6. **Produce deterministic compiled prompt record**
7. **Reject missing required variables** before calling a model

## Provider Adapter

Abstract interface for LLM providers:

```python
class BaseProviderAdapter(ABC):
    def test_connection(self) -> Tuple[bool, str, List[str]]: ...
    def generate(self, messages, **kwargs) -> ProviderResponse: ...
    def normalize_error(self, error) -> ProviderError: ...
    def normalize_usage(self, usage) -> Dict[str, int]: ...
```

### Implementations
- **OpenAICompatibleAdapter** - OpenAI, OpenRouter, OmniRoute, 9router, self-hosted gateways
- **OllamaAdapter** - Local Ollama HTTP API
- **MockProviderAdapter** - Deterministic mock for testing

### Error Categories & Retry Policy

| Category | Retryable? |
|----------|-----------|
| authentication_error | No |
| permission_error | No |
| rate_limit | Yes (exponential backoff + jitter) |
| timeout | Yes |
| connection_error | Yes |
| model_not_found | No |
| invalid_request | No |
| malformed_response | No |
| context_limit | No |
| unknown_provider_error | Varies |

## Scoring System

### Weighted Categories

| Category | Weight |
|----------|--------|
| Technical Fit | 30% |
| Proof Strength | 20% |
| Client Quality | 15% |
| Scope Clarity | 10% |
| Budget Fit | 10% |
| Competition Risk | 10% |
| Delivery Confidence | 5% |

### Decision Thresholds (configurable per workspace)
- **75–100**: Bid
- **55–74**: Conditional Bid
- **< 55**: Skip

## Security Model

1. **Authentication**: JWT tokens with configurable expiry
2. **Authorization**: Workspace-level resource isolation
3. **Encryption**: AES-256 (Fernet) for provider API keys
4. **Secrets masking**: API responses show only masked keys
5. **SSRF protection**: HTTP tools restricted from private networks
6. **Header masking**: Authorization headers masked in logs
7. **Input validation**: All identifiers validated via Pydantic
8. **CORS**: Configurable origins (not wildcard in production)

## Database Schema

### Legacy Entities (Preserved)
- User
- Workspace
- Workflow
- Job
- Log

### SignalForge Entities (New)
- ProviderConnection
- AgentDefinition
- PromptTemplateVersion
- ToolDefinition
- SourceDocument
- GroundTruthRegistry
- OpportunityProject
- PipelineTemplate
- PipelineExecution
- NodeExecution
- Artifact
- ApprovalRequest

## Migration Path

See [MIGRATION_NOTES.md](./MIGRATION_NOTES.md) for detailed migration strategy.

## Frontend Architecture

- Jinja2 templates with single-page application (SPA) architecture
- Vanilla JavaScript with fetch-based API client
- CSS custom properties for theming
- No build step required
- Mobile-responsive via CSS Grid and media queries
