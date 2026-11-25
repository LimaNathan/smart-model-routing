"""Unit tests for the Smart Model Routing CLI (bin/smr.py)."""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from bin import smr  # noqa: E402


def _run_cli(*args: str) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = smr.main(list(args))
    return code, buf.getvalue()


class SmartModelRoutingCliTests(unittest.TestCase):
    def test_clean_install_project_and_global_scopes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            project_dir = tmp_path / "repo"
            home_dir = tmp_path / "home"
            project_dir.mkdir()
            home_dir.mkdir()

            code, _ = _run_cli(
                "install",
                "--scope",
                "project",
                "--project-dir",
                str(project_dir),
                "--home-dir",
                str(home_dir),
            )
            self.assertEqual(code, 0)
            for rel in ("GEMINI.md", "CLAUDE.md", "AGENTS.md", ".cursorrules"):
                target_file = project_dir / rel
                self.assertTrue(target_file.exists(), f"Missing {rel}")
                content = target_file.read_text(encoding="utf-8")
                self.assertIn(smr.START_MARKER, content)
                self.assertIn(smr.END_MARKER, content)

            # Global install with mocked home_dir
            code_g, _ = _run_cli(
                "install",
                "--scope",
                "global",
                "--home-dir",
                str(home_dir),
                "--project-dir",
                str(project_dir),
            )
            self.assertEqual(code_g, 0)
            for rel in (
                ".gemini/GEMINI.md",
                ".claude/CLAUDE.md",
                ".codex/AGENTS.md",
                ".cursor/rules/smart-model-routing.mdc",
            ):
                target_file = home_dir / rel
                self.assertTrue(target_file.exists(), f"Missing global {rel}")
                self.assertIn(smr.START_MARKER, target_file.read_text(encoding="utf-8"))

    def test_non_destructive_append_preserves_existing_memories_and_creates_backup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp) / "repo"
            home_dir = Path(tmp) / "home"
            project_dir.mkdir()
            home_dir.mkdir()

            original_memories = "# My Personal Rules\n\n- Always use pytest.\n- Keep commits atomic.\n"
            gemini_file = project_dir / "GEMINI.md"
            gemini_file.write_text(original_memories, encoding="utf-8")

            code, _ = _run_cli(
                "install",
                "--scope",
                "project",
                "--target",
                "antigravity",
                "--project-dir",
                str(project_dir),
                "--home-dir",
                str(home_dir),
            )
            self.assertEqual(code, 0)

            updated = gemini_file.read_text(encoding="utf-8")
            self.assertTrue(updated.startswith("# My Personal Rules\n\n- Always use pytest.\n- Keep commits atomic."))
            self.assertIn(smr.START_MARKER, updated)
            self.assertIn(smr.END_MARKER, updated)

            backup_file = project_dir / "GEMINI.md.bak"
            self.assertTrue(backup_file.exists())
            self.assertEqual(backup_file.read_text(encoding="utf-8"), original_memories)

    def test_idempotent_reinstall_updates_in_place_without_duplication(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp) / "repo"
            home_dir = Path(tmp) / "home"
            project_dir.mkdir()
            home_dir.mkdir()

            gemini_file = project_dir / "GEMINI.md"
            gemini_file.write_text("# Header Memory\n\nFooter note.\n", encoding="utf-8")

            # First install (EN)
            _run_cli(
                "install",
                "--target",
                "antigravity",
                "--lang",
                "en",
                "--project-dir",
                str(project_dir),
                "--home-dir",
                str(home_dir),
            )
            # Second install (EN again -> unchanged)
            code2, out2 = _run_cli(
                "install",
                "--target",
                "antigravity",
                "--lang",
                "en",
                "--project-dir",
                str(project_dir),
                "--home-dir",
                str(home_dir),
            )
            self.assertEqual(code2, 0)
            self.assertIn("UNCHANGED", out2)

            # Third install switching to PT-BR -> updates block cleanly in-place
            code3, out3 = _run_cli(
                "install",
                "--target",
                "antigravity",
                "--lang",
                "pt-br",
                "--project-dir",
                str(project_dir),
                "--home-dir",
                str(home_dir),
            )
            self.assertEqual(code3, 0)
            self.assertIn("UPDATED", out3)

            content = gemini_file.read_text(encoding="utf-8")
            self.assertEqual(content.count(smr.START_MARKER), 1)
            self.assertEqual(content.count(smr.END_MARKER), 1)
            self.assertIn("# Header Memory", content)
            self.assertIn("Footer note.", content)
            self.assertIn("Blindagem do Contexto Raiz", content)

    def test_surgical_uninstall_removes_only_smr_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp) / "repo"
            home_dir = Path(tmp) / "home"
            project_dir.mkdir()
            home_dir.mkdir()

            claude_file = project_dir / "CLAUDE.md"
            claude_file.write_text(
                "# Top Rule\n\nKeep code clean.\n\n"
                f"{smr.render_rule_block('en')}\n\n"
                "# Bottom Rule\n\nNever force push.\n",
                encoding="utf-8",
            )

            code, out = _run_cli(
                "uninstall",
                "--target",
                "claude",
                "--scope",
                "project",
                "--project-dir",
                str(project_dir),
                "--home-dir",
                str(home_dir),
            )
            self.assertEqual(code, 0)
            self.assertIn("REMOVED", out)

            remaining = claude_file.read_text(encoding="utf-8")
            self.assertNotIn(smr.START_MARKER, remaining)
            self.assertNotIn(smr.END_MARKER, remaining)
            self.assertIn("# Top Rule", remaining)
            self.assertIn("Keep code clean.", remaining)
            self.assertIn("# Bottom Rule", remaining)
            self.assertIn("Never force push.", remaining)

    def test_languages_with_handoff_and_worktree_agent_and_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp) / "repo"
            home_dir = Path(tmp) / "home"
            project_dir.mkdir()
            home_dir.mkdir()

            # Dry run creates nothing
            code_dry, out_dry = _run_cli(
                "install",
                "--lang",
                "pt-br",
                "--with-handoff",
                "--with-worktree-agent",
                "--dry-run",
                "--project-dir",
                str(project_dir),
                "--home-dir",
                str(home_dir),
            )
            self.assertEqual(code_dry, 0)
            self.assertIn("DRY-RUN", out_dry)
            self.assertFalse((project_dir / "GEMINI.md").exists())
            self.assertFalse((project_dir / "docs" / "CONTEXT_HANDOFF.md").exists())

            # Real run with pt-br + handoff + worktree-agent
            code, _ = _run_cli(
                "install",
                "--lang",
                "pt-br",
                "--with-handoff",
                "--with-worktree-agent",
                "--project-dir",
                str(project_dir),
                "--home-dir",
                str(home_dir),
            )
            self.assertEqual(code, 0)

            handoff = project_dir / "docs" / "CONTEXT_HANDOFF.md"
            self.assertTrue(handoff.exists())
            self.assertIn("Estado Atual do Projeto", handoff.read_text(encoding="utf-8"))

            for folder in (".gemini", ".claude", ".agents"):
                wt_agent = project_dir / folder / "agents" / "worktree-agent.md"
                self.assertTrue(wt_agent.exists(), f"Missing {wt_agent}")
                self.assertIn("git worktree", wt_agent.read_text(encoding="utf-8"))

            # Pre-existing handoff must not be overwritten
            handoff.write_text("# Custom Handoff\n", encoding="utf-8")
            _run_cli(
                "install",
                "--lang",
                "en",
                "--with-handoff",
                "--project-dir",
                str(project_dir),
                "--home-dir",
                str(home_dir),
            )
            self.assertEqual(handoff.read_text(encoding="utf-8"), "# Custom Handoff\n")

    def test_doctor_detects_active_rules_and_redacts_sanitization_leaks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp) / "repo"
            home_dir = Path(tmp) / "home"
            project_dir.mkdir()
            (home_dir / ".gemini").mkdir(parents=True)

            _run_cli(
                "install",
                "--target",
                "antigravity",
                "--project-dir",
                str(project_dir),
                "--home-dir",
                str(home_dir),
            )

            secret_ip = "192.168.42.99"
            secret_path = r"C:\Users\alice\secret-repo"
            gemini_file = project_dir / "GEMINI.md"
            gemini_file.write_text(
                gemini_file.read_text(encoding="utf-8")
                + f"\nDeploy to {secret_ip} from {secret_path}\n",
                encoding="utf-8",
            )

            code, out = _run_cli(
                "doctor",
                "--project-dir",
                str(project_dir),
                "--home-dir",
                str(home_dir),
            )
            self.assertEqual(code, 0)
            self.assertIn("[ACTIVE]", out)
            self.assertIn("rfc1918_ip", out)
            self.assertIn("hardcoded_user_path", out)
            self.assertIn("value redacted", out)
            # Never expose the raw leaked values
            self.assertNotIn(secret_ip, out)
            self.assertNotIn("alice", out)

            strict_code, _ = _run_cli(
                "doctor",
                "--project-dir",
                str(project_dir),
                "--home-dir",
                str(home_dir),
                "--strict",
            )
            self.assertEqual(strict_code, 1)

    def test_benchmark_reports_72_to_78_percent_savings(self) -> None:
        turns = smr.build_benchmark_scenario()
        metrics = smr.compute_benchmark_metrics(turns)
        savings = float(metrics["savings_pct"])
        self.assertGreaterEqual(savings, 72.0)
        self.assertLessEqual(savings, 78.0)

        code_ascii, out_ascii = _run_cli("benchmark")
        self.assertEqual(code_ascii, 0)
        self.assertIn("Root Frontier Token Savings", out_ascii)
        self.assertIn("Monolithic Cumulative Root Input Tokens", out_ascii)

        code_md, out_md = _run_cli("benchmark", "--format", "markdown")
        self.assertEqual(code_md, 0)
        self.assertIn("| Turn | Workload |", out_md)


if __name__ == "__main__":
    unittest.main()
