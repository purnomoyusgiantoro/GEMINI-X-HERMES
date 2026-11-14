# MEMORY.md — GEMINI-X-HERMES

## 1. System Summary & Architecture
- **Application**: Autonomous Cognitive Intelligence Framework combining Google Gemini with NousResearch Hermes Agent for Google Antigravity
- **Local Path**: `D:\Documents\GEMINI-X-HERMES`
- **GitHub Remote**: `https://github.com/purnomoyusgiantoro/GEMINI-X-HERMES.git` (branch: `main`)
- **Tech Stack**: Python, PowerShell, Shell, Markdown, Antigravity Agent Skills (`hermes-cognition`, `hermes-git-sentinel`, `hermes-memory`, `hermes-model-router`, `switch-agy`)

## 2. Role & Access Matrix
- Developer/agent CLI tooling & skill framework installed into `~/.gemini/config/skills/` via `scripts/install.ps1` (Windows) or `scripts/install.sh` (Linux/macOS/WSL).

## 3. Core Domain Logic & Modules
- **3-Tier Cognitive Architecture** (`skills/hermes-cognition/`): Hypothesis-first framing, Mixture-of-Agents (MoA) subagent synthesis, and context compaction.
- **Git Sentinel** (`skills/hermes-git-sentinel/scripts/sentinel.py`): Pre-commit quality gate auditing secrets, destructive SQL, Rule 4 UI/Logic separation, and Error Memory Bank regressions (`--min-score 80.0`).
- **Memory Manager** (`skills/hermes-memory/scripts/memory_manager.py`): Synchronizes `~/.gemini/memory/projects.json`, `decisions.json`, and `~/.gemini/GEMINI.md`.
- **Self-Grading & Telemetry**: `self-grade/grades.json`, `telemetry/metrics.json`, `memory-bank/errors.json`.

## 4. Database Schema
- JSON-based persistent stores: `self-grade/grades.json`, `telemetry/metrics.json`, `memory-bank/errors.json`, and global `~/.gemini/memory/{projects,system_map,decisions}.json`.

## 5. Operational Procedures
```powershell
.\scripts\install.ps1
python "D:\Documents\GEMINI-X-HERMES\skills\hermes-git-sentinel\scripts\sentinel.py" --repo "<repo-path>" --staged
python "D:\Documents\GEMINI-X-HERMES\skills\hermes-memory\scripts\memory_manager.py" get-project <ProjectName>
```
