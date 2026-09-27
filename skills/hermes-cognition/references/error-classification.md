# Hermes Error Classification & Self-Correction Protocol

Adapted from Hermes Agent (`agent/error_classifier.py` & `agent/turn_retry_state.py`).

When an operation fails or tests produce an unexpected result, do not guess or randomly modify code. Follow this rigorous classification protocol.

---

## 1. Error Taxonomy

Every error encountered must be classified into one of the following 5 categories:

| Category | Typical Symptoms | Root Causes | Remediation Protocol |
| :--- | :--- | :--- | :--- |
| **1. Syntax / Parse** | `SyntaxError`, unexpected token, indent errors | Malformed AST, unmatched brackets, escaping bugs | Locate exact line & column. Inspect surrounding 10 lines. Re-check syntax before retrying. |
| **2. Import / Dependency** | `ModuleNotFoundError`, `ImportError`, unfulfilled DLL | Missing package, virtualenv mismatch, broken PATH | Verify active interpreter, check `pip list` / `node_modules`. Do not blindly edit code; check environment first. |
| **3. Runtime / State** | `NullPointerException`, `AttributeError`, `IndexError` | Uninitialized variables, unexpected nulls, timing race | Trace call stack backwards to origin of `None`/`null`. Add defensive guardrails and type checks. |
| **4. Logic / Assertion** | Unit test failure, unexpected output, semantic diff | Algorithmic flaw, off-by-one, inverted conditional | Contrast expected output vs actual output. Re-examine problem constraints and boundary conditions. |
| **5. Environment / I/O** | `EACCES`, `AccessDenied`, timeout, network error | Elevated rights needed, locked files, port in use | Check running processes, inspect file locks, check port listeners. Never force repeat without changing preconditions. |

---

## 2. The 3-Strike Rule (Anti-Loop Guardrail)

To prevent circular reasoning or infinite retry loops:
- **Attempt 1**: Root cause fix based on classified error.
- **Attempt 2**: Alternative approach if the first fix fails to eliminate the error.
- **Attempt 3**: If still failing, stop and isolate the failure into a minimal reproducible scratch test (`scratch/test_repro.*`). Present findings and alternatives to the user.
- **Never repeat the identical failing command without modifying the underlying state.**

---

## 3. Evidence-First Verification

Before marking any fix as complete:
1. Re-run the exact failing command or test suite.
2. Confirm exit code is `0` and expected output matches the acceptance criteria.
3. Verify that adjacent functionality did not regress.
