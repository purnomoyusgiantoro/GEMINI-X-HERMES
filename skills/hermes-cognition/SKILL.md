---
name: hermes-cognition
description: >-
  Hermes Agent-grade autonomous cognition, self-correction loops, memory retention, context compaction,
  and Mixture-of-Agents (MoA) synthesis for complex programming, debugging, and system orchestration.
  Activate when solving complex bugs, architecting deep systems, performing multi-agent reviews,
  or when the user requests rigorous, verified, and autonomous problem solving.
---

# Hermes Cognition: Autonomous Agentic Intelligence

> "Never guess when you can verify. Never claim completion without proof. Never repeat a failing path without changing the underlying state."

This skill distills the architectural intelligence of **Hermes Agent** (NousResearch) into a universal, high-leverage cognitive framework for Antigravity. It governs how the agent reasons, executes tools, diagnoses errors, retains project memory, and coordinates multi-agent synthesis.

---

## 1. Core Architecture (The Hermes Three-Tier System)

```
+-------------------------------------------------------------------+
| TIER 1: STABLE COGNITIVE PROTOCOL                                 |
| - Hypothesis-first analysis                                       |
| - Tool-use enforcement & strict guardrails                        |
| - 3-Strike rule against circular debugging loops                  |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| TIER 2: MIXTURE-OF-AGENTS & SUBAGENT SYNTHESIS                    |
| - Specialized subagent dispatch (Auditor, Reviewer, Tester)       |
| - Multi-perspective consensus & conflict resolution               |
| - Layered aggregation into clean, unified deliverables            |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| TIER 3: CONTEXT COMPACTION & PROJECT MEMORY                       |
| - Trajectory pruning (preventing context degradation)             |
| - Persistent state journaling (CONTEXT.md / MEMORY.md)            |
| - Empirical, evidence-based verification before completion        |
+-------------------------------------------------------------------+
```

---

## 2. The 4-Stage Hermes Execution Loop

Whenever assigned a non-trivial problem, bugfix, or feature implementation, execute through these 4 discrete stages:

### Stage 1: Hypothesis-First Goal Framing
1. **Understand Root Intent**: Identify the underlying objective, non-functional requirements, and potential side-effects.
2. **Formulate Falsifiable Hypothesis**: State *what* is expected to happen and *why*.
3. **Inspect Before Acting**: Use read tools (`view_file`, targeted commands) to establish the baseline before touching code or state.

### Stage 2: Evidence-Based Execution & Tool Enforcement
1. **Minimal Surface Area Changes**: Only edit lines directly related to the fix or feature.
2. **Preserve Existing Semantics**: Do not strip existing comments, type annotations, or unrelated structures.
3. **Capture Raw Tool Results**: Always evaluate return codes, stderr, and stdout directly. Never assume a background command succeeded without checking.

### Stage 3: Systematic Error Classification & Recovery
If a command or test fails, immediately invoke the [Error Classification Protocol](references/error-classification.md):
- **Classify**: Categorize the failure into `Syntax`, `Dependency`, `Runtime`, `Logic`, or `Environment`.
- **Apply the 3-Strike Rule**: Never execute the exact same failing command more than once without changing code or environment parameters.
- **Isolate**: If still failing on attempt 3, construct a minimal reproduction script in `scratch/repro.*` to isolate the bug before proceeding.

### Stage 4: Mixture-of-Agents (MoA) Synthesis
For complex architecture, security-sensitive logic, or large-scale refactors, invoke the [Mixture-of-Agents Protocol](references/mixture-of-agents.md):
- Dispatch specialized subagents via `invoke_subagent` (`security-auditor`, `code-reviewer`, `test-engineer`).
- Act as the Aggregator: synthesize disparate recommendations, resolve trade-offs, and produce a unified implementation.

---

## 3. Context Compaction & Working Memory Hygiene

To prevent context window bloat and "hallucination under large contexts":
- Refer to the [Memory & Context Compaction Protocol](references/memory-and-state.md).
- Keep tool output lean: slice line numbers with `StartLine`/`EndLine` rather than dumping entire files.
- Summarize multi-step intermediate outputs into clean, high-signal progress reports.
- Persist lasting decisions in `.agents/CONTEXT.md` or `MEMORY.md`.

---

## 4. The Completion Contract (Zero-Hallucination Gate)

An assignment is **NEVER** marked complete based on assumption. Completion requires concrete proof:

1. **Deterministic Verification**: Run tests, linters, or execution commands that demonstrate the code works as expected.
2. **Visible Evidence**: Display the passing test output or exit code `0` to the user.
3. **Clean Teardown**: Remove temporary scratch files, background debugging processes, or transient state before handing off.
