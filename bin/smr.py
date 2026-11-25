#!/usr/bin/env python3
"""Smart Model Routing (smr) — zero-dependency CLI installer, doctor & benchmark.

Non-destructive, idempotent installer for multi-agent Context Shielding and
Smart Model Routing rules across Google Antigravity, Claude Code, OpenAI Codex CLI,
and Cursor. Uses only Python 3.10+ standard library.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

START_MARKER = "<!-- SMART-MODEL-ROUTING:START -->"
END_MARKER = "<!-- SMART-MODEL-ROUTING:END -->"

TARGETS = ("antigravity", "claude", "codex", "cursor")

HARNESS_DIRS = {
    "antigravity": ".gemini",
    "claude": ".claude",
    "codex": ".codex",
    "cursor": ".cursor",
}

CLI_BINARIES = ("git", "codex", "claude", "agy", "cursor", "python")


@dataclass(frozen=True)
class OperationResult:
    target: str
    path: Path
    status: str  # created | appended | updated | unchanged | removed | skipped | would-create | would-append | would-update | would-remove
    backup_path: Path | None = None


@dataclass(frozen=True)
class SanitizationFinding:
    path: Path
    line: int
    category: str
    guidance: str


@dataclass(frozen=True)
class BenchmarkTurn:
    turn: int
    label: str
    category: str
    routed_tier: str
    mono_input_added: int
    mono_output: int
    routed_root_added: int
    routed_root_output: int
    subagent_tokens: int


_BLOCK_RE = re.compile(
    re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
    re.DOTALL,
)

_SANITIZATION_RULES: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "rfc1918_ip",
        re.compile(
            r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
            r"|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}"
            r"|192\.168\.\d{1,3}\.\d{1,3})\b"
        ),
        "Replace internal RFC1918 IP addresses with abstract role names or environment variables.",
    ),
    (
        "secret_token",
        re.compile(
            r"\b(?:sk-[A-Za-z0-9_-]{8,}"
            r"|ghp_[A-Za-z0-9]{10,}"
            r"|glpat-[A-Za-z0-9_-]{10,}"
            r"|AIza[0-9A-Za-z_-]{16,}"
            r"|AKIA[0-9A-Z]{16})\b"
        ),
        "Remove hardcoded API keys/tokens from rule files and load secrets from a vault or env var.",
    ),
    (
        "hardcoded_user_path",
        re.compile(
            r"(?:[A-Za-z]:\\Users\\[^\s\\/'\"<>|]+"
            r"|[A-Za-z]:/Users/[^\s/'\"<>|]+"
            r"|/Users/[^\s/'\"<>|]+"
            r"|/home/[^\s/'\"<>|]+)"
        ),
        "Replace machine-specific absolute user paths with relative paths or ~/ for cross-machine portability.",
    ),
)


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except OSError:
                pass


def render_rule_block(lang: str) -> str:
    """Return the marked Smart Model Routing rule block in the requested language."""
    if lang == "pt-br":
        body = """## Smart Model Routing & Blindagem do Contexto Raiz (`smart-model-routing`)

O agente principal atua **estritamente como arquiteto, orquestrador e interlocutor**, protegendo a janela de contexto raiz (`Pro` / `Opus` / `inherit`) contra saturação por I/O verboso.

### 1. Princípio de Blindagem do Contexto Raiz
- **NUNCA** execute no contexto principal tarefas com alto volume de I/O, outputs verbosos de terminal (logs de testes, builds, linters), varreduras amplas no codebase, leitura de múltiplos arquivos extensos ou payloads JSON grandes de MCPs.
- Delegue operações pesadas para subagentes isolados e retorne ao contexto principal **apenas** o diagnóstico sintetizado (causa-raiz, arquivos afetados, próximos passos).

