# Project Context Handoff

> Living continuity document read at the start of every AI engineering session and updated whenever technical state evolves.

- **Project**: `<project-name>`
- **Last Updated**: `YYYY-MM-DD`
- **Active Branch / Milestone**: `<branch-or-release>`

---

## 1. Architecture Decisions

Record key technical choices, trade-offs, and invariants so future sessions do not re-litigate settled design decisions.

- **[ADR-001]** `<Decision title>` — `<Context, chosen approach, and rationale>`
- **[ADR-002]** `<Decision title>` — `<Context, chosen approach, and rationale>`

---

## 2. Current State

High-level snapshot of what is working, deployed, or in progress.

- **Core Runtime / Stack**: `<e.g., Python 3.12 + FastAPI / React 19 / PostgreSQL 16>`
- **Build & Test Health**: `<e.g., Unit tests passing (142/142); E2E suite pending DB seed update>`
- **Recent Milestones**:
  - `<Completed feature or refactor>`

---

## 3. Active Models & Services

Track running services, background workers, data pipelines, or ML models and their current versions/endpoints.

| Component | Version / Tag | Status | Notes |
| :--- | :--- | :--- | :--- |
| `<api-service>` | `v1.x.y` | `Healthy` | `<Port, config, or dependency note>` |
| `<worker-queue>` | `v1.x.y` | `Active` | `<Concurrency or schedule note>` |

---

## 4. Pending Tasks

Ordered backlog for the next session(s).

- [ ] `<High-priority next task with exact file/module pointer>`
- [ ] `<Follow-up task>`
- [ ] `<Validation or documentation item>`

---

## 5. Known Blockers & Risks

Document environment quirks, upstream issues, or failing edge cases that require attention.

- **Blocker / Risk**: `<Description>` — **Mitigation / Owner**: `<Next step>`

---

## 6. Last Session Log

- **Date**: `YYYY-MM-DD`
- **Summary of Changes**:
  - `<What was implemented, fixed, or validated>`
- **Verification Executed**:
  - `<Exact test/lint command and observed result>`
- **Immediate Next Step**:
  - `<Single clearest starting point for the next session>`
