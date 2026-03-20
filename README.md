# AgentSwarm

A multi-agent orchestration system that autonomously produces a professional white paper and delivers it via email — all from a single CLI command.

## What It Does

Given a topic, AgentSwarm runs a pipeline of specialized AI agents:

1. **CEO Agent** — Interprets the topic, defines research objectives, and delegates tasks to the team
2. **Project Manager Agent** — Tracks and coordinates all agent tasks to completion
3. **Researcher Agent** — Investigates the topic across 5 distinct knowledge areas via the Claude API
4. **Publisher Agent** — Generates a polished white paper (max 800 words) with a stock photo and renders it as a PDF
5. **CEO Reviewer Agent** — Reviews the final document against the original objectives (approves or rejects)
6. **Mailer Agent** — Sends the PDF as an email attachment via Gmail SMTP

## Setup

### Prerequisites

- Python 3.10+ (TastyTrade conda environment)
- An [Anthropic API key](https://console.anthropic.com/)
- A [Gmail App Password](https://myaccount.google.com/apppasswords) (requires 2-Step Verification enabled)

### Install Dependencies

```bash
C:\Users\hjohn\anaconda3\envs\TastyTrade\python.exe -m pip install -r requirements.txt
```

### Configure Environment

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=your-anthropic-api-key
GMAIL_APP_PASSWORD=your-16-char-gmail-app-password
```

## Usage

```bash
C:\Users\hjohn\anaconda3\envs\TastyTrade\python.exe main.py --topic "Your Topic Here"
```

### Example

```bash
C:\Users\hjohn\anaconda3\envs\TastyTrade\python.exe main.py --topic "Iran conflict impact to US markets"
```

This will:
- Research the topic across 5 knowledge areas
- Generate a white paper PDF (saved to `output/iran-conflict-impact-to-us-markets.pdf`)
- Review the paper against the stated objectives
- Email the PDF to the configured recipient (hjohnnyharai@gmail.com)

## Project Structure

```
AgentSwarm/
  main.py                 # CLI entry point
  src/
    cli.py                # Argument parsing and workflow orchestration
    config.py             # Environment/config loading
    types.py              # Shared data types (WorkflowContext, AgentTask)
    agents/
      ceo.py              # CEO agent (objectives + review)
      researcher.py       # Researcher agent (Claude API research)
      publisher.py        # Publisher agent (white paper + PDF)
      mailer.py           # Mailer agent (Gmail SMTP delivery)
      project_manager.py  # PM agent (task coordination)
  output/                 # Generated PDFs and images
  tests/                  # Unit tests
```

## Configuration

| Environment Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude access |
| `GMAIL_APP_PASSWORD` | Gmail App Password for email delivery |

The sender and recipient email are configured in `src/config.py` (defaults to hjohnnyharai@gmail.com).