### 2. Matriz de Delegação em 7 Casos Operacionais
| Caso | Tipo de Tarefa | Destino / Tier | Diretriz |
| :--- | :--- | :--- | :--- |
| **1** | Validação estática, linting, testes e builds | Subagente `self` (`flash`) | Isolar logs verbosos; retornar apenas status, erros pontuais e causa-raiz. |
| **2** | Exploração, varredura e pesquisa no codebase | Subagente `research` (`flash`) | Explorar em modo somente-leitura e devolver mapa mental + caminhos relevantes. |
| **3** | Implementação mecânica, boilerplate e edições repetitivas | Subagente `self` (`flash`) | Orquestrador define contrato/interface; subagente escreve e valida. |
| **4** | Triagens rápidas e checagens pontuais (`git status`, arquivo único) | Subagente `self` (`flash_lite`) | Execução ultra-leve sem poluir o histórico principal. |
| **5** | Integrações MCP e APIs externas com JSON volumoso | Subagente `self` (`flash`) | Filtrar payloads externos antes de trazer o resumo ao orquestrador. |
| **6** | Arquitetura, planejamento, specs e decisões de design | Orquestrador Raiz (`pro` / `inherit`) | Conduzir alinhamento, trade-offs e síntese final com o usuário. |
| **7** | Code review cego, auditoria de diffs e validação cruzada | Revisor Externo (`codex review` / `codex exec`) | Auditoria independente antes de commits finais e diversificação de cotas. |"""
    else:
        body = """## Smart Model Routing & Root Context Shielding (`smart-model-routing`)

The root agent acts **strictly as architect, orchestrator, and user interlocutor**, shielding the frontier root context (`Pro` / `Opus` / `inherit`) from saturation caused by verbose I/O.

### 1. Root Context Shielding Principle
- **NEVER** run high-I/O operations directly in the root context: verbose terminal output (test suites, builds, linters), broad codebase greps, multi-file raw dumps, repetitive boilerplate edits, or large external MCP JSON payloads.
- Delegate heavy execution to isolated subagents and return **only** concise synthesized diagnostics (root cause, touched files, action items) to the root conversation.

### 2. Seven Operational Cases Delegation Matrix
| Case | Workload Type | Target / Model Tier | Directive |
| :--- | :--- | :--- | :--- |
| **1** | Static validation, linting, tests & builds | Subagent `self` (`flash`) | Isolate verbose logs; return only status, pinpoint failures & root cause. |
| **2** | Codebase exploration, search & multi-file research | Subagent `research` (`flash`) | Explore in read-only sandbox; return mental map & exact file locations. |
| **3** | Mechanical implementation, boilerplate & repetitive edits | Subagent `self` (`flash`) | Root defines contracts/architecture; worker implements & validates. |
| **4** | Quick triage & single-file / `git status` checks | Subagent `self` (`flash_lite`) | Ultra-fast, low-cost check without polluting root history. |
| **5** | External MCP integrations & heavy JSON/API payloads | Subagent `self` (`flash`) | Filter bulky external payloads in subagent before reporting summary. |
| **6** | Architecture, planning, specs & trade-off decisions | Root Orchestrator (`pro` / `inherit`) | Drive user alignment, system design & final technical synthesis. |
| **7** | Blind code review, diff audit & cross-validation | External Reviewer (`codex review` / `codex exec`) | Independent diff audit before commits & active quota diversification. |"""
    return f"{START_MARKER}\n{body}\n{END_MARKER}"


def render_handoff_template(lang: str) -> str:
    """Return initial docs/CONTEXT_HANDOFF.md content."""
    if lang == "pt-br":
        return """# CONTEXT HANDOFF

Documento vivo de continuidade técnica entre sessões e agentes. Atualize sempre que houver mudança relevante de arquitetura, modelo, dados ou estado de entrega.

## 1. Estado Atual do Projeto
- **Fase atual**: Inicialização
- **Branch ativa**: `main`
- **Resumo**: Descreva aqui o estado operacional corrente.

## 2. Decisões de Arquitetura & Contratos
- Registre decisões irreversíveis ou trade-offs importantes aqui.

## 3. Restrições & Armadilhas Conhecidas
- Liste variáveis de ambiente obrigatórias, limites de API e edge cases.

## 4. Próximos Passos Imediatos
- [ ] Definir próximo marco técnico
"""
    return """# CONTEXT HANDOFF

Living continuity document across sessions and agents. Update whenever architecture, model routing, data pipelines, or delivery state evolves.

## 1. Current Project State
- **Current phase**: Initialization
- **Active branch**: `main`
- **Summary**: Describe current operational state here.

## 2. Architecture Decisions & Contracts
- Record key design choices, contracts, and trade-offs here.

