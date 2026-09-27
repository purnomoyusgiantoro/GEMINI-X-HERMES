# Context Compaction & Working Memory Hygiene

Large Language Models operate within a finite context window. While models like Gemini feature massive context capacities, **context hygiene** remains paramount: as prompt transcripts fill up with thousands of lines of terminal output and raw file dumps, models experience attention dilution, slower latency, and increased risk of subtle hallucinations.

---

## 1. Principles of Working Memory Management

```
+-----------------------------------------------------------------------------+
|                          CONTEXT DEGRADATION HAZARD                         |
| Raw terminal dumps + full file reads  ===> Attention dilution & drift       |
+-----------------------------------------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
|                         HERMES CONTEXT COMPACTION                           |
| 1. Targeted File Slicing (StartLine / EndLine)                              |
| 2. High-Signal CLI Queries (filter at source)                               |
| 3. Trajectory Pruning (compact finished sub-tasks)                          |
| 4. Persistent Project Memory (.agents/CONTEXT.md / MEMORY.md)               |
+-----------------------------------------------------------------------------+
```

---

## 2. Tool-Use Precision Rules

### A. Surgical File Viewing
- **Anti-Pattern**: Dumping an entire 1,500-line file to check a single function signature.
- **Hermes Standard**: Inspect specific line ranges:
  ```json
  {
    "AbsolutePath": "C:/Projects/app/server.ts",
    "StartLine": 45,
    "EndLine": 75
  }
  ```

### B. Output Constrained Terminal Commands
- **Anti-Pattern**: Running unbounded `git log`, `Get-ChildItem -Recurse`, or full test suite outputs that produce 10,000 lines of logs.
- **Hermes Standard**: Filter at the source:
  ```powershell
  # Git log with count limit
  git log -n 5 --oneline

  # Search with depth and extension filters
  Get-ChildItem -Path .\src -Filter *.ts -Recurse | Select-Object -First 20 FullName
  ```

---

## 3. Project Memory Retention (`.agents/CONTEXT.md`)

To bridge context between distinct sessions without losing architectural decisions:

1. **Persistent Journal**: Every major codebase maintains a `.agents/CONTEXT.md` or `MEMORY.md` file.
2. **Contents**:
   - Architectural invariants and directory boundaries.
   - Non-standard commands (e.g. local Docker compose flags, test runners).
   - Known environmental quirks or workarounds discovered during past execution.
3. **Automatic Upkeep**: Whenever an unexpected environmental fix is discovered, record it immediately in `CONTEXT.md`.
