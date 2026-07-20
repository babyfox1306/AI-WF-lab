"""Seed demo data for SignalForge demonstration.

Usage:
    python -m app.seed_demo

Creates a demo user, workspace, mock provider, agents, Upwork pipeline template,
and a sample Upwork opportunity project with source documents.
"""

import json
import logging
from datetime import datetime, timezone

from app.auth.service import hash_password
from app.auth.models import User
from app.database.database import SessionLocal, init_db
from app.providers.models import ProviderConnection
from app.projects.models import OpportunityProject
from app.sources.models import SourceDocument
from app.pipeline_templates.models import PipelineTemplate

logger = logging.getLogger("signalforge.seed")


def seed_demo(workspace_name: str = "Demo Workspace") -> None:
    """Seed the database with demo data."""
    db = SessionLocal()
    try:
        init_db()

        # Check if demo user exists
        existing = db.query(User).filter(User.email == "demo@signalforge.io").first()
        if existing:
            logger.info("Demo data already exists. Skipping.")
            return

        # 1. Create demo user
        demo_user = User(
            email="demo@signalforge.io",
            username="demo",
            hashed_password=hash_password("demo123"),
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        db.add(demo_user)
        db.flush()
        logger.info(f"Created user: demo@signalforge.io / demo123")

        # 2. Create demo workspace
        from app.workspaces.models import Workspace
        ws = Workspace(name=workspace_name, owner_id=demo_user.id)
        db.add(ws)
        db.flush()

        # 3. Create mock provider
        provider = ProviderConnection(
            owner_id=demo_user.id,
            name="Mock Provider (Demo)",
            provider_type="openai_compatible",
            base_url="http://mock.local/v1",
            encrypted_api_key=None,
            default_model="mock-model-v1",
            timeout_seconds=30,
            is_active=True,
        )
        db.add(provider)
        db.flush()

        # 4. Create Upwork pipeline template
        system_template = PipelineTemplate(
            workspace_id=None,  # System template
            name="Upwork Opportunity Assessment v1",
            slug="upwork-opportunity-assessment-v1",
            description="Assess an Upwork job posting and produce a bid/no-bid recommendation with proposal.",
            version=1,
            is_system=True,
            graph_definition=json.dumps({
                "nodes": [
                    {"key": "start", "name": "Start", "node_type": "start", "config": {}},
                    {"key": "source_validator", "name": "Source Validator", "node_type": "validator",
                     "config": {"check_required_inputs": ["job_post", "client_metrics"]}},
                    {"key": "brief_extractor", "name": "Brief Extractor", "node_type": "agent",
                     "config": {"role": "You extract structured job briefs from Upwork posts.",
                                "output_schema": {"type": "object", "properties": {
                                    "title": {"type": "string"},
                                    "client_goal": {"type": "string"},
                                    "deliverables": {"type": "array", "items": {"type": "string"}},
                                    "required_skills": {"type": "array", "items": {"type": "string"}},
                                    "budget": {"type": "object"},
                                    "timeline": {"type": "object"},
                                    "unknowns": {"type": "array", "items": {"type": "string"}},
                                }}}},
                    {"key": "ground_truth_review", "name": "Ground Truth Review Gate", "node_type": "approval",
                     "config": {"prompt": "Review the extracted brief and ground truth facts before analysis."}},
                    {"key": "client_analyst", "name": "Client Quality Analyst", "node_type": "agent",
                     "config": {"role": "You analyze client quality from job post and metrics.",
                                "output_schema": {"type": "object", "properties": {
                                    "quality_score": {"type": "number"},
                                    "positive_signals": {"type": "array", "items": {"type": "string"}},
                                    "risk_flags": {"type": "array", "items": {"type": "string"}},
                                }}}},
                    {"key": "tech_analyst", "name": "Technical Fit Analyst", "node_type": "agent",
                     "config": {"role": "You analyze technical fit between job requirements and portfolio.",
                                "output_schema": {"type": "object", "properties": {
                                    "fit_score": {"type": "number"},
                                    "matched_requirements": {"type": "array", "items": {"type": "string"}},
                                    "gaps": {"type": "array", "items": {"type": "string"}},
                                }}}},
                    {"key": "risk_critic", "name": "Competition & Risk Critic", "node_type": "agent",
                     "config": {"role": "You assess competition level and delivery risks."}},
                    {"key": "evidence_mapper", "name": "Portfolio Evidence Mapper", "node_type": "agent",
                     "config": {"role": "You map portfolio evidence to job requirements."}},
                    {"key": "bid_synthesizer", "name": "Bid Decision Synthesizer", "node_type": "agent",
                     "config": {"role": "You synthesize all analyses into a bid/no-bid decision."}},
                    {"key": "proposal_writer", "name": "Proposal Writer", "node_type": "agent",
                     "config": {"role": "You write a tailored proposal based on evidence."}},
                    {"key": "machine_validator", "name": "Machine Validation", "node_type": "validator",
                     "config": {"rules": ["required_fields", "json_schema", "forbidden_phrase", "unsupported_claim"]}},
                    {"key": "final_reviewer", "name": "Final AI Reviewer", "node_type": "agent",
                     "config": {"role": "You review the final assessment for quality and completeness."}},
                    {"key": "human_approval", "name": "Human Approval Gate", "node_type": "approval",
                     "config": {"prompt": "Review the final assessment package before delivery."}},
                    {"key": "export", "name": "Decision Package Export", "node_type": "output", "config": {}},
                    {"key": "end", "name": "End", "node_type": "output", "config": {}},
                ],
                "edges": [
                    {"source": "start", "target": "source_validator"},
                    {"source": "source_validator", "target": "brief_extractor"},
                    {"source": "brief_extractor", "target": "ground_truth_review"},
                    {"source": "ground_truth_review", "target": "client_analyst"},
                    {"source": "ground_truth_review", "target": "tech_analyst"},
                    {"source": "client_analyst", "target": "risk_critic"},
                    {"source": "tech_analyst", "target": "risk_critic"},
                    {"source": "risk_critic", "target": "evidence_mapper"},
                    {"source": "evidence_mapper", "target": "bid_synthesizer"},
                    {"source": "bid_synthesizer", "target": "proposal_writer"},
                    {"source": "proposal_writer", "target": "machine_validator"},
                    {"source": "machine_validator", "target": "final_reviewer"},
                    {"source": "final_reviewer", "target": "human_approval"},
                    {"source": "human_approval", "target": "export"},
                    {"source": "export", "target": "end"},
                ],
            }),
        )
        db.add(system_template)
        db.flush()

        # 5. Create sample Upwork project
        project = OpportunityProject(
            workspace_id=ws.id,
            name="Upwork - AI Chatbot for E-commerce",
            project_type="upwork_opportunity",
            status="draft",
            description="Sample Upwork opportunity: Build an AI-powered customer support chatbot for an e-commerce store.",
            created_by=demo_user.id,
        )
        db.add(project)
        db.flush()

        # 6. Create sample source documents
        job_post = SourceDocument(
            workspace_id=ws.id,
            project_id=project.id,
            source_type="job_post",
            title="Job Post: AI Chatbot Developer",
            raw_text="""We need an experienced AI developer to build a customer support chatbot for our Shopify store.
We handle 500+ customer inquiries daily and want to automate responses for order status, returns, and product questions.

Budget: $5,000-$8,000
Timeline: 4-6 weeks
Required Skills: Python, OpenAI API, Shopify API, NLP
Preferred: Experience with LangChain, vector databases, RAG systems

We've tried a simple rule-based bot before but it couldn't handle the variety of questions.""",
            checksum=SourceDocument.compute_checksum("Job Post Text"),
            created_by=demo_user.id,
        )
        db.add(job_post)

        client_metrics = SourceDocument(
            workspace_id=ws.id,
            project_id=project.id,
            source_type="client_metrics",
            title="Client Stats",
            raw_text="""Client History:
- Total Spent on Upwork: $120,000+
- Previous Hires: 15 freelancers
- Average Rating Given: 4.8
- Payment Verified: Yes
- Member Since: 2019
- Country: United States
- Past Projects: Similar chatbot projects for 3 other stores""",
            checksum=SourceDocument.compute_checksum("Client Stats"),
            created_by=demo_user.id,
        )
        db.add(client_metrics)

        portfolio1 = SourceDocument(
            workspace_id=ws.id,
            project_id=project.id,
            source_type="portfolio_item",
            title="Portfolio: n8n Lead Pipeline",
            raw_text="""Built an automated lead qualification pipeline using n8n, OpenAI, and Airtable.
Processed 10,000+ leads/month, reduced manual qualification time by 80%.
Integrated with Salesforce for seamless CRM updates.""",
            checksum=SourceDocument.compute_checksum("Portfolio 1"),
            created_by=demo_user.id,
        )
        db.add(portfolio1)

        portfolio2 = SourceDocument(
            workspace_id=ws.id,
            project_id=project.id,
            source_type="portfolio_item",
            title="Portfolio: Shopify AI Assistant",
            raw_text="""Developed an AI-powered customer service assistant for a Shopify store handling 1,000+ daily inquiries.
Implemented context-aware responses using LangChain + Pinecone vector database.
Integrated with Shopify API for order lookups and inventory checks.""",
            checksum=SourceDocument.compute_checksum("Portfolio 2"),
            created_by=demo_user.id,
        )
        db.add(portfolio2)

        db.commit()
        logger.info("Demo data created successfully!")
        logger.info(f"  User:     demo@signalforge.io / demo123")
        logger.info(f"  Workspace: {ws.name}")
        logger.info(f"  Project:  {project.name}")
        logger.info(f"  Template: {system_template.name}")
        logger.info(f"  Provider: Mock Provider (no API key needed)")
        logger.info(f"  Sources:  1 job post, 1 client metrics, 2 portfolio items")

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to seed demo data: {e}", exc_info=True)
        raise
    finally:
        db.close()


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
    seed_demo()
    print("\n✅ Demo data seeded successfully!")
    print("   Login: demo@signalforge.io / demo123")
    print("   Start the API: uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()