## 3. Known Constraints & Gotchas
- List required environment variables, API limits, and edge cases.

## 4. Immediate Next Steps
- [ ] Define next technical milestone
"""


def render_worktree_agent(lang: str) -> str:
    """Return worktree-agent.md specification."""
    if lang == "pt-br":
        return """---
name: worktree-agent
description: Agente executor isolado em git worktree para implementar funcionalidades paralelas sem conflitar com o workspace principal.
---

# Worktree Agent

Você opera em um `git worktree` dedicado e isolado do workspace principal.

## Regras de Execução
1. Confirme a branch atual (`git branch --show-current`) e o diretório do worktree antes de editar qualquer arquivo.
2. Execute validações (linters, testes unitários, builds) inteiramente dentro deste worktree.
3. Nunca faça merge direto na `main` sem revisão prévia e autorização explícita do orquestrador/usuário.
4. Ao concluir, retorne apenas:
   - Branch e caminho do worktree
   - Lista concisa de arquivos alterados
   - Resultado objetivo dos testes executados
   - Eventuais riscos ou pendências
"""
    return """---
name: worktree-agent
description: Isolated git worktree execution agent for parallel feature implementation without conflicting with the main workspace.
---

# Worktree Agent

You operate inside a dedicated `git worktree` isolated from the primary workspace.

## Execution Rules
1. Verify the active branch (`git branch --show-current`) and worktree root before editing any file.
2. Run all validations (linters, unit tests, builds) strictly inside this worktree.
3. Never merge directly into `main` without prior review and explicit orchestrator/user approval.
4. When finished, return only a concise summary containing:
   - Branch name and worktree path
   - List of modified files
   - Objective pass/fail summary of executed checks
   - Any open risks or follow-ups
"""


def atomic_write(path: Path, content: str) -> None:
    """Atomically write UTF-8 text to *path* using NamedTemporaryFile + os.replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=str(path.parent),
            delete=False,
        ) as handle:
            tmp_path = Path(handle.name)
            handle.write(content)
        os.replace(tmp_path, path)
    except BaseException:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)
        raise


def target_path_for(target: str, scope: str, project_dir: Path, home_dir: Path) -> Path:
    """Resolve destination rule file path for a given harness target and scope."""
    if scope == "project":
        mapping = {
            "antigravity": project_dir / "GEMINI.md",
            "claude": project_dir / "CLAUDE.md",
            "codex": project_dir / "AGENTS.md",
            "cursor": project_dir / ".cursorrules",
        }
    elif scope == "global":
        mapping = {
            "antigravity": home_dir / ".gemini" / "GEMINI.md",
            "claude": home_dir / ".claude" / "CLAUDE.md",
            "codex": home_dir / ".codex" / "AGENTS.md",
            "cursor": home_dir / ".cursor" / "rules" / "smart-model-routing.mdc",
        }
    else:
        raise ValueError(f"Unsupported scope: {scope}")
    if target not in mapping:
        raise ValueError(f"Unsupported target: {target}")
    return mapping[target]


def detect_installed_targets(home_dir: Path) -> list[str]:
    """Detect installed AI coding harnesses in *home_dir* or PATH."""
    detected: list[str] = []
    bin_map = {
        "antigravity": "agy",
        "claude": "claude",
        "codex": "codex",
        "cursor": "cursor",
    }
    for target in TARGETS:
        dir_exists = (home_dir / HARNESS_DIRS[target]).exists()
        if target == "codex":
            dir_exists = dir_exists or (home_dir / ".agents").exists()
        bin_exists = shutil.which(bin_map[target]) is not None
        if dir_exists or bin_exists:
            detected.append(target)
    return detected


def resolve_targets(
    requested_target: str | None,
    scope: str,
    home_dir: Path,
    *,
    for_uninstall: bool = False,
) -> list[str]:
    """Resolve concrete list of targets based on flags, scope, and installed harnesses."""
    if requested_target == "all":
        return list(TARGETS)
    if requested_target is not None:
        return [requested_target]
    if scope == "project":
        return list(TARGETS)
    if for_uninstall:
        return list(TARGETS)
    detected = detect_installed_targets(home_dir)
    return detected if detected else list(TARGETS)


