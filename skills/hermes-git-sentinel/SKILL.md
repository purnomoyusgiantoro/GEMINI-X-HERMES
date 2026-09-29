---
name: hermes-git-sentinel
description: >-
  Automated quality gate, self-grading evaluator, and pre-commit security guardian for Git workflows.
  Audits staged or working-tree changes for hardcoded secrets, destructive SQL, UI vs Logic separation
  violations, and Error Memory Bank regressions before committing or pushing code.
---

# Hermes Git Sentinel: Autonomous Quality Gate & Pre-Commit Shield

> "Quality is not an accident; it is the result of continuous cognitive inspection."

`hermes-git-sentinel` acts as an autonomous guardian that bridges the **Self-Grading Engine**, the **Error Memory Bank**, and the **Cognitive Telemetry Engine** directly into the Git development cycle.

---

## 1. 🛡️ What Git Sentinel Checks

Before any commit is accepted, Sentinel inspects the diff across 5 rigorous dimensions:

| Dimension | Inspection Targets | Hard Blocker? |
| :--- | :--- | :--- |
| **Security** | Hardcoded API keys (Google, OpenAI, GitHub), private keys, plaintext passwords | 🚨 **YES (Fatal)** |
| **Database Safety** | Unverified `DROP TABLE`, `TRUNCATE TABLE`, unescaped raw SQL variables | ⚠️ **YES (High)** |
| **Architecture (Rule 4)** | Direct database calls (`DB::`, `Model::`) inside presentation templates (Blade/HTML/Vue) | ⚠️ **YES (High)** |
| **Error Regression** | Re-introduction of bug signatures registered in the `memory-bank/errors.json` | ⚠️ **YES (High)** |
| **Readability & Cleanliness**| Leftover debug statements (`dd()`, `dump()`, `console.log()`, `debugger;`) | ℹ️ Score penalty |

---

## 2. 🚀 Quick Usage

### A. Run Audit on Staged Changes:
```powershell
python "D:\Documents\GEMINI-X-HERMES\skills\hermes-git-sentinel\scripts\sentinel.py" --staged
# Or using the PowerShell helper:
& "D:\Documents\GEMINI-X-HERMES\skills\hermes-git-sentinel\scripts\sentinel.ps1"
```

### B. Audit Working Tree (Uncommitted Changes):
```powershell
python "D:\Documents\GEMINI-X-HERMES\skills\hermes-git-sentinel\scripts\sentinel.py" --all
```

### C. Audit Another Registered Project (e.g., `pajak_symotech`):
```powershell
python "D:\Documents\GEMINI-X-HERMES\skills\hermes-git-sentinel\scripts\sentinel.py" --repo "D:\Documents\symotech_projek\pajak_symotech" --staged
```

### D. Install Pre-Commit Hook into Any Repository:
```powershell
python "D:\Documents\GEMINI-X-HERMES\skills\hermes-git-sentinel\scripts\hook_installer.py" "D:\Documents\symotech_projek\pajak_symotech"
```

---

## 3. 🚦 Quality Gate Thresholds

* **Passing Score**: $\ge 80.0$ (Grade B or higher).
* **Hard Blockers**:
  * Any detected credential/secret aborts the commit immediately (Exit Code 1).
  * Any regression with $\ge 75\%$ similarity to a past resolved bug drops the correctness score and triggers a warning.

---

## 4. 🔗 Ecosystem Connections

1. **Self-Grading Engine**: Every run records an entry in `self-grade/grades.json` evaluating correctness, readability, architecture, security, and performance.
2. **Error Memory Bank**: Powered by `memory-bank/matcher.py` with fuzzy sequence matching.
3. **Cognitive Telemetry**: Increments `hermes-git-sentinel` activations and tracks quality score trends in `telemetry/metrics.json`.
