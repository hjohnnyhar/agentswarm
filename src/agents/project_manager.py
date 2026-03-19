from src.types import WorkflowContext, AgentTask, TaskStatus
from src.config import Config


def run_project_manager(ctx: WorkflowContext, config: Config) -> WorkflowContext:
    """
    Tracks Researcher and Publisher tasks to completion.
    Phase 2: real agent calls dispatch to Researcher and Publisher.
    """
    print("[PM] Starting task tracking...")
    print(f"[PM] {len(ctx.tasks)} tasks delegated by CEO.")

    for task in ctx.tasks:
        task.status = TaskStatus.IN_PROGRESS
        print(f"[PM] {task.agent.upper()} task started.")

        # Phase 2: real agent dispatch
        if task.agent == "researcher":
            from src.agents.researcher import run_researcher
            ctx = run_researcher(ctx, config)
            task.result = f"Research complete. {len(ctx.research_output)} chars."
        elif task.agent == "publisher":
            from src.agents.publisher import run_publisher
            ctx = run_publisher(ctx, config)
            task.result = f"PDF published at: {ctx.published_pdf_path}"

        task.status = TaskStatus.COMPLETE
        print(f"[PM] {task.agent.upper()} task COMPLETE.")

    _print_status_report(ctx)
    return ctx


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
