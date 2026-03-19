# Roadmap: AgentSwarm

**Created:** 2026-03-18
**Granularity:** Coarse
**Coverage:** 11/11 v1 requirements mapped

---

## Phases

- [x] **Phase 1: Foundation & Orchestration** - CLI entry point and CEO agent task delegation (completed 2026-03-19)
- [x] **Phase 2: Research & Publishing** - Researcher and Publisher agents execute independently (completed 2026-03-19)
- [ ] **Phase 3: Review & Delivery** - CEO review and email delivery of approved documents

---

## Phase Details

### Phase 1: Foundation & Orchestration

**Goal:** Users can trigger a white paper workflow via CLI with the CEO agent interpreting and delegating tasks.

**Depends on:** Nothing (foundation phase)

**Requirements:** ORCH-01, ORCH-02, ORCH-03

**Success Criteria:**
1. User can execute a CLI command with a topic to initiate the workflow
2. CEO agent receives the topic and produces written objectives for the team
3. CEO agent successfully delegates research and publishing tasks with clear context
4. Project Manager agent is tracking progress (can be polled for status)

**Plans:** 2/2 plans complete

Plans:
- [ ] 01-01-PLAN.md — Project scaffold, shared types, CLI entry point (ORCH-01)
- [ ] 01-02-PLAN.md — CEO agent + Project Manager agent, end-to-end wiring (ORCH-02, ORCH-03)

---

### Phase 2: Research & Publishing

**Goal:** Researcher and Publisher agents independently execute their tasks, producing research data and a polished PDF.

**Depends on:** Phase 1 (CEO objectives and delegation context)

**Requirements:** RSRCH-01, RSRCH-02, PUB-01, PUB-02, PUB-03

**Success Criteria:**
1. Researcher agent investigates the topic across 5+ distinct knowledge areas and outputs structured data
2. Publisher agent receives research data and generates a 2-2.5 page white paper
3. Publisher includes an auto-generated chart or diagram relevant to the topic
4. Publisher outputs a professional PDF document ready for review

**Plans:** 3/3 plans complete

Plans:
- [ ] 02-01-PLAN.md — Researcher agent: Claude API research across 5 knowledge areas (RSRCH-01, RSRCH-02)
- [ ] 02-02-PLAN.md — Publisher agent: white paper text + matplotlib chart + reportlab PDF (PUB-01, PUB-02, PUB-03)
- [x] 02-03-PLAN.md — Wire PM stubs to real agents, update CLI, human verify end-to-end (all Phase 2 requirements) (completed 2026-03-19)

---

### Phase 3: Review & Delivery

**Goal:** CEO reviews the final document and approved PDFs are delivered via email.

**Depends on:** Phase 2 (published PDF)

**Requirements:** REV-01, DEL-01, DEL-02

**Success Criteria:**
1. CEO agent can review the final PDF and confirm it meets original objectives
2. Approved PDF is sent via email to the configured recipient
3. Email delivery via Gmail SMTP completes without errors
4. User receives confirmation that the workflow completed successfully

**Plans:** 2/3 plans executed

Plans:
- [ ] 03-01-PLAN.md — CEO reviewer agent: Claude API quality review against objectives (REV-01)
- [ ] 03-02-PLAN.md — Mailer agent: Gmail SMTP with app password, PDF attachment (DEL-01, DEL-02)
- [ ] 03-03-PLAN.md — Wire PM to reviewer/mailer, update CLI, human verify end-to-end (REV-01, DEL-01, DEL-02)

---

## Progress Tracking

| Phase | Goal | Requirements | Plans Complete | Status | Completed |
|-------|------|--------------|-----------------|--------|-----------|
| 1 - Foundation & Orchestration | 2/2 | Complete    | 2026-03-19 | Complete | 2026-03-19 |
| 2 - Research & Publishing | 3/3 | Complete    | 2026-03-19 | Complete | 2026-03-19 |
| 3 - Review & Delivery | 2/3 | In Progress|  | Not started | — |

---

*Last updated: 2026-03-19 after Phase 3 planning*