def upsert_marked_block(existing: str | None, block: str) -> tuple[str, str]:
    """Insert or idempotently replace the marked block inside *existing* text."""
    if existing is None:
        return f"{block}\n", "created"

    has_start = START_MARKER in existing
    has_end = END_MARKER in existing
    if has_start != has_end:
        raise ValueError(
            "Malformed SMART-MODEL-ROUTING marker: found only one of START/END markers."
        )

    match = _BLOCK_RE.search(existing)
    if match:
        if match.group(0) == block:
            return existing, "unchanged"
        updated = existing[: match.start()] + block + existing[match.end() :]
        return updated, "updated"

    if not existing.strip():
        return f"{block}\n", "appended"

    stripped = existing.rstrip("\r\n")
    return f"{stripped}\n\n{block}\n", "appended"


def remove_marked_block(existing: str) -> tuple[str, bool]:
    """Remove only the marked block while preserving surrounding user content."""
    has_start = START_MARKER in existing
    has_end = END_MARKER in existing
    if has_start != has_end:
        raise ValueError(
            "Malformed SMART-MODEL-ROUTING marker: found only one of START/END markers."
        )

    match = _BLOCK_RE.search(existing)
    if not match:
        return existing, False

    before = existing[: match.start()]
    after = existing[match.end() :]

    if before and after:
        cleaned_before = before.rstrip("\r\n")
        cleaned_after = after.lstrip("\r\n")
        if cleaned_before and cleaned_after:
            new_text = f"{cleaned_before}\n\n{cleaned_after}"
        elif cleaned_before:
            new_text = f"{cleaned_before}\n"
        else:
            new_text = cleaned_after
    elif before:
        cleaned_before = before.rstrip("\r\n")
        new_text = f"{cleaned_before}\n" if cleaned_before else ""
    elif after:
        new_text = after.lstrip("\r\n")
    else:
        new_text = ""

    return new_text, True


def install_rule_file(
    target: str,
    path: Path,
    block: str,
    *,
    dry_run: bool = False,
) -> OperationResult:
    """Safely install or update the Smart Model Routing block at *path*."""
    existing: str | None = None
    if path.exists():
        existing = path.read_text(encoding="utf-8")

    new_content, action = upsert_marked_block(existing, block)
    if action == "unchanged":
        return OperationResult(target=target, path=path, status="unchanged")

    if dry_run:
        return OperationResult(target=target, path=path, status=f"would-{action}")

    backup_path: Path | None = None
    if existing is not None:
        backup_path = path.with_name(f"{path.name}.bak")
        atomic_write(backup_path, existing)

    atomic_write(path, new_content)
    return OperationResult(
        target=target,
        path=path,
        status=action,
        backup_path=backup_path,
    )


def uninstall_rule_file(
    target: str,
    path: Path,
    *,
    dry_run: bool = False,
) -> OperationResult:
    """Surgically remove the Smart Model Routing block from *path*."""
    if not path.exists():
        return OperationResult(target=target, path=path, status="skipped")

    existing = path.read_text(encoding="utf-8")
    new_content, changed = remove_marked_block(existing)
    if not changed:
        return OperationResult(target=target, path=path, status="skipped")

    if dry_run:
        return OperationResult(target=target, path=path, status="would-remove")

    backup_path = path.with_name(f"{path.name}.bak")
    atomic_write(backup_path, existing)
    atomic_write(path, new_content)
    return OperationResult(
        target=target,
        path=path,
        status="removed",
        backup_path=backup_path,
    )


def install_extras(
    *,
    scope: str,
    lang: str,
    project_dir: Path,
    home_dir: Path,
    with_handoff: bool,
    with_worktree_agent: bool,
    dry_run: bool,
) -> list[OperationResult]:
    """Install optional extras: docs/CONTEXT_HANDOFF.md and worktree-agent.md."""
    results: list[OperationResult] = []

    if with_handoff:
        handoff_path = project_dir / "docs" / "CONTEXT_HANDOFF.md"
        if handoff_path.exists():
            results.append(OperationResult("handoff", handoff_path, "skipped"))
        elif dry_run:
            results.append(OperationResult("handoff", handoff_path, "would-create"))
        else:
            atomic_write(handoff_path, render_handoff_template(lang))
            results.append(OperationResult("handoff", handoff_path, "created"))

    if with_worktree_agent:
        base_dir = home_dir if scope == "global" else project_dir
        agent_content = render_worktree_agent(lang)
        for folder in (".gemini", ".claude", ".agents"):
            agent_path = base_dir / folder / "agents" / "worktree-agent.md"
            if dry_run:
                status = "would-update" if agent_path.exists() else "would-create"
                results.append(OperationResult(f"worktree-agent ({folder})", agent_path, status))
            else:
                existed = agent_path.exists()
                atomic_write(agent_path, agent_content)
                results.append(
                    OperationResult(
                        f"worktree-agent ({folder})",
                        agent_path,
                        "updated" if existed else "created",
                    )
                )

    return results


