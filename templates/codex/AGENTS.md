<!-- SMART-MODEL-ROUTING:START -->
# Smart Model Routing & Engineering Guardrails (Codex CLI / AGENTS.md)

> Powered by [smart-model-routing](https://github.com/LimaNathan/smart-model-routing). Keep these markers intact to support non-destructive updates.

## 1. Smart Model Routing (`smart-model-routing`)

Operate with strict **Root Context Shielding**: keep the primary reasoning thread focused on architecture, specifications, and final synthesis, while offloading noisy execution, broad searches, and mechanical edits to lightweight worker invocations or scoped commands.

### Root Context Shielding Principle
- **AVOID** dumping raw test logs, full build transcripts, or multi-kilobyte API/JSON payloads into the main reasoning context. Pipe/filter outputs (`--tail`, `--quiet`, `--tb=short`) or isolate them in worker sub-invocations.
- **ALWAYS** separate planning/architecture from mechanical code generation and verification.

### 7-Case Operational Delegation Matrix

| Case | Workload Type | Codex / AGENTS.md Strategy | Recommended Model / Mode | Output Contract |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Static Validation, Linting, Tests & Builds** | Scoped worker / quiet runner (`-q`, `--tb=short`) | Lightweight fast model (`mini` / `nano`) | Report pass/fail counts, failing test names, and root cause only. |
| **2** | **Codebase Exploration, Sweeps & Research** | Read-only worker / targeted `rg` sweeps | Lightweight fast model (`mini`) | Return file paths, symbol definitions, and architectural summary. |
| **3** | **Mechanical Implementation & Boilerplate** | Scoped implementation worker (`codex exec`) | Balanced coding model | Implement against root-defined contracts and validate locally. |
| **4** | **Quick Triage & Point Checks** | Direct minimal check (`git status -sb`, single-file read) | Ultra-light model (`nano` / `mini`) | Single-fact response without extra file reads. |
| **5** | **MCP & External Service Integrations** | Isolated integration script or worker | Lightweight fast model (`mini`) | Filter payloads before returning structured summaries to root. |
| **6** | **Architecture, Planning & Design Decisions** | Primary Orchestrator thread | Flagship reasoning model | Trade-off analysis, specification design, and user alignment. |
| **7** | **Blind Cross-Model Code Review & Diff Audit** | Cross-provider audit (`agy` / Claude / `codex review`) | Cross-Model External | Independent diff review from another provider family before commit. |

---

## 2. Production Deploy Safety (`prod-deploy-safety`)

- **NEVER** merge into `main`, push to `main`, or trigger production release pipelines while uncommitted or untracked changes remain in the repository.
- **ALWAYS** run `git status` first and **EXPLICITLY ASK** the user for confirmation before any production merge, push, or release execution.

---

## 3. Session Continuity Protocol (`context-handoff`)

- If `docs/CONTEXT_HANDOFF.md` exists, **READ IT IMMEDIATELY** upon starting a new session to restore architectural context, active services/models, pending tasks, and blockers.
- Update `docs/CONTEXT_HANDOFF.md` whenever meaningful architectural or operational changes are completed.

---

## 4. Git Worktree Isolation (`worktree-isolation`)

- Isolate multi-scope features, parallel branches, or high-risk refactors in a dedicated Git worktree (`git worktree add`) before editing, validating tests there prior to merging back.
<!-- SMART-MODEL-ROUTING:END -->
