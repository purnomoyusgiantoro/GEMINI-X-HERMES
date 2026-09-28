#!/usr/bin/env python3
"""
Hermes Memory Manager - Cross-Session Persistent Registry & Decision Log
Part of the GEMINI X HERMES Cognitive Architecture.
"""

import os
import sys
import json
import argparse
from datetime import datetime

GEMINI_DIR = os.path.expanduser("~/.gemini")
MEMORY_DIR = os.path.join(GEMINI_DIR, "memory")
PROJECTS_FILE = os.path.join(MEMORY_DIR, "projects.json")
DECISIONS_FILE = os.path.join(MEMORY_DIR, "decisions.json")
GEMINI_MD_FILE = os.path.join(GEMINI_DIR, "GEMINI.md")

def ensure_storage():
    os.makedirs(MEMORY_DIR, exist_ok=True)
    if not os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
            json.dump({"version": "1.0", "projects": {}}, f, indent=2)
    if not os.path.exists(DECISIONS_FILE):
        with open(DECISIONS_FILE, "w", encoding="utf-8") as f:
            json.dump({"version": "1.0", "decisions": []}, f, indent=2)

def load_projects():
    ensure_storage()
    with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_projects(data):
    ensure_storage()
    data["last_updated"] = datetime.now().isoformat()
    with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_decisions():
    ensure_storage()
    with open(DECISIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_decisions(data):
    ensure_storage()
    with open(DECISIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def add_project(name, path, description="", repo_url="", tech_stack=None):
    data = load_projects()
    data["projects"][name] = {
        "path": os.path.abspath(path),
        "description": description,
        "repo_url": repo_url,
        "tech_stack": tech_stack or [],
        "last_registered": datetime.now().isoformat()
    }
    save_projects(data)
    print(f"[OK] Project '{name}' registered at: {os.path.abspath(path)}")
    sync_gemini_md()

def get_project(name):
    data = load_projects()
    proj = data.get("projects", {}).get(name)
    if not proj:
        # Fuzzy case-insensitive search
        for k, v in data.get("projects", {}).items():
            if k.lower() == name.lower():
                return k, v
        return None, None
    return name, proj

def list_projects():
    data = load_projects()
    projs = data.get("projects", {})
    print("\n=== REGISTERED PROJECTS (HERMES MEMORY) ===")
    if not projs:
        print("No projects registered.")
    for name, p in projs.items():
        print(f"- {name}:")
        print(f"    Path: {p.get('path')}")
        print(f"    Desc: {p.get('description', '-')}")
        if p.get('repo_url'):
            print(f"    Repo: {p.get('repo_url')}")
    print("===========================================\n")

def log_decision(project, summary):
    data = load_decisions()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "project": project,
        "summary": summary
    }
    data.setdefault("decisions", []).append(entry)
    save_decisions(data)
    print(f"[OK] Decision logged for '{project}': {summary}")

def list_decisions(project=None):
    data = load_decisions()
    decs = data.get("decisions", [])
    if project:
        decs = [d for d in decs if d.get("project", "").lower() == project.lower()]
    print(f"\n=== DECISION LOGS {'(' + project + ')' if project else ''} ===")
    for d in decs[-10:]:
        print(f"[{d.get('timestamp')[:19]}] ({d.get('project')}) {d.get('summary')}")
    print("=========================================\n")

def sync_gemini_md():
    data = load_projects()
    projs = data.get("projects", {})
    
    rows = []
    for name, p in projs.items():
        desc = p.get('description', '')
        rows.append(f"| **`{name}`** | `{p.get('path')}` | {desc} |")
    
    table_content = "\n".join(rows) if rows else "| *None* | *None* | *None* |"
    
    md_content = f"""# Global Antigravity Directives & Persistent Memory

> "Never guess when you can verify. Never wander when you can clarify."

---

## 1. 🧠 Persistent Project Registry (Cross-Session Recall)

Antigravity agents running on this machine must refer to this project index first before searching the filesystem:

| Project Name | Path | Description / Tech Stack |
| :--- | :--- | :--- |
{table_content}

Full machine-readable registry and decision history are maintained in:
- `~/.gemini/memory/projects.json`
- `~/.gemini/memory/decisions.json`

When the user mentions any known project or asks about past activities, query `~/.gemini/memory/` immediately.

---

## 2. 🎯 Proactive Clarification Gate (Brainstorming Pattern)

Whenever an agent encounters:
1. **Ambiguous or underspecified requests** (e.g., "bikin fitur X", "pindahkan ini", or referencing an unknown project)
2. **Uncertainty about paths, architectural decisions, or tools**
3. **Missing parameters or unclear goals**

### The Inviolable Clarification Rule:
> **DO NOT GUESS.** Do not execute blind exploratory searches across arbitrary directories.  
> **IMMEDIATELY CALL `ask_question`** to present an interactive multiple-choice modal to the user.

### Question Requirements:
- Title must clearly state the specific ambiguity or decision point.
- Provide 2–4 concrete, distinct options.
- The highest-confidence or most standard option must be placed first and prefixed with `(Recommended)`.
- Format options as the user's direct choice/action.
- Once the user selects an option, execute that specific path with full verification.
"""
    with open(GEMINI_MD_FILE, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"[OK] Synced ~/.gemini/GEMINI.md with {len(projs)} projects.")

def main():
    parser = argparse.ArgumentParser(description="Hermes Memory Manager")
    subparsers = parser.add_subparsers(dest="command")

    # list-projects
    subparsers.add_parser("list-projects")

    # get-project
    p_get = subparsers.add_parser("get-project")
    p_get.add_argument("name")

    # add-project
    p_add = subparsers.add_parser("add-project")
    p_add.add_argument("name")
    p_add.add_argument("path")
    p_add.add_argument("--desc", default="")
    p_add.add_argument("--repo", default="")

    # log-decision
    p_log = subparsers.add_parser("log-decision")
    p_log.add_argument("project")
    p_log.add_argument("summary")

    # list-decisions
    p_ld = subparsers.add_parser("list-decisions")
    p_ld.add_argument("--project", default=None)

    # sync
    subparsers.add_parser("sync")

    args = parser.parse_args()

    if args.command == "list-projects":
        list_projects()
    elif args.command == "get-project":
        name, p = get_project(args.name)
        if p:
            print(json.dumps({name: p}, indent=2))
        else:
            print(f"Project '{args.name}' not found.")
            sys.exit(1)
    elif args.command == "add-project":
        add_project(args.name, args.path, args.desc, args.repo)
    elif args.command == "log-decision":
        log_decision(args.project, args.summary)
    elif args.command == "list-decisions":
        list_decisions(args.project)
    elif args.command == "sync":
        sync_gemini_md()
    else:
        list_projects()

if __name__ == "__main__":
    main()
