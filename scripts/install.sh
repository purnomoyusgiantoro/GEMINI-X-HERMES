#!/usr/bin/env bash
#
# GEMINI X HERMES - Autonomous Skill Installer (Linux / macOS / WSL)
# Installs hermes-cognition globally (~/.gemini/config/skills) or to a project (.agents/skills)
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$(dirname "$SCRIPT_DIR")/skills/hermes-cognition"

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

if [ ! -d "$SOURCE_DIR" ]; then
    echo "[-] Error: Source directory $SOURCE_DIR does not exist."
    exit 1
fi

if [ "$MODE" = "global" ]; then
    TARGET_BASE="$HOME/.gemini/config/skills"
    TARGET_DIR="$TARGET_BASE/hermes-cognition"
    echo "[+] Target: Global Antigravity Config ($TARGET_BASE)"
else
    TARGET_PROJECT="${TARGET_PROJECT:-$(pwd)}"
    TARGET_BASE="$TARGET_PROJECT/.agents/skills"
    TARGET_DIR="$TARGET_BASE/hermes-cognition"
    echo "[+] Target: Local Project Workspace ($TARGET_PROJECT)"
fi

mkdir -p "$TARGET_BASE"

echo "[*] Copying skill files from $SOURCE_DIR..."
cp -R "$SOURCE_DIR" "$TARGET_BASE/"

if [ -f "$TARGET_DIR/SKILL.md" ]; then
    echo ""
    echo "[SUCCESS] Hermes Cognition skill installed successfully!"
    echo "Location: $TARGET_DIR"
    echo "Antigravity will automatically discover 'hermes-cognition' on startup."
else
    echo "[-] Error: SKILL.md not found in $TARGET_DIR after copy."
    exit 1
fi
