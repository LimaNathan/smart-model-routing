# Global Launch Post (EN) — LinkedIn / X / Reddit / Hacker News

---

## LinkedIn / Social Version (EN)

Your frontier coding model didn't suddenly get dumber halfway through the session.
You just drowned its root context window in 120k tokens of raw test logs and grep dumps.

In multi-turn agentic coding, every turn re-sends the entire conversation history. Drop one 15k-token stack trace or raw MCP JSON payload into your root chat, and you re-pay for—and re-attend to—that noise on every single turn afterward.

Token burn scales quadratically, and architectural reasoning quietly degrades ("context rot").

To fix this across my daily workflow, I packaged the delegation protocol I rely on into a zero-dependency Python CLI: **Smart Model Routing (`smr`)**.

The core rule is strict **Root Context Shielding**:

1. **Root Orchestrator (`Pro` / `Opus`)**: strictly handles architecture, trade-offs, specs, and final synthesis.
2. **Isolated Workers (`Flash` / `Flash-Lite`)**: absorb verbose test/build logs, broad codebase greps, heavy MCP JSON payloads, and repetitive boilerplate—returning only concise root-cause summaries.
3. **Blind External Reviewer (`Codex CLI`)**: runs an independent diff audit before final commits while diversifying model quotas.

In a simulated 15-turn engineering session (`smr benchmark`), cumulative root frontier input tokens drop from **1,219,500 to 318,010** (**73.9% reduction**), cutting peak turn-15 context by **80.3%**.

What's in the box (pure Python 3.10+ stdlib, zero pip dependencies):
- `smr install`: non-destructive, idempotent marker injection with automatic `.bak` backups across `GEMINI.md`, `CLAUDE.md`, `AGENTS.md`, and `.cursorrules`
- `smr uninstall`: surgical block removal preserving all personal rules
- `smr doctor`: verifies active harnesses and scans rule files for leaked private IPs, tokens, or hardcoded user paths
- `smr benchmark`: reproducible 15-turn context-shielding simulator

Link to the repo in the comments.

How are you routing heavy tool output vs. architectural reasoning in your multi-agent setups?

#SoftwareEngineering #AIAgents #ContextEngineering

---

## Reddit / Hacker News Discussion Version (`r/ClaudeAI`, `r/ChatGPTCoding`, `r/LocalLLaMA`)

**Title:** `Show HN / Tool: Smart Model Routing (smr) — Zero-dependency CLI for Root Context Shielding across Claude Code, Antigravity, Codex CLI & Cursor (73.9% fewer frontier tokens)`

**Body:**
When running long coding sessions in Claude Code, Antigravity, Codex CLI, or Cursor, the biggest silent killer of both quota and reasoning quality is letting verbose I/O (pytest logs, build output, multi-file greps, raw MCP JSON responses) accumulate in the root conversation. Because history is re-sent every turn, every raw log inflates input tokens quadratically.

I built **Smart Model Routing (`smr`)**, a pure Python 3.10+ stdlib CLI that installs a non-destructive 7-case delegation matrix into `GEMINI.md`, `CLAUDE.md`, `AGENTS.md`, and `.cursorrules`:

- **Shield the Root (`Pro`/`Opus`)**: architecture, specs, alignment, synthesis only.
- **Delegate heavy I/O (`Flash` / `Flash-Lite`)**: test runs, codebase exploration, boilerplate, MCP JSON parsing -> return only concise diagnostics.
- **Cross-validate (`Codex CLI`)**: blind diff audit before final commits.

Key features:
- **Safe & idempotent**: wraps rules in `<!-- SMART-MODEL-ROUTING:START/END -->`, backs up existing files to `.bak`, and uses atomic writes (`NamedTemporaryFile` + `os.replace`).
- **`smr doctor`**: checks detected harnesses and scans rule files for accidental RFC1918 IPs, secret prefixes, or hardcoded user paths without echoing the values.
- **`smr benchmark`**: models a 15-turn session showing **1,219,500 -> 318,010** cumulative root tokens (**73.9% savings**).

Repo: `https://github.com/LimaNathan/smart-model-routing`
Would love feedback on the 7-case matrix and how other folks handle context hygiene across harnesses.
