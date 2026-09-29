#!/usr/bin/env python3
"""
Hermes Model Router - Intelligent Multi-Model Orchestration Engine.
Directs tasks to the optimal AI model tier and handles auto-downgrade cascades.
"""
import sys
import re
import json
import argparse
from typing import Dict, Any, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

TIER_S_MODELS = ["claude-opus-4-6-thinking", "gemini-3.1-pro-high"]
TIER_A_MODELS = ["gemini-3.8-flash-high", "claude-sonnet-4-6", "gemini-3.7-flash-high"]
TIER_B_MODELS = ["gemini-3.8-flash-medium", "gemini-3.8-flash-low", "gemini-3.7-flash-medium"]

DOWNGRADE_CASCADE = {
    "claude-opus-4-6-thinking": "gemini-3.8-flash-high",
    "gemini-3.1-pro-high": "gemini-3.8-flash-high",
    "claude-sonnet-4-6": "gemini-3.8-flash-high",
    "gemini-3.8-flash-high": "gemini-3.8-flash-medium",
    "gemini-3.8-flash-medium": "gemini-3.8-flash-low",
}

SUBAGENT_MODEL_MAP = {
    "security-auditor": "pro",
    "code-reviewer": "pro",
    "architect": "pro",
    "research": "flash",
    "test-engineer": "flash",
    "web-performance-auditor": "flash",
    "formatter": "flash_lite",
    "status-checker": "flash_lite",
}


class ModelRouter:
    """Evaluates task complexity and suggests optimal model routing."""

    def classify_task(self, prompt: str) -> Dict[str, Any]:
        """Classifies a task prompt into Tier S, Tier A, or Tier B."""
        p = prompt.lower()

        # Tier S indicators: Deep reasoning, architecture, security, design, trade-offs
        tier_s_keywords = [
            "brainstorm", "arsitektur", "architecture", "design", "security audit",
            "threat model", "trade-off", "analisis mendalam", "spec", "refactor subsystem",
            "root cause", "investigasi bug rumit", "multi-step"
        ]
        
        # Tier B indicators: Trivial, formatting, quick check, typos
        tier_b_keywords = [
            "typo", "formatting", "status", "list file", "cek commit", "rename",
            "simple fix", "quick check", "baca baris"
        ]

        # Check Tier S first
        for kw in tier_s_keywords:
            if kw in p:
                return {
                    "tier": "Tier S",
                    "category": "Deep Reasoning & Architecture",
                    "recommended_models": TIER_S_MODELS,
                    "subagent_model": "pro",
                    "reason": f"Detected high-cognition requirement (keyword: '{kw}')"
                }

        # Check Tier B
        for kw in tier_b_keywords:
            if kw in p:
                return {
                    "tier": "Tier B",
                    "category": "Lightweight & Bulk Operations",
                    "recommended_models": TIER_B_MODELS,
                    "subagent_model": "flash_lite",
                    "reason": f"Detected trivial/bulk task requirement (keyword: '{kw}')"
                }

        # Default to Tier A
        return {
            "tier": "Tier A",
            "category": "Balanced Execution & Standard Coding",
            "recommended_models": TIER_A_MODELS,
            "subagent_model": "flash",
            "reason": "Standard coding, file modification, or test execution task"
        }

    def get_subagent_model(self, role: str) -> str:
        """Determines the appropriate model tier for an Antigravity subagent."""
        role_normalized = role.lower().strip()
        for key, model in SUBAGENT_MODEL_MAP.items():
            if key in role_normalized:
                return model
        return "flash"

    def get_downgrade(self, current_model: str) -> Optional[str]:
        """Returns the fallback model if current_model encounters rate limits."""
        for key, fallback in DOWNGRADE_CASCADE.items():
            if key in current_model.lower():
                return fallback
        return "gemini-3.8-flash-medium"

    def route(self, task_prompt: str, current_model: str = "gemini-3.8-flash-high") -> Dict[str, Any]:
        """Produces full routing recommendation."""
        classification = self.classify_task(task_prompt)
        target_tier = classification["tier"]
        
        current_tier = "Tier A"
        if any(m in current_model.lower() for m in TIER_S_MODELS):
            current_tier = "Tier S"
        elif any(m in current_model.lower() for m in TIER_B_MODELS):
            current_tier = "Tier B"

        is_optimal = (current_tier == target_tier)
        suggestion = None
        if not is_optimal:
            rec_model = classification["recommended_models"][0]
            suggestion = (
                f"💡 Model Suggestion: Tugas ini tergolong {target_tier} ({classification['category']}). "
                f"Model aktif saat ini: {current_model}. "
                f"Pertimbangkan beralih ke {rec_model} untuk performa optimal."
            )

        return {
            "task": task_prompt,
            "current_model": current_model,
            "current_tier": current_tier,
            "target_tier": target_tier,
            "category": classification["category"],
            "subagent_model": classification["subagent_model"],
            "is_optimal": is_optimal,
            "suggestion": suggestion,
            "fallback_on_rate_limit": self.get_downgrade(current_model)
        }


def main():
    parser = argparse.ArgumentParser(description="Hermes Model Router")
    parser.add_argument("prompt", nargs="?", default="", help="Task prompt to classify")
    parser.add_argument("--current-model", default="gemini-3.8-flash-high", help="Current active model")
    parser.add_argument("--subagent", help="Get model for a specific subagent role")
    parser.add_argument("--downgrade", help="Get downgrade target for a model")

    args = parser.parse_args()
    router = ModelRouter()

    if args.subagent:
        m = router.get_subagent_model(args.subagent)
        print(f"Subagent '{args.subagent}' -> model: {m}")
        return

    if args.downgrade:
        d = router.get_downgrade(args.downgrade)
        print(f"Downgrade from '{args.downgrade}' -> {d}")
        return

    if not args.prompt:
        parser.print_help()
        return

    result = router.route(args.prompt, args.current_model)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
