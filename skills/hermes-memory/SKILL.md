---
name: hermes-memory
description: >-
  Long-term cross-session memory recall and proactive clarification gate.
  Use when recalling past projects, workspaces, or architectural decisions,
  and when user intent is ambiguous, underspecified, or requires interactive
  multiple-choice brainstorming via ask_question instead of guessing or blind searching.
---

# Hermes Memory: Cross-Session Recall & Proactive Clarification

> "Never guess when you can verify. Never wander when you can clarify."

This skill provides Google Antigravity agents with **Episodic Long-Term Memory** across sessions and an **Active Clarification Gate** inspired by the Brainstorming protocol.

---

## 1. Cross-Session Project & Context Recall

Antigravity sessions start with a clean working memory. This skill establishes an anchor to persist and retrieve project knowledge:

### Memory Hierarchy:
1. **Universal Memory Anchor**: `~/.gemini/GEMINI.md` (read automatically on session start).
2. **Machine-Readable Project Registry**: `~/.gemini/memory/projects.json`.
3. **Architectural Decision Journal**: `~/.gemini/memory/decisions.json`.

### How to Recall a Project:
When the user mentions a project (e.g., `GEMINI-X-HERMES`, `SISTEM_TANI`, `portofolio`):
```powershell
python "D:\Documents\GEMINI-X-HERMES\skills\hermes-memory\scripts\memory_manager.py" get-project <ProjectName>
```
**Rule**: Do NOT scan random drives or folders when a project is registered in the memory bank.

---

## 2. 🎯 The Proactive Clarification Gate (Brainstorming Pattern)

### Anti-Pattern: Blind Wandering & Silent Guessing
When the user says something ambiguous, mentions an unknown repository, or requests a feature with multiple viable paths:
- ❌ **Forbidden**: Silently guessing what the user wants.
- ❌ **Forbidden**: Running broad, recursive file searches across entire drives.
- ❌ **Forbidden**: Writing implementation code before confirming intent.

### The Required Clarification Flow:
Whenever confidence in requirements or target location is `<90%`:
1. **STOP immediately**. Do not run side-effect commands or scaffold code.
2. **Formulate Clarifying Options**:
   - Synthesize 2 to 4 concrete, actionable choices.
   - Designate the most idiomatic/standard path as `(Recommended)` and place it first.
   - Format each option as the user's direct choice.
3. **Trigger Interactive Modal via `ask_question`**:
   ```json
   {
     "questions": [
       {
         "question": "Pertanyaan spesifik dan jelas mengenai kebutuhan atau lokasi:",
         "is_multi_select": false,
         "options": [
           "(Recommended) Opsi A: ...",
           "Opsi B: ...",
           "Opsi C: ..."
         ]
       }
     ]
   }
   ```
4. **Execute Selected Path with Proof**:
   Only proceed with implementation or operations after the user picks an option.

---

## 3. Memory Consolidation Protocol

When completing a milestone, registering a new project, or making an architectural change:
1. **Register Project (if new)**:
   ```powershell
   python "D:\Documents\GEMINI-X-HERMES\skills\hermes-memory\scripts\memory_manager.py" add-project <name> <path> --desc "<summary>"
   ```
2. **Log Decision / Milestone**:
   ```powershell
   python "D:\Documents\GEMINI-X-HERMES\skills\hermes-memory\scripts\memory_manager.py" log-decision <project> "<summary of change>"
   ```
3. **Synchronize Anchor**:
   The script automatically keeps `~/.gemini/GEMINI.md` up-to-date with registered projects.
