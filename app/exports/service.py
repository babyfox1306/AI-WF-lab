"""Export services for creating final decision packages."""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class ExportService:
    """Service for exporting decision packages in various formats."""

    def export_json(self, package: Dict[str, Any]) -> str:
        """Export decision package as formatted JSON."""
        return json.dumps(package, indent=2, default=str)

    def export_markdown(self, package: Dict[str, Any]) -> str:
        """Export decision package as a Markdown document."""
        lines = []
        meta = package.get("metadata", {})
        project = package.get("project", {})
        scorecard = package.get("scorecard", {})
        assessment = package.get("assessment", {})

        lines.append(f"# Decision Package: {project.get('name', 'Unknown Project')}")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now(timezone.utc).isoformat()}")
        lines.append(f"**Project Type:** {project.get('project_type', 'N/A')}")
        lines.append(f"**Status:** {package.get('status', 'N/A')}")
        if meta.get("generation_timestamp"):
            lines.append(f"**Generation Timestamp:** {meta['generation_timestamp']}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Source Summary
        sources = package.get("sources", [])
        lines.append("## Source Summary")
        lines.append("")
        if sources:
            for src in sources:
                lines.append(f"- **{src.get('title', 'Untitled')}** ({src.get('source_type', 'unknown')})")
        else:
            lines.append("_No sources provided._")
        lines.append("")

        # Scorecard
        lines.append("## Scorecard")
        lines.append("")
        lines.append(f"| Category | Score | Weight | Weighted |")
        lines.append(f"|----------|-------|--------|----------|")
        categories = scorecard.get("categories", {})
        weights = scorecard.get("weights", {})
        weighted = scorecard.get("weighted_scores", {})
        for cat in sorted(categories.keys()):
            s = categories.get(cat, 0)
            w = weights.get(cat, 0)
            ws = weighted.get(cat, 0)
            lines.append(f"| {cat.replace('_', ' ').title()} | {s} | {w:.0%} | {ws} |")
        lines.append(f"| **Total** | | | **{scorecard.get('total', 0)}** |")
        lines.append("")
        lines.append(f"**Decision:** {scorecard.get('decision', 'N/A').upper()}")
        lines.append("")

        # Bid Recommendation
        decision = scorecard.get("decision", "skip")
        assessment_data = assessment.get("bid_decision", {})
        lines.append("## Bid Recommendation")
        lines.append("")
        lines.append(f"**Decision:** {decision.replace('_', ' ').title()}")
        lines.append(f"**Overall Score:** {scorecard.get('total', 0)}/100")
        if assessment_data.get("reasons"):
            lines.append("")
            lines.append("### Reasons")
            for r in assessment_data["reasons"]:
                lines.append(f"- {r}")
        lines.append("")

        # Client Assessment
        client = assessment.get("client_quality", {})
        lines.append("## Client Assessment")
        lines.append("")
        lines.append(f"**Quality Score:** {client.get('quality_score', 'N/A')}")
        if client.get("positive_signals"):
            lines.append("")
            lines.append("### Positive Signals")
            for s in client["positive_signals"]:
                lines.append(f"- {s}")
        if client.get("risk_flags"):
            lines.append("")
            lines.append("### Risk Flags")
            for f in client["risk_flags"]:
                lines.append(f"- ⚠️ {f}")
        lines.append("")

        # Technical Fit
        tech = assessment.get("technical_fit", {})
        lines.append("## Technical Fit")
        lines.append("")
        lines.append(f"**Fit Score:** {tech.get('fit_score', 'N/A')}")
        if tech.get("matched_requirements"):
            lines.append("")
            lines.append("### Matched Requirements")
            for m in tech["matched_requirements"]:
                lines.append(f"- ✅ {m}")
        if tech.get("gaps"):
            lines.append("")
            lines.append("### Gaps")
            for g in tech["gaps"]:
                lines.append(f"- ❌ {g}")
        lines.append("")

        # Risks
        risks = assessment.get("competition_risk", {})
        lines.append("## Competition & Risk Assessment")
        lines.append("")
        lines.append(f"**Competition Level:** {risks.get('competition_level', 'unknown')}")
        if risks.get("delivery_risks"):
            lines.append("")
            lines.append("### Delivery Risks")
            for r in risks["delivery_risks"]:
                lines.append(f"- {r}")
        if risks.get("red_flags"):
            lines.append("")
            lines.append("### Red Flags")
            for r in risks["red_flags"]:
                lines.append(f"- 🚩 {r}")
        lines.append("")

        # Evidence Mapping
        evidence = assessment.get("evidence_mapping", {})
        lines.append("## Evidence Mapping")
        lines.append("")
        proof_items = evidence.get("proof_items", [])
        if proof_items:
            lines.append("| Requirement | Portfolio Fact | Strength |")
            lines.append("|-------------|----------------|----------|")
            for item in proof_items:
                lines.append(f"| {item.get('requirement', '')} | {item.get('portfolio_fact', '')} | {item.get('strength', '')} |")
        else:
            lines.append("_No evidence mapped._")
        if evidence.get("unsupported_claims_to_avoid"):
            lines.append("")
            lines.append("### Unsupported Claims to Avoid")
            for c in evidence["unsupported_claims_to_avoid"]:
                lines.append(f"- {c}")
        lines.append("")

        # Unanswered Questions
        questions = assessment.get("unanswered_questions", [])
        if questions:
            lines.append("## Unanswered Questions")
            lines.append("")
            for q in questions:
                lines.append(f"- {q}")
            lines.append("")

        # Proposal Draft
        proposal = package.get("proposal", {})
        proposal_text = proposal.get("proposal_text", "")
        if proposal_text:
            lines.append("## Proposal Draft")
            lines.append("")
            lines.append(proposal_text)
            lines.append("")

        # Provenance Summary
        provenance = package.get("provenance", [])
        if provenance:
            lines.append("## Provenance Summary")
            lines.append("")
            lines.append("| Claim | Type | Source | Confidence |")
            lines.append("|-------|------|--------|------------|")
            for p in provenance:
                lines.append(f"| {p.get('claim', '')} | {p.get('claim_type', '')} | {p.get('source_artifact_id', '')} | {p.get('confidence', '')} |")
            lines.append("")

        # Execution Metadata
        exec_meta = package.get("execution_metadata", {})
        lines.append("## Execution Metadata")
        lines.append("")
        lines.append(f"- **Execution ID:** {exec_meta.get('execution_id', 'N/A')}")
        lines.append(f"- **Template Version:** {exec_meta.get('template_version', 'N/A')}")
        lines.append(f"- **Status:** {exec_meta.get('status', 'N/A')}")
        lines.append(f"- **Started:** {exec_meta.get('started_at', 'N/A')}")
        lines.append(f"- **Finished:** {exec_meta.get('finished_at', 'N/A')}")
        lines.append(f"- **Token Usage:** {exec_meta.get('total_tokens', 0)}")
        lines.append("")

        lines.append("---")
        lines.append("")
        lines.append(f"*Decision Package generated by SignalForge at {datetime.now(timezone.utc).isoformat()}*")

        return "\n".join(lines)

    def export_plain_text_proposal(self, package: Dict[str, Any]) -> str:
        """Extract just the proposal text."""
        proposal = package.get("proposal", {})
        text = proposal.get("proposal_text", "")
        if not text and "assessment" in package:
            text = package.get("assessment", {}).get("proposal_writer", {}).get("proposal_text", "")
        return text or "No proposal available."

    def build_package(
        self,
        project: Dict,
        scorecard: Dict,
        assessment: Dict,
        sources: List[Dict],
        proposal: Optional[Dict] = None,
        provenance: Optional[List[Dict]] = None,
        execution_metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Build a complete decision package from components."""
        return {
            "metadata": {
                "generation_timestamp": datetime.now(timezone.utc).isoformat(),
                "format_version": "2.0",
                "exporter": "SignalForge Export Service",
            },
            "status": "final",
            "project": project,
            "sources": sources,
            "scorecard": scorecard,
            "assessment": assessment,
            "proposal": proposal or {},
            "provenance": provenance or [],
            "execution_metadata": execution_metadata or {},
        }
