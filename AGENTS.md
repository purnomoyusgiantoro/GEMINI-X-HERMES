# Agent Directives: GEMINI X HERMES

Welcome to the **GEMINI X HERMES** repository. All AI agents, contributors, and pairing systems interacting with this project must strictly comply with the following directives.

---

## 1. Zero-Hallucination Policy
- Never claim a task, script, or change is working without running verification tools and providing tangible output.
- Always report exit codes and actual test output.

## 2. Minimal Surface Area Edits
- When editing documentation or code, only touch the exact target lines.
- Preserve existing formatting, comments, and structure.

## 3. 3-Strike Debugging Rule
- If a command fails, classify the failure into: `Syntax`, `Dependency`, `Runtime`, `Logic`, or `Environment`.
- Never re-execute the identical failing command without modifying underlying code or parameters.
- If failing on attempt 3, isolate the problem in `scratch/` and consult the user.

## 4. Context Hygiene
- Do not dump entire large files into terminal context. Use slice parameters (`StartLine`/`EndLine`).
- Keep persistent discoveries in `.agents/CONTEXT.md`.