def scan_file_for_leaks(path: Path) -> list[SanitizationFinding]:
    """Scan a rule file for private IPs, tokens, or hardcoded user paths without exposing values."""
    if not path.exists() or not path.is_file():
        return []
    findings: list[SanitizationFinding] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []

    for idx, line in enumerate(lines, start=1):
        for category, pattern, guidance in _SANITIZATION_RULES:
            if pattern.search(line):
                findings.append(
                    SanitizationFinding(
                        path=path,
                        line=idx,
                        category=category,
                        guidance=guidance,
                    )
                )
    return findings


def _is_smr_active(path: Path) -> bool:
    if not path.exists() or not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return START_MARKER in text or "smart-model-routing" in text.lower()


def run_doctor(project_dir: Path, home_dir: Path, strict: bool = False) -> int:
    """Inspect harnesses, binaries, rule activation, and sanitization hygiene."""
    print("Smart Model Routing — Doctor Report")
    print("=" * 64)

    print("\n1. Harness Directories (home):")
    for folder in (".gemini", ".claude", ".codex", ".agents", ".cursor"):
        candidate = home_dir / folder
        tag = "[OK]" if candidate.exists() else "[MISSING]"
        print(f"  {tag:9s} ~/{folder} ({candidate})")

    print("\n2. CLI Binaries in PATH:")
    for binary in CLI_BINARIES:
        resolved = shutil.which(binary)
        tag = "[OK]" if resolved else "[MISSING]"
        detail = resolved if resolved else "not found"
        print(f"  {tag:9s} {binary:8s} -> {detail}")

    rule_paths: list[tuple[str, Path]] = [
        ("global:antigravity", target_path_for("antigravity", "global", project_dir, home_dir)),
        ("global:claude", target_path_for("claude", "global", project_dir, home_dir)),
        ("global:codex", target_path_for("codex", "global", project_dir, home_dir)),
        ("global:cursor", target_path_for("cursor", "global", project_dir, home_dir)),
        ("project:antigravity", target_path_for("antigravity", "project", project_dir, home_dir)),
        ("project:claude", target_path_for("claude", "project", project_dir, home_dir)),
        ("project:codex", target_path_for("codex", "project", project_dir, home_dir)),
        ("project:cursor", target_path_for("cursor", "project", project_dir, home_dir)),
    ]

    print("\n3. Rule Activation Status:")
    active_count = 0
    for label, rpath in rule_paths:
        if not rpath.exists():
            print(f"  [ABSENT]  {label:20s} -> {rpath}")
        elif _is_smr_active(rpath):
            active_count += 1
            print(f"  [ACTIVE]  {label:20s} -> {rpath}")
        else:
            print(f"  [INACTIVE]{label:20s} -> {rpath} (file exists without SMR block)")

    print("\n4. Sanitization & Portability Scan (values redacted):")
    all_findings: list[SanitizationFinding] = []
    seen_paths: set[Path] = set()
    scan_candidates: Iterable[Path] = [p for _, p in rule_paths] + [
        home_dir / ".agents" / "AGENTS.md",
    ]
    for candidate in scan_candidates:
        resolved = candidate.resolve() if candidate.exists() else candidate
        if resolved in seen_paths:
            continue
        seen_paths.add(resolved)
        all_findings.extend(scan_file_for_leaks(candidate))

    if not all_findings:
        print("  [OK]      No private IPs, secret tokens, or hardcoded user paths detected.")
    else:
        for finding in all_findings:
            print(
                f"  [WARN]    {finding.path.name}:{finding.line} "
                f"[{finding.category}] (value redacted) — {finding.guidance}"
            )

    print("\nSummary:")
    print(f"  Active SMR targets : {active_count}")
    print(f"  Sanitization warns : {len(all_findings)}")
    if strict and all_findings:
        return 1
    return 0


