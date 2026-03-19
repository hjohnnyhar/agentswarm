import argparse
import sys
from src.types import WorkflowContext
from src.config import Config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="agentswarm",
        description="Generate a professional white paper via multi-agent orchestration.",
    )
    parser.add_argument(
        "--topic",
        required=True,
        metavar="TOPIC",
        help='Topic for the white paper, e.g. "AI in Healthcare"',
    )
    return parser.parse_args()


def run_workflow(topic: str) -> None:
    """Full agent workflow: CEO delegation -> PM tracking -> (Phase 2: research/publish)."""
    config = Config()
    ctx = WorkflowContext(topic=topic)

    print(f"[AgentSwarm] Workflow started for topic: {ctx.topic!r}")

    # Phase 1: CEO interprets and delegates
    from src.agents.ceo import run_ceo
    ctx = run_ceo(ctx, config)

    # Phase 1: PM tracks tasks (stubs for Researcher/Publisher until Phase 2)
    from src.agents.project_manager import run_project_manager
    ctx = run_project_manager(ctx, config)

    if ctx.published_pdf_path:
        print(f"\n[AgentSwarm] Workflow complete. White paper PDF: {ctx.published_pdf_path}")
    else:
        print("\n[AgentSwarm] Workflow complete. (No PDF path — check publisher output.)")
