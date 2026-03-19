# Requirements: AgentSwarm

**Defined:** 2026-03-18
**Core Value:** A single command takes a topic and autonomously produces a professional white paper delivered via email — demonstrating multi-agent orchestration with clear role separation.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Orchestration

- [x] **ORCH-01**: User can run a single CLI command with a topic to start the workflow
- [x] **ORCH-02**: CEO agent interprets the topic, defines objectives, and delegates to the team
- [x] **ORCH-03**: Project Manager agent tracks Researcher and Publisher progress to completion

### Research

- [x] **RSRCH-01**: Researcher agent investigates the topic across 5+ distinct knowledge areas via Claude API
- [x] **RSRCH-02**: Researcher produces structured output formatted for Publisher consumption

### Publishing

- [x] **PUB-01**: Publisher agent generates a professional 2-2.5 page white paper from research
- [x] **PUB-02**: Publisher includes an auto-generated chart or diagram relevant to the topic
- [x] **PUB-03**: Publisher outputs the white paper as a PDF document

### Review

- [x] **REV-01**: CEO agent reviews the final document for clarity and objective alignment

### Delivery

- [x] **DEL-01**: Mailer agent emails the approved PDF as an attachment
- [x] **DEL-02**: Email sent via Gmail SMTP with app password

## v2 Requirements

### Orchestration

- **ORCH-04**: CEO agent revision loop — sends document back for rework if standards not met
- **ORCH-05**: Configurable recipient email address via config file

### Research

- **RSRCH-03**: Web search integration for real-time research (Brave/Google API)

### Publishing

- **PUB-04**: AI-generated cover image for white paper
- **PUB-05**: Multiple output formats (PDF, DOCX)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Web UI | CLI-only PoC — simplicity over polish |
| Web scraping / search APIs | Agents use Claude knowledge only for v1 |
| Multiple LLM providers | Claude API only — single provider keeps PoC simple |
| Multi-user support | Single user proof of concept |
| Persistent memory across runs | Each run is independent |
| Real-time streaming output | Batch processing sufficient for PoC |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| ORCH-01 | Phase 1 | Complete |
| ORCH-02 | Phase 1 | Complete |
| ORCH-03 | Phase 1 | Complete |
| RSRCH-01 | Phase 2 | Complete |
| RSRCH-02 | Phase 2 | Complete |
| PUB-01 | Phase 2 | Complete |
| PUB-02 | Phase 2 | Complete |
| PUB-03 | Phase 2 | Complete |
| REV-01 | Phase 3 | Complete |
| DEL-01 | Phase 3 | Complete |
| DEL-02 | Phase 3 | Complete |

**Coverage:**
- v1 requirements: 11 total
- Mapped to phases: 11
- Unmapped: 0

---

*Requirements defined: 2026-03-18*
*Last updated: 2026-03-18 after roadmap creation*
