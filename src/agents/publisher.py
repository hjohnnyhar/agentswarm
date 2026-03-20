import os
import re
import anthropic
import urllib.parse
import urllib.request

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

from src.types import WorkflowContext
from src.config import Config

PUBLISHER_SYSTEM_PROMPT = """You are a professional technical writer producing executive white papers.

Given research notes and objectives, write a polished white paper with the following structure:

1. Title: A concise, professional title derived from the topic (single line)
2. Executive Summary: 1 paragraph summarizing the key findings and significance
3. Introduction: 1 paragraph introducing the topic and context
4. Background & History: 1 tight paragraph on origins and historical context
5. Current State & Key Players: 1 paragraph on the present landscape
6. Technical Foundations: 1 paragraph on core technical concepts and mechanisms
7. Challenges & Controversies: 1 paragraph on open problems and limitations
8. Future Outlook & Implications: 1 paragraph on projected developments
9. Conclusion: 1 paragraph synthesizing the key takeaways

Rules:
- Use formal, professional prose throughout. Do not use bullet lists in the body.
- HARD LIMIT: Maximum 800 words total (excluding the title). Aim for 600-800 words.
- Begin the response with "Title: <title text>" on its own line.
- Separate each section with a blank line.
- Use the section names above as headers (e.g., "Executive Summary", "Introduction", etc.).
"""


def run_publisher(ctx: WorkflowContext, config: Config) -> WorkflowContext:
    """Generate white paper PDF from research markdown using Claude, stock photo, and reportlab."""
    print("[Publisher] Generating white paper from research...")
    os.makedirs("output", exist_ok=True)

    # Step 1: Generate white paper text via Claude (with word count enforcement)
    whitepaper_text = _generate_whitepaper_text(ctx, config)
    word_count = len(whitepaper_text.split())
    max_attempts = 3
    attempt = 1
    while word_count > 800 and attempt < max_attempts:
        attempt += 1
        print(f"[Publisher] Text is {word_count} words (max 800). Reworking (attempt {attempt}/{max_attempts})...")
        whitepaper_text = _rework_text(whitepaper_text, config)
        word_count = len(whitepaper_text.split())
    print(f"[Publisher] White paper text generated ({word_count} words, {len(whitepaper_text)} chars).")

    # Step 2: Fetch stock photo
    image_path = _fetch_stock_photo(ctx.topic)

    # Step 3: Derive filename from title and render PDF
    title = _extract_title(whitepaper_text, ctx.topic)
    pdf_filename = _slugify(title) + ".pdf"
    pdf_path = os.path.join("output", pdf_filename)
    _render_pdf(whitepaper_text, image_path, ctx.topic, pdf_path)

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


def _rework_text(text: str, config: Config) -> str:
    """Ask Claude to condense the white paper to under 800 words."""
    client = anthropic.Anthropic(api_key=config.anthropic_api_key)
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1500,
        system="You are an editor. Condense the following white paper to a maximum of 800 words. Keep the same structure, title line, and section headers. Preserve the most important content.",
        messages=[{"role": "user", "content": text}],
    )
    return message.content[0].text


def _extract_title(whitepaper_text: str, fallback: str) -> str:
    """Extract the title from the white paper text."""
    for line in whitepaper_text.strip().split("\n"):
        stripped = line.strip()
        if stripped.lower().startswith("title:"):
            return stripped[len("title:"):].strip()
    return fallback


def _slugify(text: str) -> str:
    """Convert text to a filesystem-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text[:80].strip('-')


def _fetch_stock_photo(topic: str) -> str:
    """Fetch a relevant stock photo from Unsplash (free, no API key needed)."""
    image_path = "output/cover.jpg"
    query = urllib.parse.quote(topic[:50])
    url = f"https://source.unsplash.com/800x400/?{query}"
    try:
        urllib.request.urlretrieve(url, image_path)
        print(f"[Publisher] Cover image saved to {image_path}")
    except Exception as e:
        print(f"[Publisher] Could not fetch stock photo ({e}), continuing without image.")
        return ""
    return image_path


def _render_pdf(whitepaper_text: str, image_path: str, topic: str, pdf_path: str) -> str:
    """Render white paper text and optional image into a letter-size PDF using reportlab."""

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

    # Cover image (stock photo)
    if image_path and os.path.exists(image_path):
        story.append(Spacer(1, 0.3 * inch))
        story.append(Image(image_path, width=6 * inch, height=3 * inch))
        story.append(
            Paragraph(
                f"Image: {topic}",
                caption_style,
            )
        )

    doc.build(story)
    print(f"[Publisher] PDF written to {pdf_path}")
    return pdf_path
