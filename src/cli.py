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
    """Entry point for the full agent workflow. CEO delegation added in plan 02."""
    config = Config()
    ctx = WorkflowContext(topic=topic)
    print(f"[AgentSwarm] Workflow started for topic: {ctx.topic!r}")
    print("[AgentSwarm] CEO agent will delegate tasks — orchestration coming in plan 02.")
