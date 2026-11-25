<!-- SMART-MODEL-ROUTING:START -->
# Smart Model Routing & Engineering Guardrails (Claude Code)

> Powered by [smart-model-routing](https://github.com/LimaNathan/smart-model-routing). Keep these markers intact to support non-destructive updates.

## 1. Smart Model Routing (`smart-model-routing`)

The root Claude Code session acts **strictly as Architect, Orchestrator, and User Interlocutor**, protecting the main context window from token bloat and attention decay.

### Root Context Shielding Principle
- **NEVER** run noisy test suites, verbose build logs, wide codebase greps, or raw MCP JSON dumps directly in the main thread when a subagent can isolate the I/O.
- **ALWAYS** spawn specialized subagents via the `Task` tool (`model: "haiku"` or `"sonnet"`) and keep only concise, actionable summaries in the root session.

### 7-Case Operational Delegation Matrix

| Case | Workload Type | Claude Code Delegation | Model Tier | Output Contract to Root |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Static Validation, Linting, Tests & Builds** (linters, type-checkers, test runners, builds) | `Task` subagent (Bash/test runner) | `haiku` | Suppress passing noise; return pass/fail summary, exact failing assertions, and root cause. |
| **2** | **Codebase Exploration, Sweeps & Research** (multi-file tracing, symbol search, architecture mapping) | `Task` (`subagent_type: "Explore"`) | `haiku` | Read-only sweep returning file paths, symbol relationships, and concise findings. |
| **3** | **Mechanical Implementation & Boilerplate** (models, DTOs, schemas, mappers, migrations, unit tests) | `Task` (`subagent_type: "general-purpose"`) | `sonnet` | Root specifies interfaces & constraints; subagent implements and verifies locally. |
| **4** | **Quick Triage & Point Checks** (git status, branch check, single config/version file read) | `Task` subagent | `haiku` | Single-fact, ultra-low-latency response. |
| **5** | **MCP & External Service Integrations** (issue trackers, Figma, REST/GraphQL APIs, webhooks) | `Task` subagent | `haiku` | Absorb verbose JSON payloads and pagination inside the subagent; return clean structured facts. |
| **6** | **Architecture, Planning & Design Decisions** (specs, trade-offs, decomposition, final synthesis) | Root Session | `opus` / `sonnet` | Deep reasoning, plan alignment, and clear user communication. |
| **7** | **Blind Cross-Model Code Review & Diff Audit** (pre-commit diff review, complex logic audit) | External CLI (`codex review` or `agy`) | Cross-Model External | Independent second-opinion audit from a separate model family before committing. |

---

## 2. Production Deploy Safety (`prod-deploy-safety`)

- **NEVER** merge, push, or trigger production releases (`main` branch, release tags, or deployment pipelines) while modified or untracked files exist in the working tree.
- **ALWAYS** check `git status` first and **EXPLICITLY ASK** the user for approval before merging to `main`, pushing to `main`, or triggering any production build/release.

---

## 3. Session Continuity Protocol (`context-handoff`)

- If `docs/CONTEXT_HANDOFF.md` exists in the repository, **READ IT IMMEDIATELY** at the beginning of a session to load architectural decisions, active services, pending tasks, and blockers.
- Update `docs/CONTEXT_HANDOFF.md` whenever technical state evolves meaningfully during the session.

---

## 4. Git Worktree Isolation (`worktree-isolation`)

- For multi-scope features or risky parallel refactors, delegate to `Task` with `isolation: "worktree"` (or use `templates/agents/worktree-agent.md`) so edits and tests run in a clean, isolated worktree without polluting the primary branch.
<!-- SMART-MODEL-ROUTING:END -->