def build_benchmark_scenario() -> list[BenchmarkTurn]:
    """Return a realistic 15-turn software engineering session workload.

    Composition:
    - 2 planning/architecture turns (Root)
    - 3 broad codebase exploration turns (grep + multi-file dumps)
    - 4 verbose test/build execution turns (stack traces, build output)
    - 2 external MCP JSON payload turns (Figma/tracker schemas)
    - 3 mechanical boilerplate edit turns (DTOs, mappers, repetitive tests)
    - 1 blind diff code review + final synthesis turn
    """
    return [
        BenchmarkTurn(1, "Kickoff & architecture alignment", "Planning", "root (Pro/Opus)", 3_200, 1_400, 3_200, 1_400, 0),
        BenchmarkTurn(2, "Broad codebase grep & symbol map #1", "Search (1/3)", "research (Flash)", 9_200, 900, 420, 680, 10_100),
        BenchmarkTurn(3, "Broad codebase multi-file read #2", "Search (2/3)", "research (Flash)", 10_800, 950, 420, 720, 11_750),
        BenchmarkTurn(4, "Cross-module dependency trace #3", "Search (3/3)", "research (Flash)", 8_900, 850, 420, 680, 9_750),
        BenchmarkTurn(5, "Contract & spec design", "Planning", "root (Pro/Opus)", 2_800, 1_800, 2_800, 1_800, 0),
        BenchmarkTurn(6, "Baseline test suite run #1", "Test/Build (1/4)", "self (Flash)", 12_400, 700, 380, 560, 13_100),
        BenchmarkTurn(7, "External MCP payload fetch #1 (board/Figma)", "MCP JSON (1/2)", "self (Flash)", 11_600, 650, 360, 580, 12_250),
        BenchmarkTurn(8, "External MCP payload fetch #2 (issue tree)", "MCP JSON (2/2)", "self (Flash)", 10_400, 600, 360, 540, 11_000),
        BenchmarkTurn(9, "Boilerplate DTO & schema generation #1", "Boilerplate (1/3)", "self (Flash)", 6_200, 1_500, 450, 620, 7_700),
        BenchmarkTurn(10, "Linter & type-check run #2", "Test/Build (2/4)", "self (Flash)", 9_400, 600, 380, 520, 10_000),
        BenchmarkTurn(11, "Boilerplate mapper & adapter edits #2", "Boilerplate (2/3)", "self (Flash)", 5_900, 1_450, 450, 600, 7_350),
        BenchmarkTurn(12, "Boilerplate unit test scaffolding #3", "Boilerplate (3/3)", "self (Flash)", 6_400, 1_600, 450, 640, 8_000),
        BenchmarkTurn(13, "Full integration test run #3 (failure)", "Test/Build (3/4)", "self (Flash)", 14_800, 800, 380, 620, 15_600),
        BenchmarkTurn(14, "Post-fix build & test verification #4", "Test/Build (4/4)", "self (Flash)", 11_200, 550, 380, 480, 11_750),
        BenchmarkTurn(15, "Blind diff audit & final synthesis", "Code Review (1/1)", "codex review", 8_400, 1_300, 650, 1_100, 9_700),
    ]


