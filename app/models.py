# Import all models so Alembic and init_db() discover them
from app.auth.models import User  # noqa: F401
from app.workspaces.models import Workspace  # noqa: F401
from app.workflows.models import Workflow  # noqa: F401
from app.jobs.models import Job  # noqa: F401
from app.logs.models import Log  # noqa: F401
from app.providers.models import ProviderConnection  # noqa: F401
from app.agents.models import AgentDefinition  # noqa: F401
from app.agents.prompt_versions import PromptTemplateVersion  # noqa: F401
from app.tools.models import ToolDefinition  # noqa: F401
from app.sources.models import SourceDocument  # noqa: F401
from app.registries.models import GroundTruthRegistry  # noqa: F401
from app.pipeline_templates.models import PipelineTemplate  # noqa: F401
from app.executions.models import PipelineExecution  # noqa: F401
from app.execution_nodes.models import NodeExecution  # noqa: F401
from app.artifacts.models import Artifact  # noqa: F401
from app.approvals.models import ApprovalRequest  # noqa: F401
from app.projects.models import OpportunityProject  # noqa: F401
