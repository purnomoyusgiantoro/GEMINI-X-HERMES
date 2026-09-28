#!/usr/bin/env bash
#
# GEMINI X HERMES - Autonomous Skill Installer (Linux / macOS / WSL)
# Installs all skills globally (~/.gemini/config/skills) or to a project (.agents/skills)
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
SKILLS_SOURCE="$REPO_ROOT/skills"

MODE="global"
TARGET_PROJECT=""

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --local) MODE="local"; TARGET_PROJECT="${2:-.}"; shift ;;
        --global) MODE="global" ;;
        -h|--help)
            echo "Usage: ./install.sh [--global | --local [project_path]]"
            exit 0
            ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

echo "=========================================================="
echo "    GEMINI X HERMES - Autonomous Skill Installer (POSIX)   "
echo "=========================================================="

if [ ! -d "$SKILLS_SOURCE" ]; then
    echo "[-] Error: Source directory $SKILLS_SOURCE does not exist."
    exit 1
fi

if [ "$MODE" = "global" ]; then
    TARGET_BASE="$HOME/.gemini/config/skills"
    echo "[+] Target: Global Antigravity Config ($TARGET_BASE)"
else
    TARGET_PROJECT="${TARGET_PROJECT:-$(pwd)}"
    TARGET_BASE="$TARGET_PROJECT/.agents/skills"
    echo "[+] Target: Local Project Workspace ($TARGET_PROJECT)"
fi

mkdir -p "$TARGET_BASE"

echo "[*] Copying skills from $SKILLS_SOURCE..."
for skill in "$SKILLS_SOURCE"/*; do
    if [ -d "$skill" ]; then
        skill_name="$(basename "$skill")"
        echo "[*] Installing skill: $skill_name -> $TARGET_BASE/$skill_name"
        cp -R "$skill" "$TARGET_BASE/"
    fi
done

# If switch-agy scripts exist, copy to ~/.local/bin or agy bin if available
AGY_BIN="$HOME/.local/bin"
if [ -d "$SKILLS_SOURCE/switch-agy/scripts" ]; then
    mkdir -p "$AGY_BIN"
    cp "$SKILLS_SOURCE/switch-agy/scripts/switch-agy-core.py" "$AGY_BIN/switch-agy" 2>/dev/null || true
    chmod +x "$AGY_BIN/switch-agy" 2>/dev/null || true
fi

echo ""
echo "[SUCCESS] All skills installed successfully!"
echo "Antigravity will automatically discover 'hermes-cognition' and 'switch-agy' on startup."
