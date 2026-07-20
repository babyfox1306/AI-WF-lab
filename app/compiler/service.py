"""Context compiler that assembles relevant information for each agent node."""

import hashlib
import json
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.config import settings


class ContextCompiler:
    """Compiles execution context for agent nodes from relevant sources."""

    def __init__(self, db: Session, project_id: int, execution_id: int):
        self.db = db
        self.project_id = project_id
        self.execution_id = execution_id

    def compile(
        self,
        node_config: Dict[str, Any],
        dependency_artifacts: Optional[List[Dict]] = None,
        registry_items: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """Compile the full context for a node execution."""
        context = {
            "project": self._get_project_metadata(),
            "agent_role": node_config.get("role", ""),
            "instructions": node_config.get("instructions", ""),
            "output_schema": node_config.get("output_schema", {}),
            "dependencies": self._prepare_dependencies(dependency_artifacts or []),
            "ground_truth": self._prepare_registry(registry_items),
            "forbidden_claims": self._get_forbidden_claims(registry_items),
            "unresolved_questions": self._get_unresolved_questions(registry_items),
        }
        return context

    def compile_with_checksum(self, **kwargs) -> tuple[Dict[str, Any], str]:
        """Compile context and return it with a deterministic checksum."""
        context = self.compile(**kwargs)
        checksum = self._compute_checksum(context)
        return context, checksum

    def _get_project_metadata(self) -> Dict[str, Any]:
        from app.projects.models import OpportunityProject
        project = (
            self.db.query(OpportunityProject)
            .filter(OpportunityProject.id == self.project_id)
            .first()
        )
        if not project:
            return {"id": self.project_id, "name": "Unknown", "status": "unknown"}
        return {
            "id": project.id,
            "name": project.name,
            "project_type": project.project_type,
            "status": project.status,
        }

    def _prepare_dependencies(self, artifacts: List[Dict]) -> List[Dict]:
        """Select relevant dependency artifacts."""
        prepared = []
        for art in artifacts:
            prepared.append({
                "artifact_type": art.get("artifact_type", "generic"),
                "name": art.get("name", ""),
                "content": art.get("content_json") or art.get("content_text", ""),
            })
        return prepared

    def _prepare_registry(self, items: Optional[List[Dict]]) -> List[Dict]:
        """Filter and format registry items for the prompt."""
        if not items:
            return []
        return [
            {
                "key": item.get("key", ""),
                "value": json.loads(item.get("value", "{}")) if isinstance(item.get("value"), str) else item.get("value"),
                "category": item.get("category", "unknown"),
                "confidence": item.get("confidence", 1.0),
                "locked": item.get("locked", False),
            }
            for item in items
            if item.get("key")  # Skip empty keys
        ]

    def _get_forbidden_claims(self, items: Optional[List[Dict]]) -> List[str]:
        """Extract forbidden claims from registry."""
        if not items:
            return []
        return [
            item.get("value", "") if isinstance(item.get("value"), str) else json.dumps(item.get("value", ""))
            for item in items
            if item.get("category") == "forbidden_claim"
        ]

    def _get_unresolved_questions(self, items: Optional[List[Dict]]) -> List[str]:
        """Get unresolved questions from registry."""
        if not items:
            return []
        return [
            item.get("value", "") if isinstance(item.get("value"), str) else json.dumps(item.get("value", ""))
            for item in items
            if item.get("category") == "unresolved_question"
        ]

    def enforce_context_limit(self, context: Dict[str, Any], max_chars: int = 100000) -> Dict[str, Any]:
        """Enforce context-size limits by truncating dependency content."""
        total = len(json.dumps(context))
        if total <= max_chars:
            return context

        # Truncate dependency text content first
        for dep in context.get("dependencies", []):
            content = dep.get("content", "")
            if isinstance(content, str) and len(content) > 5000:
                dep["content"] = content[:5000] + "\n...[truncated]"
        return context

    @staticmethod
    def _compute_checksum(data: Dict[str, Any]) -> str:
        raw = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
