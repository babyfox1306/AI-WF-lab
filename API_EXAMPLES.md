# SignalForge API Examples

## Authentication

### Register a new user

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepassword123"
  }'
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "is_active": true,
  "created_at": "2026-07-20T10:00:00"
}
```

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

## Provider Setup

### Add an OpenAI-compatible provider

```bash
curl -X POST http://localhost:8000/providers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "My OpenAI Gateway",
    "provider_type": "openai_compatible",
    "base_url": "http://localhost:20128/v1",
    "api_key": "sk-your-api-key-here",
    "default_model": "gpt-4o-mini",
    "timeout_seconds": 120,
    "is_active": true
  }'
```

**Response:**
```json
{
  "id": 1,
  "name": "My OpenAI Gateway",
  "provider_type": "openai_compatible",
  "base_url": "http://localhost:20128/v1",
  "masked_api_key": "sk-yo****ere",
  "default_model": "gpt-4o-mini",
  "timeout_seconds": 120,
  "is_active": true,
  "created_at": "2026-07-20T10:00:00"
}
```

### Add an Ollama provider

```bash
curl -X POST http://localhost:8000/providers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Local Ollama",
    "provider_type": "ollama",
    "base_url": "http://localhost:11434",
    "api_key": "",
    "default_model": "llama3.2",
    "timeout_seconds": 120,
    "is_active": true
  }'
```

### Test provider connection

```bash
curl -X POST http://localhost:8000/providers/1/test \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "message": "Connected",
  "models": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"]
}
```

## Create an Opportunity Project

### Create project

```bash
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "workspace_id": 1,
    "name": "Upwork: Build E-commerce Platform",
    "project_type": "upwork_opportunity",
    "description": "Client needs an e-commerce platform with React + Node.js"
  }'
```

**Response:**
```json
{
  "id": 1,
  "workspace_id": 1,
  "name": "Upwork: Build E-commerce Platform",
  "project_type": "upwork_opportunity",
  "status": "draft",
  "description": "Client needs an e-commerce platform with React + Node.js",
  "created_at": "2026-07-20T10:00:00"
}
```

### Add source documents

```bash
# Add a job post
curl -X POST http://localhost:8000/projects/1/sources \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "source_type": "job_post",
    "title": "Job Post",
    "raw_text": "We need an experienced full-stack developer...",
    "structured_data": {}
  }'

# Add client metrics
curl -X POST http://localhost:8000/projects/1/sources \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "source_type": "client_metrics",
    "title": "Client Profile",
    "raw_text": "Client has 5-star rating, $50k+ total spent...",
    "structured_data": {}
  }'

# Add portfolio evidence
curl -X POST http://localhost:8000/projects/1/sources \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "source_type": "portfolio_item",
    "title": "Previous E-commerce Project",
    "raw_text": "Built a similar platform using React + Node.js + Stripe...",
    "structured_data": {}
  }'
```

## Ground Truth Registry

### View extracted facts

```bash
curl -X GET http://localhost:8000/projects/1/registry \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
[
  {
    "id": 1,
    "project_id": 1,
    "key": "job.required_skills",
    "value": {"skills": ["React", "Node.js", "PostgreSQL"]},
    "category": "job_requirement",
    "confidence": 0.95,
    "locked": false
  }
]
```

### Lock a fact (after review)

```bash
curl -X PUT http://localhost:8000/projects/1/registry/1/lock \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"locked": true}'
```

## Start Pipeline Execution

```bash
curl -X POST http://localhost:8000/projects/1/executions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "pipeline_template_id": 1
  }'
```

**Response:**
```json
{
  "id": 1,
  "project_id": 1,
  "status": "queued",
  "pipeline_template_id": 1,
  "template_version": 1
}
```

## Resolve Approval

### View pending approvals

```bash
curl -X GET http://localhost:8000/approvals?status=pending \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Approve or reject

```bash
# Approve
curl -X POST http://localhost:8000/approvals/1/resolve \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "decision": "approved",
    "comment": "Looks good, continue with the analysis."
  }'

# Reject
curl -X POST http://localhost:8000/approvals/1/resolve \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "decision": "rejected",
    "comment": "The analysis is incomplete. Please add more details."
  }'

# Request changes
curl -X POST http://localhost:8000/approvals/1/resolve \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "decision": "changes_requested",
    "comment": "Please update the technical fit section with more details."
  }'
```

## Retrieve Results

### View artifacts

```bash
curl -X GET http://localhost:8000/projects/1/artifacts \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### View execution history

```bash
curl -X GET http://localhost:8000/executions/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### View node executions

```bash
curl -X GET http://localhost:8000/executions/1/nodes \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Export Decision Package

### JSON export

```bash
curl -X GET "http://localhost:8000/projects/1/exports?format=json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o decision-package.json
```

### Markdown export

```bash
curl -X GET "http://localhost:8000/projects/1/exports?format=markdown" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o decision-package.md
```

### Plain text proposal

```bash
curl -X GET "http://localhost:8000/projects/1/exports?format=proposal" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o proposal.txt
```

## Demo Seed Data

```bash
# Create demo data with mock provider
python -m app.seed_demo

# Run the execution worker
python -m app.worker.runner
```

## Dashboard

```bash
curl -X GET http://localhost:8000/dashboard/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "total_workflows": 10,
  "running_jobs": 2,
  "completed_jobs": 15,
  "failed_jobs": 1,
  "recent_activity": [...]
}
```

## Full End-to-End Flow

```bash
# 1. Register
TOKEN=$(curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@test.com","username":"demo","password":"test123"}' | \
  python -c "import sys,json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

# 2. Create workspace
WS_ID=$(curl -s -X POST http://localhost:8000/workspaces/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"My Workspace"}' | \
  python -c "import sys,json; print(json.load(sys.stdin)['id'])")

# 3. Add provider
PROV_ID=$(curl -s -X POST http://localhost:8000/providers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"Mock","provider_type":"openai_compatible","base_url":"http://mock","api_key":"test","is_active":true}' | \
  python -c "import sys,json; print(json.load(sys.stdin)['id'])")

# 4. Create project
PROJ_ID=$(curl -s -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"workspace_id\":$WS_ID,\"name\":\"Test Project\",\"project_type\":\"upwork_opportunity\"}" | \
  python -c "import sys,json; print(json.load(sys.stdin)['id'])")

# 5. Start execution
EXEC_ID=$(curl -s -X POST http://localhost:8000/projects/$PROJ_ID/executions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"pipeline_template_id":1}' | \
  python -c "import sys,json; print(json.load(sys.stdin)['id'])")

# 6. Run worker (in another terminal)
# python -m app.worker.runner
```
