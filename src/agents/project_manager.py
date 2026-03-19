from src.types import WorkflowContext, AgentTask, TaskStatus
from src.config import Config


def run_project_manager(ctx: WorkflowContext, config: Config) -> WorkflowContext:
    """
    Tracks Researcher and Publisher tasks to completion.
    Phase 1: agent calls are stubs that immediately mark tasks COMPLETE.
    Phase 2 will replace stubs with real agent implementations.
    """
    print("[PM] Starting task tracking...")
    print(f"[PM] {len(ctx.tasks)} tasks delegated by CEO.")

    for task in ctx.tasks:
        task.status = TaskStatus.IN_PROGRESS
        print(f"[PM] {task.agent.upper()} task started.")

        # Phase 1 stub — Phase 2 replaces this block
        if task.agent == "researcher":
            task.result = _stub_researcher(task, ctx)
        elif task.agent == "publisher":
            task.result = _stub_publisher(task, ctx)

        task.status = TaskStatus.COMPLETE
        print(f"[PM] {task.agent.upper()} task COMPLETE.")

    _print_status_report(ctx)
    return ctx


def _stub_researcher(task: AgentTask, ctx: WorkflowContext) -> str:
    """Placeholder. Phase 2 will call the real Researcher agent here."""
    print(f"  [Researcher STUB] Would research: {ctx.topic!r}")
    return f"[STUB] Research complete for topic: {ctx.topic}"


def _stub_publisher(task: AgentTask, ctx: WorkflowContext) -> str:
    """Placeholder. Phase 2 will call the real Publisher agent here."""
    print(f"  [Publisher STUB] Would publish white paper for: {ctx.topic!r}")
    return "[STUB] PDF generated at output/whitepaper.pdf"


def _print_status_report(ctx: WorkflowContext) -> None:
    """Print a summary of all task statuses — PM's visibility guarantee."""
    print("\n[PM] STATUS REPORT")
    print(f"  Topic: {ctx.topic}")
    all_complete = all(t.status == TaskStatus.COMPLETE for t in ctx.tasks)
    for t in ctx.tasks:
        icon = "v" if t.status == TaskStatus.COMPLETE else "x"
        print(f"  [{icon}] {t.agent.upper()}: {t.status.value}")
    if all_complete:
        print("[PM] All tasks complete. Workflow ready for Phase 2 (review & delivery).")
    else:
        failed = [t for t in ctx.tasks if t.status == TaskStatus.FAILED]
        print(f"[PM] WARNING: {len(failed)} task(s) failed.")
