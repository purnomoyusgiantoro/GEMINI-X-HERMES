---
name: hermes-model-router
description: >-
  Intelligent model routing and automatic delegation for multi-model AI workflows.
  Use when the user wants to optimize model usage across tasks: Claude for deep thinking,
  brainstorming, and architecture review; Gemini Flash for fast code execution and file I/O;
  and auto-downgrade to lighter models when tasks are trivial or rate limits are hit.
  Activates on /model-router, "ganti model otomatis", "pakai claude buat mikir", or
  when dispatching subagents that would benefit from model-specific strengths.
---

# Hermes Model Router: Intelligent Multi-Model Orchestration

> "Use the right brain for the right job. Heavy thinking deserves heavy models. Fast execution deserves fast models."

This skill teaches Antigravity agents to **automatically select and delegate** to the optimal AI model for each phase of a task, maximizing quality while conserving premium model quota.

---

## 1. Model Tier Classification

### Tier S — Deep Reasoning (Brainstorming, Architecture, Review)
**Models**: `claude-opus-4-6-thinking`, `gemini-3.1-pro-high`
**When to use**:
- Architectural design decisions & trade-off analysis
- Complex debugging requiring multi-step hypothesis chains
- Code review across security, performance, and correctness axes
- Brainstorming sessions, spec writing, and design documents
- Ambiguous requirements that need creative problem-solving

### Tier A — Balanced Execution (Standard Coding, Research)
**Models**: `gemini-3.8-flash-high`, `claude-sonnet-4-6`
**When to use**:
- Writing implementation code from a clear spec
- Running tests and interpreting results
- File editing, refactoring, and code generation
- Research lookups and documentation reading
- Standard git operations and deployment tasks

### Tier B — Fast & Light (Simple Tasks, Bulk Operations)
**Models**: `gemini-3.8-flash-medium`, `gemini-3.8-flash-low`, `gemini-3.7-flash-medium`
**When to use**:
- Simple file reads, directory listings, status checks
- Formatting, linting, and trivial code fixes
- Repetitive bulk operations (rename, copy, template expansion)
- Quick Q&A that doesn't require deep reasoning
- Fallback when rate limits are hit on higher-tier models

---

## 2. Automatic Routing Protocol

### For the Main Agent (You):
When processing a user request, classify the task complexity before acting:

```
IF task is { brainstorming, architecture, design review, complex debug, spec writing }:
    → Stay on current model if it's Tier S (Claude Opus / Gemini Pro)
    → If current model is Tier A/B, SUGGEST: "Tugas ini membutuhkan deep reasoning.
      Pertimbangkan ganti ke Claude Opus via /model untuk hasil terbaik."

IF task is { code implementation, file editing, test running, git operations }:
    → Delegate to subagent with model='flash' when possible
    → If working directly, Tier A is optimal

IF task is { simple lookup, status check, formatting, trivial fix }:
    → Delegate to subagent with model='flash_lite' when possible
    → If working directly, any tier works (don't waste premium quota)
```

### For Subagent Delegation:
When dispatching subagents via `invoke_subagent`, select the Model argument intelligently:

| Task Type | Subagent Model | Rationale |
|:---|:---|:---|
| Security audit, code review, architecture analysis | `pro` | Deep multi-dimensional reasoning |
| Research, file reading, web search, documentation | `flash` | Fast retrieval, no deep reasoning needed |
| Code implementation from clear spec | `flash` or `inherit` | Speed over depth for known patterns |
| Simple file ops, formatting, bulk tasks | `flash_lite` | Minimal resources for trivial work |
| Complex debugging, root cause analysis | `pro` or `inherit` | Needs hypothesis chains and verification |

---

## 3. Rate Limit Awareness & Auto-Downgrade

When a model returns a rate limit error or the agent detects slowdowns:

### Downgrade Cascade:
```
claude-opus-4-6-thinking  →  claude-sonnet-4-6  →  gemini-3.8-flash-high
gemini-3.1-pro-high       →  gemini-3.8-flash-high  →  gemini-3.8-flash-medium
gemini-3.8-flash-high     →  gemini-3.8-flash-medium  →  gemini-3.8-flash-low
```

### How to Suggest Model Change to User:
When the agent detects the current model is suboptimal for the task at hand:

```
"💡 Model Suggestion: Tugas ini [bersifat ringan / membutuhkan deep thinking].
Anda saat ini menggunakan [current model].
Pertimbangkan beralih ke [suggested model] via /model untuk [alasan]."
```

**Never force a model change.** Always suggest and let the user decide.

---

## 4. Workflow Examples

### Example A: Full Feature Development
```
Phase 1 - Brainstorming (Tier S: Claude Opus)
  User: "Desain sistem autentikasi untuk app kita"
  → Agent stays on Claude Opus for design thinking
  → Produces spec document with trade-off analysis

Phase 2 - Implementation (Tier A: Gemini Flash High)
  → Agent suggests: "Spec sudah siap. /model ke Gemini Flash High untuk eksekusi cepat."
  → Or: Dispatches subagent(model='flash') for code writing

Phase 3 - Review (Tier S: Claude Opus)
  → Agent suggests: "Implementasi selesai. /model ke Claude Opus untuk review mendalam."
  → Or: Dispatches code-reviewer subagent(model='pro')
```

### Example B: Quick Fix
```
User: "Fix typo di README"
→ Agent recognizes Tier B task
→ Executes directly (no model change needed)
→ Does NOT suggest upgrading to Claude for a typo fix
```

### Example C: Rate Limit Hit
```
User on Claude Opus hits rate limit mid-task
→ Agent detects error
→ Suggests: "Rate limit tercapai pada Claude Opus.
  Saya sarankan beralih ke Gemini 3.8 Flash High via /model
  untuk melanjutkan eksekusi. Brainstorming bisa dilanjutkan
  setelah limit reset."
```

---

## 5. Integration with Hermes Cognition

This skill works alongside `hermes-cognition`:
- **Stage 1 (Hypothesis Framing)** → Tier S model recommended
- **Stage 2 (Evidence-Based Execution)** → Tier A model, delegate to flash subagents
- **Stage 3 (Error Classification)** → Tier S for complex errors, Tier A for simple retries
- **Stage 4 (Verification)** → Tier A for test execution, Tier S for final review

---

## 6. Available Models Reference

| Model ID | Display Name | Tier | Best For |
|:---|:---|:---|:---|
| `claude-opus-4-6-thinking` | Claude Opus 4.6 (Thinking) | S | Deep reasoning, architecture, review |
| `gemini-3.1-pro-high` | Gemini 3.1 Pro (High) | S | Complex analysis, large context |
| `claude-sonnet-4-6` | Claude Sonnet 4.6 (Thinking) | A | Balanced reasoning + speed |
| `gemini-3.8-flash-high` | Gemini 3.8 Flash (High) | A | Fast coding, execution |
| `gemini-3.8-flash-medium` | Gemini 3.8 Flash (Medium) | B | Light tasks, bulk ops |
| `gemini-3.8-flash-low` | Gemini 3.8 Flash (Low) | B | Minimal, fallback |
| `gemini-3.7-flash-high` | Gemini 3.7 Flash (High) | A | Stable alternative |
| `gpt-oss-120b-medium` | GPT-OSS 120B (Medium) | A | Alternative perspective |
