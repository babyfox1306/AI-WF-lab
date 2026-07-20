# SignalForge Migration Notes

## Original Architecture (AI Workflow Lab)

The original project, **AI Workflow Lab**, was a SaaS MVP with:

- FastAPI backend with SQLAlchemy + SQLite
- JWT authentication with bcrypt
- 5 database entities: User, Workspace, Workflow, Job, Log
- Simple job execution with simulated AI processing
- Jinja2-based dark SPA dashboard
- 34 pytest tests

## Migration Strategy

### Strategy: Extend + Preserve

We chose **Strategy A** — extend existing entities as the lower-level execution primitives while adding new SignalForge entities alongside.

### Backward Compatibility Decisions

1. **Legacy entities preserved** — User, Workspace, Workflow, Job, Log remain unchanged
2. **Legacy endpoints preserved** — All original API endpoints continue to work
3. **Legacy tests preserved** — All 34 original tests pass without modification
4. **No forced remapping** — New SignalForge entities are proper new models, not forced into old ones
5. **Database file renamed** — From `ai_workflow_lab.db` to `signalforge.db`

### Database Migration Path

```bash
# Option 1: Fresh start with Alembic
mv ai_workflow_lab.db signalforge.db  # Rename if needed
alembic upgrade head

# Option 2: Complete reset
python -c "from app.database.database import init_db; init_db()"

# Option 3: Seed demo data
python -m app.seed_demo
```

## Entities Added

| Entity | Table | Purpose |
|--------|-------|---------|
| ProviderConnection | provider_connections | LLM provider config with encrypted API keys |
| AgentDefinition | agent_definitions | Reusable AI workers with versioning |
| PromptTemplateVersion | prompt_template_versions | Versioned prompt templates |
| ToolDefinition | tool_definitions | External/internal tools for agents |
| SourceDocument | source_documents | Input material with checksum dedup |
| GroundTruthRegistry | ground_truth_registry | Locked facts with provenance |
| OpportunityProject | opportunity_projects | Analysis target (e.g., Upwork opportunity) |
| PipelineTemplate | pipeline_templates | Versioned pipeline graph definitions |
| PipelineExecution | pipeline_executions | One pipeline run with status |
| NodeExecution | node_executions | Per-node execution tracking |
| Artifact | artifacts | Immutable intermediate/final outputs |
| ApprovalRequest | approval_requests | Human approval gates |

## Commit History

See `DEVELOPMENT_REPORT.md` for a complete file change log.

## Database Changes

### New Tables Created

All new tables use:
- `id` as auto-incrementing primary key
- `created_at` with server default timestamp
- `updated_at` where applicable
- Foreign keys with explicit cascade behavior
- Appropriate indexes on foreign keys and commonly queried columns

### Foreign Key Dependencies

```
provider_connections → users (owner_id)
agent_definitions → workspaces, provider_connections
tool_definitions → workspaces
source_documents → workspaces, opportunity_projects
ground_truth_registry → opportunity_projects, source_documents (optional)
opportunity_projects → workspaces
pipeline_templates → workspaces (nullable for system templates)
pipeline_executions → opportunity_projects, pipeline_templates
node_executions → pipeline_executions
artifacts → opportunity_projects, pipeline_executions, node_executions (optional)
approval_requests → pipeline_executions, node_executions
```

### PostgreSQL Compatibility

All new schemas avoid SQLite-only features:
- No `JSON` type (using `Text` with JSON serialization)
- Standard timestamp handling
- Explicit foreign key constraints
- String-based enums (not SQLite-specific enums)
