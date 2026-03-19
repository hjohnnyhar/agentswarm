import os
import anthropic
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend — required on Windows without display
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

from src.types import WorkflowContext
from src.config import Config

PUBLISHER_SYSTEM_PROMPT = """You are a professional technical writer producing executive white papers.

Given research notes and objectives, write a polished 2-2.5 page white paper with the following structure:

1. Title: A concise, professional title derived from the topic (single line)
2. Executive Summary: 1 paragraph summarizing the key findings and significance
3. Introduction: 1 paragraph introducing the topic and context
4. Background & History: 1-2 tight paragraphs on origins and historical context
5. Current State & Key Players: 1-2 paragraphs on the present landscape
6. Technical Foundations: 1-2 paragraphs on core technical concepts and mechanisms
7. Challenges & Controversies: 1-2 paragraphs on open problems and limitations
8. Future Outlook & Implications: 1-2 paragraphs on projected developments
9. Conclusion: 1 paragraph synthesizing the key takeaways

Rules:
- Use formal, professional prose throughout. Do not use bullet lists in the body.
- Aim for approximately 900-1100 words total (excluding the title).
- Begin the response with "Title: <title text>" on its own line.
- Separate each section with a blank line.
- Use the section names above as headers (e.g., "Executive Summary", "Introduction", etc.).
"""


def run_publisher(ctx: WorkflowContext, config: Config) -> WorkflowContext:
    """Generate white paper PDF from research markdown using Claude, matplotlib, and reportlab."""
    print("[Publisher] Generating white paper from research...")
    os.makedirs("output", exist_ok=True)

    # Step 1: Generate white paper text via Claude
    whitepaper_text = _generate_whitepaper_text(ctx, config)
    print(f"[Publisher] White paper text generated ({len(whitepaper_text)} chars).")

    # Step 2: Generate chart
    chart_path = _generate_chart(ctx)

    # Step 3: Render PDF
    pdf_path = _render_pdf(whitepaper_text, chart_path, ctx.topic)

    ctx.published_pdf_path = pdf_path
    print(f"[Publisher] Complete. PDF at: {pdf_path}")
    return ctx


def _generate_whitepaper_text(ctx: WorkflowContext, config: Config) -> str:
    """Call Claude claude-haiku-4-5 to produce a structured white paper from research markdown."""
    client = anthropic.Anthropic(api_key=config.anthropic_api_key)

    user_message = (
        f"Topic: {ctx.topic}\n\n"
        f"Objectives:\n{ctx.objectives}\n\n"
        f"Research:\n{ctx.research_output}"
    )

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=2000,
        system=PUBLISHER_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_message},
        ],
    )

    return message.content[0].text


def _generate_chart(ctx: WorkflowContext) -> str:
    """Generate a bar chart illustrating relative importance of the 5 research areas."""
    categories = [
        "Background",
        "Current State",
        "Technical\nFoundations",
        "Challenges",
        "Future\nOutlook",
    ]
    scores = [7, 9, 8, 6, 8]  # Illustrative relative importance

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(categories, scores, color="#4472C4")
    ax.set_ylabel("Relative Importance")
    ax.set_title(f"Key Research Areas: {ctx.topic}")
    ax.set_ylim(0, 10)
    plt.tight_layout()

    chart_path = "output/chart.png"
    plt.savefig(chart_path, dpi=150)
    plt.close(fig)

    print(f"[Publisher] Chart saved to {chart_path}")
    return chart_path


def _render_pdf(whitepaper_text: str, chart_path: str, topic: str) -> str:
    """Render white paper text and chart into a letter-size PDF using reportlab."""
    pdf_path = "output/whitepaper.pdf"

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=1 * inch,
        rightMargin=1 * inch,
        topMargin=1 * inch,
        bottomMargin=1 * inch,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "WhitepaperTitle",
        parent=styles["Heading1"],
        fontSize=18,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "WhitepaperBody",
        parent=styles["Normal"],
        fontSize=11,
        fontName="Helvetica",
        alignment=TA_JUSTIFY,
        spaceAfter=6,
        leading=16,
    )

    section_header_style = ParagraphStyle(
        "WhitepaperSection",
        parent=styles["Heading2"],
        fontSize=12,
        fontName="Helvetica-Bold",
        spaceBefore=10,
        spaceAfter=4,
    )

    caption_style = ParagraphStyle(
        "WhitepaperCaption",
        parent=styles["Normal"],
        fontSize=9,
        fontName="Helvetica-Oblique",
        alignment=TA_CENTER,
        spaceAfter=6,
    )

    # Parse white paper text into title and body paragraphs
    lines = whitepaper_text.strip().split("\n")
    title_text = topic  # fallback
    body_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.lower().startswith("title:"):
            title_text = stripped[len("title:"):].strip()
        else:
            body_lines.append(stripped)

    # Section headers we recognize (from the system prompt structure)
    section_headers = {
        "executive summary",
        "introduction",
        "background & history",
        "background",
        "current state & key players",
        "current state",
        "technical foundations",
        "challenges & controversies",
        "challenges",
        "future outlook & implications",
        "future outlook",
        "conclusion",
    }

    story = []

    # Title
    story.append(Paragraph(title_text, title_style))
    story.append(Spacer(1, 0.2 * inch))

    # Body paragraphs
    # Group consecutive non-empty lines into paragraphs, detect section headers
    current_paragraph_lines = []

    def flush_paragraph():
        if current_paragraph_lines:
            text = " ".join(current_paragraph_lines)
            # Escape XML special chars for reportlab
            text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(text, body_style))
            story.append(Spacer(1, 0.1 * inch))
            current_paragraph_lines.clear()

    for line in body_lines:
        if not line:
            flush_paragraph()
        elif line.lower().rstrip(":") in section_headers:
            flush_paragraph()
            header_text = line.rstrip(":")
            header_text = header_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(header_text, section_header_style))
        else:
            current_paragraph_lines.append(line)

    flush_paragraph()

    # Chart image
    story.append(Spacer(1, 0.3 * inch))
    story.append(Image(chart_path, width=6 * inch, height=3 * inch))
    story.append(
        Paragraph(
            "Figure 1: Key Research Areas by Relative Importance",
            caption_style,
        )
    )

    doc.build(story)
    print(f"[Publisher] PDF written to {pdf_path}")
    return pdf_path
