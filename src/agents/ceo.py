import anthropic
from src.types import WorkflowContext, AgentTask, TaskStatus
from src.config import Config

CEO_SYSTEM_PROMPT = """You are the CEO of a white paper production company.
Your job: given a research topic, produce:
1. A concise set of objectives (3-5 bullet points) for the white paper.
2. A task brief for the Researcher (what to investigate, which knowledge areas to cover).
3. A task brief for the Publisher (what tone, structure, and format to use for the white paper).
4. A task brief for the Reviewer (what quality standards to apply when reviewing the white paper).
5. A task brief for the Mailer (who to send the approved white paper to).

Respond in exactly this format:
OBJECTIVES:
<bullet points>

RESEARCHER TASK:
<task brief>

PUBLISHER TASK:
<task brief>

REVIEWER TASK:
Review the white paper against the stated objectives and confirm it meets executive standards.

MAILER TASK:
Send the approved white paper PDF to the configured recipient email address.
"""


def run_ceo(ctx: WorkflowContext, config: Config) -> WorkflowContext:
    """Calls Claude API to interpret the topic, write objectives, and create tasks."""
    print("[CEO] Interpreting topic and defining objectives...")
    client = anthropic.Anthropic(api_key=config.anthropic_api_key)

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        system=CEO_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Topic: {ctx.topic}"},
        ],
    )

    response_text = message.content[0].text

    # Parse objectives and task briefs from structured response
    objectives, researcher_brief, publisher_brief, reviewer_brief, mailer_brief = _parse_ceo_response(response_text)

    ctx.objectives = objectives
    ctx.tasks = [
        AgentTask(agent="researcher", instructions=researcher_brief),
        AgentTask(agent="publisher", instructions=publisher_brief),
        AgentTask(agent="reviewer", instructions=reviewer_brief),
        AgentTask(agent="mailer", instructions=mailer_brief),
    ]

    print(f"[CEO] Objectives defined:\n{objectives}")
    print(f"[CEO] Delegated {len(ctx.tasks)} tasks to the team.")
    return ctx


def _parse_ceo_response(text: str) -> tuple[str, str, str, str, str]:
    """Extract objectives, researcher brief, publisher brief, reviewer brief, and mailer brief from CEO response."""
    objectives = ""
    researcher_brief = ""
    publisher_brief = ""
    reviewer_brief = ""
    mailer_brief = ""

    current_section = None
    lines_buffer: list[str] = []

    for line in text.splitlines():
        if line.startswith("OBJECTIVES:"):
            current_section = "objectives"
            lines_buffer = []
        elif line.startswith("RESEARCHER TASK:"):
            objectives = "\n".join(lines_buffer).strip()
            current_section = "researcher"
            lines_buffer = []
        elif line.startswith("PUBLISHER TASK:"):
            researcher_brief = "\n".join(lines_buffer).strip()
            current_section = "publisher"
            lines_buffer = []
        elif line.startswith("REVIEWER TASK:"):
            publisher_brief = "\n".join(lines_buffer).strip()
            current_section = "reviewer"
            lines_buffer = []
        elif line.startswith("MAILER TASK:"):
            reviewer_brief = "\n".join(lines_buffer).strip()
            current_section = "mailer"
            lines_buffer = []
        else:
            lines_buffer.append(line)

    # Capture the last section
    if current_section == "mailer":
        mailer_brief = "\n".join(lines_buffer).strip()
    elif current_section == "reviewer":
        reviewer_brief = "\n".join(lines_buffer).strip()
    elif current_section == "publisher":
        publisher_brief = "\n".join(lines_buffer).strip()
    elif current_section == "researcher":
        researcher_brief = "\n".join(lines_buffer).strip()
    elif current_section == "objectives":
        objectives = "\n".join(lines_buffer).strip()

    # Fallback: if parsing fails, use full text as objectives
    if not objectives:
        objectives = text.strip()
    if not researcher_brief:
        researcher_brief = f"Research the topic: {text[:200]}"
    if not publisher_brief:
        publisher_brief = "Produce a professional 2-2.5 page white paper from the research."
    if not reviewer_brief:
        reviewer_brief = "Review the white paper against the stated objectives and confirm it meets executive standards."
    if not mailer_brief:
        mailer_brief = "Send the approved white paper PDF to the configured recipient email address."

    return objectives, researcher_brief, publisher_brief, reviewer_brief, mailer_brief


def _assign_section(section: str, lines: list[str],
                    objectives: str, researcher: str, publisher: str) -> None:
    pass  # helper only used for side-effect flow — assignments done inline above


REVIEWER_SYSTEM_PROMPT = """You are the CEO of a white paper production company acting as quality reviewer.
Given a topic, objectives, and a research summary, decide if a white paper produced from this content
would meet professional executive standards and clearly address all stated objectives.

Respond in exactly this format:
APPROVED
<1-2 sentences of positive confirmation explaining why the content meets standards>

or:
REJECTED
<1-2 sentences explaining what falls short and what would need improvement>

Do not include any other text before or after. The first line must be exactly APPROVED or REJECTED."""


def run_reviewer(ctx: WorkflowContext, config: Config) -> WorkflowContext:
    """Calls Claude API to review whether the white paper meets the stated objectives."""
    client = anthropic.Anthropic(api_key=config.anthropic_api_key)

    user_message = (
        f"Topic: {ctx.topic}\n\n"
        f"Objectives:\n{ctx.objectives}\n\n"
        f"Research summary (first 2000 chars):\n{ctx.research_output[:2000]}"
    )

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=256,
        system=REVIEWER_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_message},
        ],
    )

    response_text = message.content[0].text.strip()
    lines = response_text.splitlines()
    verdict = lines[0].strip().upper() if lines else ""
    feedback = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

    ctx.review_approved = verdict == "APPROVED"
    ctx.review_feedback = feedback

    status = "APPROVED" if ctx.review_approved else "REJECTED"
    print(f"[CEO Reviewer] Review complete. {status}: {ctx.review_feedback[:100]}")

    return ctx
