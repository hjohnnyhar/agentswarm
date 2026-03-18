# AgentSwarm

## What This Is

A proof-of-concept multi-agent system where specialized AI agents collaborate in a corporate hierarchy to produce professional white papers. A human provides a topic to a CEO agent, which delegates research, writing, project management, and delivery across a team of agents — culminating in a polished PDF emailed to a fixed recipient.

## Core Value

A single command takes a topic and autonomously produces a professional white paper delivered via email — demonstrating multi-agent orchestration with clear role separation.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Human provides a topic via CLI to the CEO agent
- [ ] CEO agent interprets the topic, sets objectives, and delegates to the team
- [ ] Researcher agent investigates the topic across a minimum of 5 distinct knowledge areas using Claude API
- [ ] Publisher agent takes research output and produces a professional 2-2.5 page white paper as PDF
- [ ] Publisher includes an auto-generated chart or diagram relevant to the topic
- [ ] Project Manager agent tracks progress of Researcher and Publisher, ensures completion
- [ ] CEO agent reviews the final document for clarity and objective alignment
- [ ] CEO agent can send the document back for revisions if it doesn't meet objectives
- [ ] Mailer agent emails the approved PDF as an attachment to a configured recipient
- [ ] All agents are powered by Claude API calls
- [ ] Email delivery via Gmail SMTP (app password)
- [ ] The entire workflow runs from a single CLI command

### Out of Scope

- Web UI — CLI-only for this PoC
- Web scraping or search APIs — agents use Claude's knowledge only
- Multiple LLM providers — Claude API only
- AI-generated images — charts/diagrams via Python libraries only
- Multi-user support — single user PoC
- Persistent memory across runs — each run is independent
- Real-time streaming output — batch processing is fine

## Context

- This is a greenfield proof of concept to demonstrate multi-agent orchestration
- The agent hierarchy mirrors a corporate structure: CEO → PM → (Researcher, Publisher) → Mailer
- Python is the implementation language, using the TastyTrade conda environment
- Claude API (Anthropic SDK) powers each agent's reasoning
- PDF generation via Python libraries (e.g., reportlab)
- Charts/diagrams via matplotlib or similar
- Email via Gmail SMTP with app password (hjohnnyharai@gmail.com)
- No agent framework required — pure Python orchestration keeps the PoC simple and transparent

## Constraints

- **Tech stack**: Python + Claude API + reportlab/matplotlib + Gmail SMTP
- **Environment**: TastyTrade conda environment (`C:\Users\hjohn\anaconda3\envs\TastyTrade\python.exe`)
- **API**: Requires Anthropic API key configured
- **Email**: Requires Gmail app password for SMTP sending
- **Scope**: Proof of concept — favor simplicity over production-readiness

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Pure Python over agent framework | PoC should be transparent and minimal — frameworks add complexity | — Pending |
| Claude API for all agents | User has Anthropic access, consistent API surface | — Pending |
| AI knowledge over web search | Simpler implementation, no search API keys needed | — Pending |
| PDF output format | Professional appearance for white paper delivery | — Pending |
| Gmail SMTP for email | User already has Gmail account, no additional services needed | — Pending |

---
*Last updated: 2026-03-18 after initialization*
