"""
Error Memory Bank CRUD operations module.
"""
import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional

class ErrorCategory(str, Enum):
    SYNTAX = "Syntax"
    DEPENDENCY = "Dependency"
    RUNTIME = "Runtime"
    LOGIC = "Logic"
    ENVIRONMENT = "Environment"

class ErrorMemoryBank:
    """Manages the storage and retrieval of error solutions."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.errors: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        """Loads errors from the database file."""
        if self.db_path.exists():
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    self.errors = json.load(f)
            except json.JSONDecodeError:
                self.errors = []
        else:
            self.errors = []
            self._save()

    def _save(self) -> None:
        """Saves current errors to the database file."""
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self.errors, f, indent=2, ensure_ascii=False)

    def add_error(self, category: ErrorCategory | str, error_signature: str, root_cause: str, solution: str, context: Optional[Dict[str, str]] = None) -> str:
        """Adds a new error to the memory bank."""
        if context is None:
            context = {"project": "", "file": "", "stack": ""}
            
        error_id = f"err_{uuid.uuid4().hex[:8]}"
        
        # Validate enum
        cat_val = category.value if isinstance(category, ErrorCategory) else category

        new_error = {
            "id": error_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "category": cat_val,
            "error_signature": error_signature,
            "root_cause": root_cause,
            "solution": solution,
            "context": context,
            "reuse_count": 0,
            "confidence": 1.0
        }
        self.errors.append(new_error)
        self._save()
        return error_id

    def find_by_signature(self, signature: str) -> Optional[Dict[str, Any]]:
        """Exact match lookup by error signature."""
        for error in self.errors:
            if error["error_signature"] == signature:
                return error
        return None

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Searches across signature, root_cause, and solution fields."""
        query_lower = query.lower()
        results = []
        for error in self.errors:
            if (query_lower in error["error_signature"].lower() or 
                query_lower in error["root_cause"].lower() or 
                query_lower in error["solution"].lower()):
                results.append(error)
        return results

    def increment_reuse(self, error_id: str) -> bool:
        """Bumps reuse_count when a solution is reused."""
        for error in self.errors:
            if error["id"] == error_id:
                error["reuse_count"] += 1
                self._save()
                return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics about the error bank."""
        total_errors = len(self.errors)
        categories: Dict[str, int] = {}
        for error in self.errors:
            cat = error.get("category", "Unknown")
            categories[cat] = categories.get(cat, 0) + 1
            
        sorted_by_reuse = sorted(self.errors, key=lambda x: x.get("reuse_count", 0), reverse=True)
        most_reused = sorted_by_reuse[:5]

        return {
            "total_errors": total_errors,
            "categories": categories,
            "most_reused": most_reused
        }

    def export_markdown(self) -> str:
        """Exports the entire bank as a formatted markdown string."""
        lines = ["# Error Memory Bank\n"]
        for error in self.errors:
            lines.append(f"## [{error['category']}] {error['id']}")
            lines.append(f"**Timestamp:** {error['timestamp']}")
            lines.append(f"**Reuse Count:** {error['reuse_count']} | **Confidence:** {error['confidence']}")
            lines.append(f"\n### Signature\n```\n{error['error_signature']}\n```")
            lines.append(f"### Root Cause\n{error['root_cause']}")
            lines.append(f"### Solution\n{error['solution']}")
            lines.append("---\n")
        return "\n".join(lines)

if __name__ == "__main__":
    bank = ErrorMemoryBank("test_errors.json")
    bank.add_error(
        category=ErrorCategory.RUNTIME,
        error_signature="TypeError: 'NoneType' object is not iterable",
        root_cause="Function returned None instead of a list",
        solution="Add a check for None before iterating, or ensure function returns an empty list.",
        context={"project": "test", "file": "main.py", "stack": ""}
    )
    print(bank.get_stats())
    print(bank.export_markdown())
    # Cleanup
    if Path("test_errors.json").exists():
        Path("test_errors.json").unlink()
