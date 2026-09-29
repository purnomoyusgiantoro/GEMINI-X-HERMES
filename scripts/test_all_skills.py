#!/usr/bin/env python3
"""
Comprehensive Test Suite for GEMINI X HERMES Skills.
Tests all 5 active skills and underlying cognitive modules.
"""
import sys
import os
import io
import json
import unittest
from pathlib import Path

# Configure Windows UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

HERMES_ROOT = Path("D:/Documents/GEMINI-X-HERMES")
sys.path.insert(0, str(HERMES_ROOT))


class TestSwitchAgy(unittest.TestCase):
    """Test Suite for switch-agy skill."""

    def test_script_exists_and_loads(self):
        script_path = HERMES_ROOT / "skills" / "switch-agy" / "scripts" / "switch-agy-core.py"
        self.assertTrue(script_path.exists(), "switch-agy-core.py must exist")

    def test_credential_read(self):
        sys.path.insert(0, str(HERMES_ROOT / "skills" / "switch-agy" / "scripts"))
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("switch_agy_core", HERMES_ROOT / "skills" / "switch-agy" / "scripts" / "switch-agy-core.py")
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            
            cred, user = mod.read_win_cred()
            self.assertIsNotNone(user)
            email = mod.extract_email(cred)
            self.assertTrue(email is None or "@" in email, "Extracted email must be valid format if present")
        except Exception as e:
            self.fail(f"switch-agy failed execution: {e}")


class TestHermesMemory(unittest.TestCase):
    """Test Suite for hermes-memory skill."""

    def setUp(self):
        sys.path.insert(0, str(HERMES_ROOT / "skills" / "hermes-memory" / "scripts"))
        import importlib.util
        spec = importlib.util.spec_from_file_location("memory_manager", HERMES_ROOT / "skills" / "hermes-memory" / "scripts" / "memory_manager.py")
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)

    def test_load_projects(self):
        data = self.mod.load_projects()
        self.assertIn("projects", data)
        self.assertIn("GEMINI-X-HERMES", data["projects"])

    def test_get_project(self):
        name, proj = self.mod.get_project("GEMINI-X-HERMES")
        self.assertEqual(name, "GEMINI-X-HERMES")
        self.assertTrue(os.path.exists(proj["path"]))

    def test_load_decisions(self):
        decisions = self.mod.load_decisions()
        self.assertIn("decisions", decisions)
        self.assertGreater(len(decisions["decisions"]), 0)