def compute_benchmark_metrics(
    turns: list[BenchmarkTurn],
    base_system_tokens: int = 7_500,
) -> dict[str, object]:
    """Compute quadratic cumulative root input tokens for Monolithic vs Routed."""
    mono_history = base_system_tokens
    routed_history = base_system_tokens

    mono_cumulative = 0
    routed_cumulative = 0
    total_subagent_tokens = 0
    rows: list[dict[str, object]] = []

    for item in turns:
        mono_turn_ctx = mono_history + item.mono_input_added
        mono_cumulative += mono_turn_ctx
        mono_history = mono_turn_ctx + item.mono_output

        routed_turn_ctx = routed_history + item.routed_root_added
        routed_cumulative += routed_turn_ctx
        routed_history = routed_turn_ctx + item.routed_root_output

        total_subagent_tokens += item.subagent_tokens
        rows.append(
            {
                "turn": item.turn,
                "category": item.category,
                "tier": item.routed_tier,
                "mono_ctx": mono_turn_ctx,
                "routed_ctx": routed_turn_ctx,
                "mono_cum": mono_cumulative,
                "routed_cum": routed_cumulative,
                "subagent": item.subagent_tokens,
            }
        )

    savings_pct = (
        ((mono_cumulative - routed_cumulative) / mono_cumulative) * 100.0
        if mono_cumulative
        else 0.0
    )
    peak_reduction_pct = (
        ((mono_history - routed_history) / mono_history) * 100.0 if mono_history else 0.0
    )

    # Illustrative blended frontier vs worker API pricing ($ per 1M input tokens)
    frontier_cost_usd = (mono_cumulative / 1_000_000) * 3.00
    routed_cost_usd = ((routed_cumulative / 1_000_000) * 3.00) + (
        (total_subagent_tokens / 1_000_000) * 0.15
    )

    return {
        "rows": rows,
        "mono_cumulative": mono_cumulative,
        "routed_cumulative": routed_cumulative,
        "mono_peak": mono_history,
        "routed_peak": routed_history,
        "subagent_total": total_subagent_tokens,
        "savings_pct": savings_pct,
        "peak_reduction_pct": peak_reduction_pct,
        "frontier_cost_usd": frontier_cost_usd,
        "routed_cost_usd": routed_cost_usd,
    }


def run_benchmark(fmt: str = "ascii") -> int:
    """Print the 15-turn Context Shielding benchmark comparison."""
    turns = build_benchmark_scenario()
    metrics = compute_benchmark_metrics(turns)
    rows = metrics["rows"]

    print("Smart Model Routing — 15-Turn Root Context Shielding Benchmark")
    print("Scenario: 2 planning, 3 broad searches, 4 test/build logs, 2 MCP JSONs, 3 boilerplate edits, 1 diff review\n")

    if fmt == "markdown":
        print("| Turn | Workload | Routed Tier | Mono Turn Ctx | Routed Turn Ctx | Mono Cumulative | Routed Cumulative |")
        print("| ---: | :--- | :--- | ---: | ---: | ---: | ---: |")
        for r in rows:
            print(
                f"| {r['turn']} | {r['category']} | {r['tier']} | "
                f"{r['mono_ctx']:,} | {r['routed_ctx']:,} | "
                f"{r['mono_cum']:,} | {r['routed_cum']:,} |"
            )
    else:
        header = (
            f"{'Turn':>4} | {'Workload':<18} | {'Routed Tier':<16} | "
            f"{'Mono Ctx':>10} | {'Routed Ctx':>10} | "
            f"{'Mono Cumul.':>12} | {'Routed Cumul.':>13}"
        )
        sep = "-" * len(header)
        print(header)
        print(sep)
        for r in rows:
            print(
                f"{r['turn']:>4} | {str(r['category']):<18} | {str(r['tier']):<16} | "
                f"{r['mono_ctx']:>10,} | {r['routed_ctx']:>10,} | "
                f"{r['mono_cum']:>12,} | {r['routed_cum']:>13,}"
            )
        print(sep)

    print("\nKey Metrics:")
    print(f"  Monolithic Cumulative Root Input Tokens : {metrics['mono_cumulative']:,}")
    print(f"  Routed Cumulative Root Input Tokens     : {metrics['routed_cumulative']:,}")
    print(f"  Root Frontier Token Savings             : {metrics['savings_pct']:.1f}%")
    print(
        f"  Final Peak Root Context (Turn 15)       : "
        f"{metrics['mono_peak']:,} -> {metrics['routed_peak']:,} "
        f"(-{metrics['peak_reduction_pct']:.1f}%)"
    )
    print(f"  Offloaded Subagent Tokens (Flash/Codex) : {metrics['subagent_total']:,}")
    print(
        f"  Illustrative Input Cost (@$3/1M vs $0.15/1M): "
        f"${metrics['frontier_cost_usd']:.2f} -> ${metrics['routed_cost_usd']:.2f}"
    )
    return 0


