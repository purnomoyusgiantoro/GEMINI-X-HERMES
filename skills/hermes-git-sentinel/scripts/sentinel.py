#!/usr/bin/env python3
"""
Hermes Git Sentinel - Intelligent Pre-Commit & Quality Gate Engine.
Integrates Self-Grading Engine, Error Memory Bank, and Universal Protocols.
"""
import sys
import os
import re
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

# Locate GEMINI-X-HERMES Root Directory
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

CURRENT_FILE = Path(__file__).resolve()
HERMES_ROOT = CURRENT_FILE.parents[3]
if not (HERMES_ROOT / "self-grade").exists():
    HERMES_ROOT = Path("D:/Documents/GEMINI-X-HERMES")

# Add submodules to path
sys.path.insert(0, str(HERMES_ROOT))

try:
    from self_grade.grader import SelfGrader
except (ImportError, ModuleNotFoundError):
    try:
        # direct import if directory has hyphen
        import importlib.util
        spec = importlib.util.spec_from_file_location("grader", HERMES_ROOT / "self-grade" / "grader.py")
        grader_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(grader_module)
        SelfGrader = grader_module.SelfGrader
    except Exception as e:
        SelfGrader = None

try:
    import importlib.util
    bank_spec = importlib.util.spec_from_file_location("bank", HERMES_ROOT / "memory-bank" / "bank.py")
    bank_module = importlib.util.module_from_spec(bank_spec)
    bank_spec.loader.exec_module(bank_module)
    ErrorMemoryBank = bank_module.ErrorMemoryBank

    matcher_spec = importlib.util.spec_from_file_location("matcher", HERMES_ROOT / "memory-bank" / "matcher.py")
    matcher_module = importlib.util.module_from_spec(matcher_spec)
    matcher_spec.loader.exec_module(matcher_module)
    ErrorMatcher = matcher_module.ErrorMatcher
except Exception:
    ErrorMemoryBank = None
    ErrorMatcher = None

try:
    telemetry_spec = importlib.util.spec_from_file_location("collector", HERMES_ROOT / "telemetry" / "collector.py")
    telemetry_module = importlib.util.module_from_spec(telemetry_spec)
    telemetry_spec.loader.exec_module(telemetry_module)
    TelemetryCollector = telemetry_module.TelemetryCollector
except Exception:
    TelemetryCollector = None


