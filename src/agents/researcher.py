import anthropic
from src.types import WorkflowContext, AgentTask, TaskStatus
from src.config import Config

RESEARCHER_SYSTEM_PROMPT = """You are a research analyst specializing in producing structured white paper research.

Given a topic, produce a comprehensive research report covering exactly these 5 knowledge areas.
Each section must have 2-3 substantive paragraphs with enough depth to support a 2-2.5 page white paper.

Format your response as markdown with these exact section headers:

## Background & History
<2-3 paragraphs covering origins, historical context, and evolution>

## Current State & Key Players
<2-3 paragraphs covering the present landscape, major organizations, and leading contributors>

## Technical Foundations
<2-3 paragraphs covering the core technical concepts, methodologies, and underlying mechanisms>

## Challenges & Controversies
<2-3 paragraphs covering open problems, debates, limitations, and ethical concerns>

## Future Outlook & Implications
<2-3 paragraphs covering projected developments, potential impact, and strategic considerations>

Do not include any text before the first ## header. Use the exact header names as shown above.
Write in a professional, authoritative tone suitable for an executive white paper audience.
"""


def run_researcher(ctx: WorkflowContext, config: Config) -> WorkflowContext:
    """Calls Claude API to investigate the topic across 5 knowledge areas and produce structured markdown."""
    print("[Researcher] Investigating topic across 5 knowledge areas...")

    client = anthropic.Anthropic(api_key=config.anthropic_api_key)

    # Find researcher task brief from CEO-delegated tasks
    researcher_task = next(
        (t for t in ctx.tasks if t.agent == "researcher"),
        None,
    )

    if researcher_task:
        user_message = (
            f"Topic: {ctx.topic}\n\nResearcher instructions: {researcher_task.instructions}"
        )
    else:
        user_message = f"Topic: {ctx.topic}"

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=3000,
        system=RESEARCHER_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_message},
        ],
    )

    raw_text = message.content[0].text
    parsed_research = _parse_research_response(raw_text)

    ctx.research_output = parsed_research

    print(
        f"[Researcher] Research complete. {len(ctx.research_output)} chars across 5 knowledge areas."
    )
    return ctx


def _parse_research_response(text: str) -> str:
    """Validate that all 5 section headers are present. Return cleaned markdown string.

    If any section is missing, prepend a warning comment but still return the text
    (partial research is better than nothing).
    """
    required_sections = [
        "## Background",
        "## Current State",
        "## Technical",
        "## Challenges",
        "## Future",
    ]

    text_lower = text.lower()
    missing = []
    for section in required_sections:
        if section.lower() not in text_lower:
            missing.append(section)

    if missing:
        warning = (
            f"<!-- WARNING: Missing expected sections: {', '.join(missing)} -->\n\n"
        )
        return warning + text

    return text
