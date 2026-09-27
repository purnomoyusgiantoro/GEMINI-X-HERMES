# Hermes Memory & Context Compaction Protocol

Adapted from Hermes Agent (`agent/context_compressor.py`, `agent/memory_manager.py`, and `trajectory_compressor.py`).

In extended coding sessions, LLM performance degrades if the context window is flooded with redundant output, verbose logs, and unstructured chatter. Hermes Cognition implements systematic context hygiene and project memory retention.

---

## 1. Context Pruning (Keep Trajectory Razor-Sharp)

1. **Prune Verbose Tool Outputs**:
   - When inspecting large files, never cat the whole file if only 20 lines matter. Use targeted line ranges (`StartLine`/`EndLine`).
   - When running search commands (`grep`, `find`, `Get-ChildItem`), constrain depth and filter early to prevent multi-megabyte terminal outputs.
2. **Compress Completed Sub-tasks**:
   - Once a task or sub-step is finished and verified, maintain a mental "Historical Task Snapshot". Do not re-evaluate already solved sub-tasks unless new evidence indicates a regression.

---

## 2. Project Memory & Attestation (`CONTEXT.md` / `MEMORY.md`)

When working on a persistent repository or complex project:
1. **Persistent Context File**: Maintain or update a `.agents/CONTEXT.md` or `MEMORY.md` at the project root for:
   - System architecture and key design choices.
   - Non-standard development commands (how to run dev server, build, test).
   - User preferences and domain-specific vocabulary.
2. **State Journaling**:
   - If an unexpected environmental quirk or critical workaround is discovered during execution, document it immediately so future interactions do not repeat the discovery cost.
