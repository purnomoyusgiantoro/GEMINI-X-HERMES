# Task-to-Model Routing Decision Matrix

## Classification Signals

Use these signals to determine task tier automatically:

### Tier S Signals (Deep Reasoning Required)
- User uses words: "desain", "arsitektur", "review", "audit", "brainstorm", "analisis", "rancang", "debug kompleks"
- Task involves trade-off evaluation between multiple approaches
- Task requires reading and synthesizing >5 files simultaneously
- Task involves security, correctness proofs, or architectural invariants
- Output is a design doc, spec, or architectural decision record (ADR)

### Tier A Signals (Standard Execution)
- User uses words: "buat", "implementasi", "tulis", "edit", "fix", "refactor", "test"
- Task has a clear spec or pattern to follow
- Task involves writing code, running commands, or editing files
- Output is working code, passing tests, or completed file edits

### Tier B Signals (Trivial / Lightweight)
- User uses words: "cek", "lihat", "status", "format", "rename", "copy", "typo"
- Task requires no creative problem-solving
- Task is a single command or minor text change
- Output is a status check, simple lookup, or formatting fix

---

## Subagent Model Selection Cheat Sheet

```
invoke_subagent:
  Role: "Code Reviewer"        → Model: "pro"
  Role: "Security Auditor"     → Model: "pro"
  Role: "Test Engineer"        → Model: "flash"
  Role: "Codebase Researcher"  → Model: "flash"
  Role: "File Editor"          → Model: "flash"
  Role: "Documentation Writer" → Model: "flash"
  Role: "Quick Lookup"         → Model: "flash_lite"
  Role: "Format Checker"       → Model: "flash_lite"
```

---

## Rate Limit Detection Patterns

The agent should watch for these indicators:
1. HTTP 429 responses or "rate limit exceeded" error messages
2. Unusually slow response times (>30s for simple operations)
3. Repeated connection timeouts on a specific model
4. User explicitly says "limit", "lambat", "slow", or "ganti model"

When detected, suggest the next model down in the cascade:
- Don't auto-switch without user consent
- Frame it as a temporary measure: "Sementara limit reset..."
- Track which model hit the limit so the agent can suggest returning later