class TestHermesModelRouter(unittest.TestCase):
    """Test Suite for hermes-model-router skill."""

    def setUp(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("router", HERMES_ROOT / "skills" / "hermes-model-router" / "scripts" / "router.py")
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        self.router = self.mod.ModelRouter()

    def test_tier_s_classification(self):
        res = self.router.classify_task("Tolong brainstorm arsitektur sistem baru dan threat model")
        self.assertEqual(res["tier"], "Tier S")
        self.assertEqual(res["subagent_model"], "pro")

    def test_tier_a_classification(self):
        res = self.router.classify_task("Implementasikan fungsi controller untuk menghitung pajak penghasilan")
        self.assertEqual(res["tier"], "Tier A")
        self.assertEqual(res["subagent_model"], "flash")

    def test_tier_b_classification(self):
        res = self.router.classify_task("Fix typo di file README.md dan formatting spasi")
        self.assertEqual(res["tier"], "Tier B")
        self.assertEqual(res["subagent_model"], "flash_lite")

    def test_subagent_mapping(self):
        self.assertEqual(self.router.get_subagent_model("security-auditor"), "pro")
        self.assertEqual(self.router.get_subagent_model("code-reviewer"), "pro")
        self.assertEqual(self.router.get_subagent_model("research"), "flash")
        self.assertEqual(self.router.get_subagent_model("test-engineer"), "flash")
        self.assertEqual(self.router.get_subagent_model("formatter"), "flash_lite")

    def test_downgrade_cascade(self):
        fallback = self.router.get_downgrade("claude-opus-4-6-thinking")
        self.assertEqual(fallback, "gemini-3.8-flash-high")


class TestHermesGitSentinel(unittest.TestCase):
    """Test Suite for hermes-git-sentinel skill."""

    def setUp(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("sentinel", HERMES_ROOT / "skills" / "hermes-git-sentinel" / "scripts" / "sentinel.py")
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        self.sentinel = self.mod.GitSentinel(repo_path=HERMES_ROOT)

    def test_secret_detection(self):
        fake_key = "".join(["AIzaSy", "FakeKeyWithThirtyThreeCharacters_"])
        fake_diff = f"+ api_key = '{fake_key}'\n"
        issues = self.sentinel.scan_secrets(fake_diff)
        self.assertGreater(len(issues), 0)
        self.assertEqual(issues[0]["type"], "SECRET")

    def test_database_danger_detection(self):
        drop_cmd = "".join(["DROP ", "TABLE ", "users"])
        fake_diff = f"+ DB::statement('{drop_cmd}');\n"
        issues = self.sentinel.scan_anti_patterns(fake_diff, ["test.php"])
        db_issues = [i for i in issues if i["type"] == "DATABASE_SAFETY"]
        self.assertGreater(len(db_issues), 0)

    def test_ui_logic_separation_detection(self):
        query_snippet = "".join(["User", "::all()"])
        fake_diff = f"+ <div> {{{{ {query_snippet} }}}} </div>\n"
        issues = self.sentinel.scan_anti_patterns(fake_diff, ["index.blade.php"])
        ui_issues = [i for i in issues if i["type"] == "UI_LOGIC_SEPARATION"]
        self.assertGreater(len(ui_issues), 0)


class TestHermesCognitionCore(unittest.TestCase):
    """Test Suite for hermes-cognition and core cognitive submodules."""

    def test_error_memory_bank_and_matcher(self):
        import importlib.util
        bank_spec = importlib.util.spec_from_file_location("bank", HERMES_ROOT / "memory-bank" / "bank.py")
        bank_mod = importlib.util.module_from_spec(bank_spec)
        bank_spec.loader.exec_module(bank_mod)
        
        matcher_spec = importlib.util.spec_from_file_location("matcher", HERMES_ROOT / "memory-bank" / "matcher.py")
        matcher_mod = importlib.util.module_from_spec(matcher_spec)
        matcher_spec.loader.exec_module(matcher_mod)

        bank = bank_mod.ErrorMemoryBank(HERMES_ROOT / "memory-bank" / "errors.json")
        matcher = matcher_mod.ErrorMatcher(bank)
        self.assertIsNotNone(bank)
        self.assertIsNotNone(matcher)

    def test_self_grader(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("grader", HERMES_ROOT / "self-grade" / "grader.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        grader = mod.SelfGrader(HERMES_ROOT / "self-grade" / "grades.json")
        res = grader.grade_task("unit_test_task", "Unit Test Evaluation", {
            "tests_passed": True, "exit_code": 0, "lint_clean": True,
            "naming_consistent": True, "single_responsibility": True,
            "no_hardcoded_secrets": True, "input_validated": True,
            "no_n_plus_one": True, "no_unnecessary_rerenders": True
        })
        self.assertEqual(res["score"], 100.0)
        self.assertEqual(res["grade"], "A+")

    def test_telemetry(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("collector", HERMES_ROOT / "telemetry" / "collector.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        collector = mod.TelemetryCollector(HERMES_ROOT / "telemetry" / "metrics.json")
        self.assertIn("total_tasks_completed", collector.metrics)


def run_full_suite():
    loader = unittest.defaultTestLoader
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(TestSwitchAgy))
    suite.addTest(loader.loadTestsFromTestCase(TestHermesMemory))
    suite.addTest(loader.loadTestsFromTestCase(TestHermesModelRouter))
    suite.addTest(loader.loadTestsFromTestCase(TestHermesGitSentinel))
    suite.addTest(loader.loadTestsFromTestCase(TestHermesCognitionCore))

    runner = unittest.TextTestRunner(verbosity=2)
    print("=" * 68)
    print("  🚀 EXECUTING COMPREHENSIVE SKILL SUITE (GEMINI X HERMES)")
    print("=" * 68)
    res = runner.run(suite)
    print("=" * 68)
    if res.wasSuccessful():
        print("  🎉 ALL 5 SKILLS & COGNITIVE MODULES PASSED VERIFICATION!")
    else:
        print(f"  ❌ FAILED: {len(res.failures)} failures, {len(res.errors)} errors")
    print("=" * 68)
    return res.wasSuccessful()


if __name__ == "__main__":
    success = run_full_suite()
    sys.exit(0 if success else 1)
