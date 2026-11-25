<!-- SMART-MODEL-ROUTING:START -->
# Smart Model Routing & Engineering Guardrails (Google Antigravity)

> Powered by [smart-model-routing](https://github.com/LimaNathan/smart-model-routing). Keep these markers intact to support non-destructive updates.

## 1. Smart Model Routing (`smart-model-routing`)

The root agent acts **strictly as Architect, Orchestrator, and User Interlocutor**, shielding the root context window from token saturation and attention degradation.

### Root Context Shielding Principle
- **NEVER** execute high-I/O tasks, verbose terminal commands, broad codebase sweeps, or extensive boilerplate edits directly in the root conversation.
- **ALWAYS** delegate heavy execution to subagents via `invoke_subagent` (or cross-model CLI audits), returning only synthesized diagnostics, file paths, and high-level decisions to the root context.

### 7-Case Operational Delegation Matrix

| Case | Workload Type | Target Harness / Subagent | Model Tier | Output Contract to Root |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Static Validation, Linting, Tests & Builds** (linters, type-checkers, test runners, compilers) | `invoke_subagent` (`TypeName: "self"`) | `flash` | Isolate verbose logs; return pass/fail status, pinpoint failures, and root cause only. |
| **2** | **Codebase Exploration, Sweeps & Research** (wide grep/find, multi-file architecture tracing) | `invoke_subagent` (`TypeName: "research"`) | `flash` | Run in read-only sandbox; return mental map, relevant file paths, and synthesized findings. |
| **3** | **Mechanical Implementation & Boilerplate** (models, DTOs, schemas, mappers, migrations, unit tests) | `invoke_subagent` (`TypeName: "self"`) | `flash` | Root defines contracts & architecture; subagent writes/edits files and runs local checks. |
| **4** | **Quick Triage & Point Checks** (git status/branch checks, single config/version file reads, env checks) | `invoke_subagent` (`TypeName: "self"`) | `flash_lite` | Minimal-cost single-fact response. |
| **5** | **MCP & External Service Integrations** (issue trackers, design tools, REST/GraphQL APIs, webhooks) | `invoke_subagent` (`TypeName: "self"`) | `flash` | Prevent massive JSON payloads and tool schemas from polluting the root window. |
| **6** | **Architecture, Planning & Design Decisions** (specs, trade-off analysis, strategy, user alignment) | Root Orchestrator | `pro` / `inherit` | High-reasoning synthesis, plan approval, and final user communication. |
| **7** | **Blind Cross-Model Code Review & Diff Audit** (pre-commit audit, complex algorithm second opinion) | OpenAI Codex CLI (`codex review` / `codex exec`) | External Cross-Model | Unbiased diff review from a different model provider before finalizing commits. |

---

## 2. Production Deploy Safety (`prod-deploy-safety`)

- **NEVER** push, merge, or trigger production releases (e.g., `main` branch, CI/CD release tags, or app store pipelines) while there are modified or untracked (uncommitted) files in the working tree.
- **ALWAYS** inspect `git status` beforehand and **EXPLICITLY ASK** the user for confirmation before executing any merge into `main`, push to `main`, or production build/release trigger.

---

## 3. Session Continuity Protocol (`context-handoff`)

- If `docs/CONTEXT_HANDOFF.md` exists in the workspace, **READ IT IMMEDIATELY** at the start of every new conversation to restore architectural decisions, active services/models, pending tasks, and known blockers.
- Whenever a session introduces meaningful technical progress (architecture changes, new endpoints, schema migrations, model updates, or resolved blockers), **UPDATE** `docs/CONTEXT_HANDOFF.md` before wrapping up.

---

## 4. Git Worktree Isolation (`worktree-isolation`)

- For multi-scope features, high-risk refactors, or parallel implementation tracks, isolate execution in a dedicated Git worktree (`git worktree add`) or delegate to `worktree-agent` (`templates/agents/worktree-agent.md`).
- Keep the primary working tree clean while experimental or parallel work is validated and tested.
<!-- SMART-MODEL-ROUTING:END -->