def _print_results(results: list[OperationResult], dry_run: bool) -> None:
    prefix = "[DRY-RUN] " if dry_run else ""
    for res in results:
        bak = f" (backup: {res.backup_path.name})" if res.backup_path else ""
        print(f"{prefix}[{res.status.upper()}] {res.target}: {res.path}{bak}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="smr",
        description="Smart Model Routing — non-destructive multi-harness installer, doctor & context benchmark.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # install
    p_install = sub.add_parser("install", help="Install or update Smart Model Routing rules.")
    p_install.add_argument(
        "--target",
        choices=[*TARGETS, "all"],
        default=None,
        help="Target harness (default: all for project scope, auto-detected for global scope).",
    )
    p_install.add_argument(
        "--scope",
        choices=["global", "project"],
        default="project",
        help="Install globally under home dir or locally in project dir (default: project).",
    )
    p_install.add_argument(
        "--lang",
        choices=["en", "pt-br"],
        default="en",
        help="Rule template language (default: en).",
    )
    p_install.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Target project directory for --scope project (default: current directory).",
    )
    p_install.add_argument(
        "--home-dir",
        type=Path,
        default=Path.home(),
        help="Override user home directory (useful for safe isolated testing).",
    )
    p_install.add_argument(
        "--with-handoff",
        action="store_true",
        help="Create docs/CONTEXT_HANDOFF.md in the project if it does not exist.",
    )
    p_install.add_argument(
        "--with-worktree-agent",
        action="store_true",
        help="Install worktree-agent.md into .gemini/agents/, .claude/agents/ and .agents/agents/.",
    )
    p_install.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing any files.",
    )

    # uninstall
    p_uninstall = sub.add_parser("uninstall", help="Surgically remove Smart Model Routing blocks.")
    p_uninstall.add_argument(
        "--target",
        choices=[*TARGETS, "all"],
        default=None,
        help="Target harness (default: all).",
    )
    p_uninstall.add_argument(
        "--scope",
        choices=["global", "project"],
        default="project",
        help="Uninstall from global home dir or local project dir (default: project).",
    )
    p_uninstall.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Target project directory for --scope project.",
    )
    p_uninstall.add_argument(
        "--home-dir",
        type=Path,
        default=Path.home(),
        help="Override user home directory.",
    )
    p_uninstall.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview removals without modifying any files.",
    )

    # doctor
    p_doctor = sub.add_parser("doctor", help="Diagnose harnesses, active rules, and sanitization leaks.")
    p_doctor.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Project directory to inspect (default: current directory).",
    )
    p_doctor.add_argument(
        "--home-dir",
        type=Path,
        default=Path.home(),
        help="Override user home directory.",
    )
    p_doctor.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if sanitization warnings are detected.",
    )

    # benchmark
    p_bench = sub.add_parser("benchmark", help="Simulate 15-turn Root Context Shielding token savings.")
    p_bench.add_argument(
        "--format",
        choices=["ascii", "markdown"],
        default="ascii",
        help="Output table format (default: ascii).",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "install":
        project_dir = args.project_dir.resolve()
        home_dir = args.home_dir.resolve()
        targets = resolve_targets(args.target, args.scope, home_dir)
        block = render_rule_block(args.lang)
        results: list[OperationResult] = []
        for target in targets:
            dest = target_path_for(target, args.scope, project_dir, home_dir)
            results.append(install_rule_file(target, dest, block, dry_run=args.dry_run))

        results.extend(
            install_extras(
                scope=args.scope,
                lang=args.lang,
                project_dir=project_dir,
                home_dir=home_dir,
                with_handoff=args.with_handoff,
                with_worktree_agent=args.with_worktree_agent,
                dry_run=args.dry_run,
            )
        )
        _print_results(results, args.dry_run)
        return 0

    if args.command == "uninstall":
        project_dir = args.project_dir.resolve()
        home_dir = args.home_dir.resolve()
        targets = resolve_targets(args.target, args.scope, home_dir, for_uninstall=True)
        results = []
        for target in targets:
            dest = target_path_for(target, args.scope, project_dir, home_dir)
            results.append(uninstall_rule_file(target, dest, dry_run=args.dry_run))
        _print_results(results, args.dry_run)
        return 0

    if args.command == "doctor":
        return run_doctor(args.project_dir.resolve(), args.home_dir.resolve(), strict=args.strict)

    if args.command == "benchmark":
        return run_benchmark(fmt=args.format)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
