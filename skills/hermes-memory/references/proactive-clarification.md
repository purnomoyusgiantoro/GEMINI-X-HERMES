# Proactive Clarification Reference Guide

This reference outlines the exact cognitive protocol for Antigravity agents when disambiguating user requests.

---

## When to Trigger the Clarification Gate

Agents must trigger `ask_question` whenever:
1. **Target Ambiguity**: The user refers to a codebase, file, or component with an unknown location.
2. **Design Fork**: There are multiple valid technical approaches (e.g. monolithic vs modular, synchronous vs async, local vs cloud).
3. **Implicit Scope**: The user ask is broad (e.g. "buatkan sistem auth") without specifying providers, sessions, or persistence.
4. **Destructive or High-Impact Operations**: Migrating data, restructuring repos, or rewriting key modules.

---

## Formatting Rules for `ask_question`

- **Single Question Focus**: Address the primary bottleneck decision first. Do not overwhelm with multiple nested questions simultaneously.
- **Recommended Flag**: Always indicate `(Recommended)` on the primary option that follows project conventions and best practices.
- **Action-Oriented Options**: Options should describe the user's intent directly (e.g. `Simpan konfigurasi ke file lokal .env` rather than `Saya akan menyimpan ke .env`).
- **No Redundant Choices**: Do not include generic "Other" options as the UI provides a write-in input by default.