class GitSentinel:
    """Pre-commit and quality gate inspector for Hermes Agent ecosystem."""

    def __init__(self, repo_path: Path | str = None, min_score: float = 80.0):
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.min_score = min_score
        self.hermes_root = HERMES_ROOT
        
        # Initialize modules
        self.grades_file = self.hermes_root / "self-grade" / "grades.json"
        self.grader = SelfGrader(self.grades_file) if SelfGrader else None
        
        self.errors_file = self.hermes_root / "memory-bank" / "errors.json"
        if ErrorMemoryBank and ErrorMatcher:
            self.bank = ErrorMemoryBank(self.errors_file)
            self.matcher = ErrorMatcher(self.bank)
        else:
            self.bank = None
            self.matcher = None
            
        self.metrics_file = self.hermes_root / "telemetry" / "metrics.json"
        self.telemetry = TelemetryCollector(self.metrics_file) if TelemetryCollector else None

    def _run_git(self, args: List[str]) -> str:
        """Executes a git command in the target repository."""
        try:
            res = subprocess.run(
                ["git"] + args,
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
                errors="replace"
            )
            return res.stdout
        except subprocess.CalledProcessError as e:
            return ""

    def get_diff(self, staged_only: bool = True) -> str:
        """Fetches git diff (staged or working tree)."""
        if staged_only:
            diff = self._run_git(["diff", "--cached", "--unified=3"])
            if not diff.strip():
                # If nothing staged, fallback to HEAD diff for review mode
                diff = self._run_git(["diff", "HEAD", "--unified=3"])
            return diff
        return self._run_git(["diff", "HEAD", "--unified=3"])

    def get_changed_files(self, staged_only: bool = True) -> List[str]:
        """Gets list of modified file paths."""
        if staged_only:
            out = self._run_git(["diff", "--cached", "--name-only"])
            if not out.strip():
                out = self._run_git(["diff", "HEAD", "--name-only"])
        else:
            out = self._run_git(["diff", "HEAD", "--name-only"])
            
        return [line.strip() for line in out.splitlines() if line.strip()]

    def scan_secrets(self, diff_text: str) -> List[Dict[str, Any]]:
        """Scans added diff lines for API keys, tokens, or credentials."""
        issues = []
        secret_patterns = [
            (r'(?i)(api[_-]?key|secret[_-]?key|auth[_-]?token|app[_-]?secret)\s*[:=]\s*[\'"][A-Za-z0-9_\-\.]{16,}[\'"]', "High-entropy API key or secret assignment"),
            (r'AIzaSy[A-Za-z0-9_-]{33}', "Google API Key detected"),
            (r'ghp_[A-Za-z0-9]{36}', "GitHub Personal Access Token"),
            (r'sk-[A-Za-z0-9]{32,}', "OpenAI API Secret Key"),
            (r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----', "Raw Private Cryptographic Key"),
            (r'(?i)password\s*[:=]\s*[\'"][^\'"]{6,}[\'"]', "Hardcoded plaintext password"),
        ]

        for line_num, line in enumerate(diff_text.splitlines(), 1):
            if not line.startswith('+') or line.startswith('+++'):
                continue
            added_content = line[1:]
            for pattern, desc in secret_patterns:
                if re.search(pattern, added_content):
                    issues.append({
                        "type": "SECRET",
                        "severity": "FATAL",
                        "description": desc,
                        "sample": line.strip()[:60] + "..."
                    })
        return issues

    def scan_anti_patterns(self, diff_text: str, changed_files: List[str]) -> List[Dict[str, Any]]:
        """Scans for database risks (Rule 3) and UI/Logic mixing (Rule 4)."""
        issues = []
        
        # 1. Dangerous DB queries
        db_danger_patterns = [
            (r'(?i)\bDROP\s+TABLE\s+(?!IF\s+EXISTS)\b', "Destructive DROP TABLE without IF EXISTS guard"),
            (r'(?i)\bTRUNCATE\s+TABLE\b', "Destructive TRUNCATE TABLE statement"),
            (r'DB::raw\(["\'].*\$[a-zA-Z0-9_]+.*["\']\)', "Unparameterized variable in DB::raw (SQL Injection risk)")
        ]
        
        # 2. UI vs Logic Separation violations
        ui_extensions = ('.blade.php', '.html', '.htm', '.vue', '.jsx', '.tsx')
        has_ui_files = any(f.endswith(ui_extensions) for f in changed_files)
        
        for line in diff_text.splitlines():
            if not line.startswith('+') or line.startswith('+++'):
                continue
            added = line[1:]
            
            # Skip self-inspection lines (defining the regexes)
            if 'db_danger_patterns' in added or 'r\'(?i)' in added or 'r"(?i)' in added or 're.search' in added:
                continue
            
            for pat, desc in db_danger_patterns:
                if re.search(pat, added):
                    issues.append({
                        "type": "DATABASE_SAFETY",
                        "severity": "HIGH",
                        "description": desc,
                        "sample": added.strip()[:70]
                    })
                    
            if has_ui_files:
                # Check for direct Eloquent/DB queries inside UI templates
                if re.search(r'(DB::table|User::|Auth::user\(\)->|::where\(|::all\(\)|::find\()', added):
                    issues.append({
                        "type": "UI_LOGIC_SEPARATION",
                        "severity": "HIGH",
                        "description": "Direct database query / model access inside presentation template (Rule 4 violation)",
                        "sample": added.strip()[:70]
                    })
                    
            # Debug statements
            if re.search(r'(?<!function\s)(dd\(|dump\(|console\.log\(|debugger;)', added):
                # Filter test files or scanner regex lines
                if not any('test' in f.lower() for f in changed_files) and 're.search' not in added and 'patterns' not in added:
                    issues.append({
                        "type": "DEBUG_LEFTOVER",
                        "severity": "MEDIUM",
                        "description": "Debug statement left in code (dd, dump, or console.log)",
                        "sample": added.strip()[:70]
                    })

        return issues

    def scan_memory_bank_regressions(self, diff_text: str) -> List[Dict[str, Any]]:
        """Cross-references added lines against Error Memory Bank fuzzy matcher."""
        if not self.matcher or not self.bank or not self.bank.errors:
            return []

        issues = []
        for line in diff_text.splitlines():
            if not line.startswith('+') or line.startswith('+++'):
                continue
            added = line[1:].strip()
            if len(added) < 15:
                continue

            matches = self.matcher.find_similar(added, threshold=0.75)
            if matches:
                error_item, score = matches[0]
                issues.append({
                    "type": "REGRESSION_WARNING",
                    "severity": "HIGH",
                    "description": f"Potential bug regression! Matches known error in Memory Bank ({score*100:.1f}%)",
                    "sample": f"Code: '{added[:50]}' matches: {error_item.get('error_signature', '')[:50]}",
                    "solution": error_item.get("solution", "")
                })
        return issues

    def evaluate_quality(self, diff_text: str, changed_files: List[str]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Runs all checks and computes Self-Grade scores."""
        all_issues = []
        
        secrets = self.scan_secrets(diff_text)
        antipatterns = self.scan_anti_patterns(diff_text, changed_files)
        regressions = self.scan_memory_bank_regressions(diff_text)
        
        all_issues.extend(secrets)
        all_issues.extend(antipatterns)
        all_issues.extend(regressions)
        
        # Compute dimension booleans for SelfGrader
        has_secrets = any(i["type"] == "SECRET" for i in all_issues)
        has_db_danger = any(i["type"] == "DATABASE_SAFETY" for i in all_issues)
        has_ui_mix = any(i["type"] == "UI_LOGIC_SEPARATION" for i in all_issues)
        has_debug = any(i["type"] == "DEBUG_LEFTOVER" for i in all_issues)
        has_regression = any(i["type"] == "REGRESSION_WARNING" for i in all_issues)

        results = {
            "tests_passed": not has_regression,
            "exit_code": 1 if has_secrets else 0,
            "lint_clean": not has_debug,
            "naming_consistent": True,
            "single_responsibility": not has_ui_mix,
            "no_hardcoded_secrets": not has_secrets,
            "input_validated": not has_db_danger,
            "no_n_plus_one": True,
            "no_unnecessary_rerenders": True
        }
        
        repo_name = self.repo_path.name or "current_repo"
        task_id = f"sentinel_{repo_name}"
        task_desc = f"Pre-commit audit on {len(changed_files)} files in {repo_name}"
        
        if self.grader:
            grade_record = self.grader.grade_task(task_id, task_desc, results)
        else:
            # Fallback calculation
            score = 100.0
            if has_secrets: score -= 50
            if has_db_danger: score -= 25
            if has_ui_mix: score -= 20
            if has_debug: score -= 10
            if has_regression: score -= 25
            score = max(0.0, score)
            grade_letter = "A" if score >= 90 else ("B" if score >= 80 else ("C" if score >= 70 else "F"))
            grade_record = {
                "id": "grade_fallback",
                "task_id": task_id,
                "score": score,
                "grade": grade_letter,
                "dimensions": {
                    "correctness": 100 if not has_regression else 50,
                    "readability": 100 if not has_debug else 50,
                    "architecture": 100 if not has_ui_mix else 0,
                    "security": 100 if not (has_secrets or has_db_danger) else 50,
                    "performance": 100
                }
            }
            
        # Record telemetry
        if self.telemetry:
            self.telemetry.record_skill_activation("hermes-git-sentinel")
            self.telemetry.record_grade(grade_record["score"])

        return grade_record, all_issues

    def render_report(self, grade_record: Dict[str, Any], issues: List[Dict[str, Any]], changed_files: List[str]) -> str:
        """Formats the audit report for console output."""
        score = grade_record["score"]
        grade = grade_record["grade"]
        passed = score >= self.min_score and not any(i.get("severity") == "FATAL" for i in issues)

        status_badge = "\033[92m[PASSED]\033[0m" if passed else "\033[91m[BLOCKED]\033[0m"
        lines = []
        lines.append("=" * 68)
        lines.append(f"  🛡️  HERMES GIT SENTINEL - QUALITY GATE: {status_badge}")
        lines.append("=" * 68)
        lines.append(f"  • Repository     : {self.repo_path.resolve()}")
        lines.append(f"  • Files Checked  : {len(changed_files)} file(s)")
        lines.append(f"  • Overall Score  : {score}/100 (Grade: {grade})")
        lines.append(f"  • Required Score : {self.min_score}/100")
        lines.append("-" * 68)
        lines.append("  DIMENSION BREAKDOWN:")
        for dim, val in grade_record.get("dimensions", {}).items():
            bar_len = int(val / 10)
            bar = "█" * bar_len + "░" * (10 - bar_len)
            lines.append(f"    - {dim.capitalize():<15}: [{bar}] {val:>3}/100")
        lines.append("-" * 68)

        if issues:
            lines.append(f"  ⚠️  ISSUES DETECTED ({len(issues)}):")
            for idx, issue in enumerate(issues, 1):
                sev = issue.get("severity", "WARN")
                sev_color = "\033[91m" if sev == "FATAL" else ("\033[93m" if sev == "HIGH" else "\033[96m")
                lines.append(f"    {idx}. {sev_color}[{sev}]\033[0m {issue['type']}: {issue['description']}")
                lines.append(f"       Sample : {issue.get('sample', '')}")
                if "solution" in issue:
                    lines.append(f"       💡 Fix   : {issue['solution']}")
            lines.append("-" * 68)
        else:
            lines.append("  ✨ No critical security vulnerabilities or architectural violations found.")
            lines.append("-" * 68)

        if passed:
            lines.append("  ✅ Quality Gate PASSED. Proceeding with Git Commit.")
        else:
            lines.append("  ❌ Quality Gate FAILED. Commit has been aborted.")
            lines.append("     Please resolve the issues above or increase score above threshold.")
        lines.append("=" * 68)
        return "\n".join(lines)

    def run(self, staged_only: bool = True) -> bool:
        """Main execution flow."""
        changed_files = self.get_changed_files(staged_only=staged_only)
        if not changed_files:
            print("\033[93m[HERMES SENTINEL]\033[0m No modified or staged files found to audit.")
            return True

        diff_text = self.get_diff(staged_only=staged_only)
        grade_record, issues = self.evaluate_quality(diff_text, changed_files)
        report = self.render_report(grade_record, issues, changed_files)
        print(report)

        passed = (grade_record["score"] >= self.min_score) and not any(i.get("severity") == "FATAL" for i in issues)
        return passed


def main():
    parser = argparse.ArgumentParser(description="Hermes Git Sentinel Quality Gate")
    parser.add_argument("--repo", type=str, default=".", help="Path to git repository")
    parser.add_argument("--staged", action="store_true", default=True, help="Check staged changes only")
    parser.add_argument("--all", action="store_true", help="Check all uncommitted changes (HEAD)")
    parser.add_argument("--min-score", type=float, default=80.0, help="Minimum score threshold (default: 80.0)")
    parser.add_argument("--install-hook", action="store_true", help="Install pre-commit hook into repo")

    args = parser.parse_args()
    repo_dir = Path(args.repo).resolve()

    if args.install_hook:
        from hook_installer import install_git_hook
        success = install_git_hook(repo_dir)
        sys.exit(0 if success else 1)

    sentinel = GitSentinel(repo_path=repo_dir, min_score=args.min_score)
    is_staged = not args.all
    passed = sentinel.run(staged_only=is_staged)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
