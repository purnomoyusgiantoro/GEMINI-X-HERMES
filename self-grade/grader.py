import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

class SelfGrader:
    """Self-assessment engine for GEMINI X HERMES v2."""

    def __init__(self, grades_path: str | Path):
        self.grades_path = Path(grades_path)
        self.grades: List[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        """Load grades from the database, creating it if it doesn't exist."""
        if self.grades_path.exists():
            try:
                with open(self.grades_path, 'r', encoding='utf-8') as f:
                    self.grades = json.load(f)
            except json.JSONDecodeError:
                self.grades = []
        else:
            self.grades = []
            self._save()

    def _save(self) -> None:
        """Save grades to the database."""
        self.grades_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.grades_path, 'w', encoding='utf-8') as f:
            json.dump(self.grades, f, indent=2)

    def grade_task(self, task_id: str, task_description: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate task results and assign a score and grade.
        
        Args:
            task_id: Unique identifier for the task.
            task_description: Description of the task.
            results: Dictionary containing boolean/integer results for different metrics.
            
        Returns:
            Dictionary containing the final grade record.
        """
        # Correctness: tests_passed (50) + exit_code == 0 (50)
        correctness_score = 0
        if results.get('tests_passed'): correctness_score += 50
        if results.get('exit_code') == 0: correctness_score += 50
        
        # Readability: lint_clean (50) + naming_consistent (50)
        readability_score = 0
        if results.get('lint_clean'): readability_score += 50
        if results.get('naming_consistent'): readability_score += 50
            
        # Architecture: single_responsibility (100)
        architecture_score = 100 if results.get('single_responsibility') else 0
        
        # Security: no_hardcoded_secrets (50) + input_validated (50)
        security_score = 0
        if results.get('no_hardcoded_secrets'): security_score += 50
        if results.get('input_validated'): security_score += 50
            
        # Performance: no_n_plus_one (50) + no_unnecessary_rerenders (50)
        performance_score = 0
        if results.get('no_n_plus_one'): performance_score += 50
        if results.get('no_unnecessary_rerenders'): performance_score += 50

        # Calculate final score based on weights
        final_score = (
            correctness_score * 0.30 +
            readability_score * 0.20 +
            architecture_score * 0.20 +
            security_score * 0.15 +
            performance_score * 0.15
        )
        
        # Determine grade letter
        if final_score >= 95: grade_letter = "A+"
        elif final_score >= 90: grade_letter = "A"
        elif final_score >= 85: grade_letter = "B+"
        elif final_score >= 80: grade_letter = "B"
        elif final_score >= 75: grade_letter = "C+"
        elif final_score >= 70: grade_letter = "C"
        elif final_score >= 60: grade_letter = "D"
        else: grade_letter = "F"
            
        grade_record = {
            "id": f"grade_{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task_id": task_id,
            "task_description": task_description,
            "score": round(final_score, 2),
            "grade": grade_letter,
            "dimensions": {
                "correctness": correctness_score,
                "readability": readability_score,
                "architecture": architecture_score,
                "security": security_score,
                "performance": performance_score
            }
        }
        
        self.grades.append(grade_record)
        self._save()
        return grade_record

    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Return the most recent grades."""
        return self.grades[-limit:] if limit > 0 else []

    def get_average_score(self) -> float:
        """Calculate the overall average score."""
        if not self.grades:
            return 0.0
        total = sum(g.get("score", 0) for g in self.grades)
        return round(total / len(self.grades), 2)

    def get_trend(self, last_n: int = 10) -> str:
        """Determine the trend of the last N grades."""
        recent = self.grades[-last_n:]
        if len(recent) < 2:
            return "stable"
            
        scores = [g.get("score", 0) for g in recent]
        x = list(range(len(scores)))
        x_mean = sum(x) / len(x)
        y_mean = sum(scores) / len(scores)
        
        numerator = sum((x_i - x_mean) * (y_i - y_mean) for x_i, y_i in zip(x, scores))
        denominator = sum((x_i - x_mean) ** 2 for x_i in x)
        
        if denominator == 0:
            return "stable"
            
        slope = numerator / denominator
        if slope > 0.5:
            return "improving"
        elif slope < -0.5:
            return "declining"
        else:
            return "stable"

    def get_dimension_breakdown(self) -> Dict[str, float]:
        """Calculate the average score for each dimension."""
        if not self.grades:
            return {
                "correctness": 0.0,
                "readability": 0.0,
                "architecture": 0.0,
                "security": 0.0,
                "performance": 0.0
            }
            
        totals = {
            "correctness": 0.0,
            "readability": 0.0,
            "architecture": 0.0,
            "security": 0.0,
            "performance": 0.0
        }
        
        for g in self.grades:
            dims = g.get("dimensions", {})
            for k in totals.keys():
                totals[k] += dims.get(k, 0)
                
        count = len(self.grades)
        return {k: round(v / count, 2) for k, v in totals.items()}

if __name__ == "__main__":
    # Test block
    grader = SelfGrader(Path("grades.json"))
    sample_results = {
        "tests_passed": True,
        "exit_code": 0,
        "lint_clean": True,
        "naming_consistent": False,
        "single_responsibility": True,
        "no_hardcoded_secrets": True,
        "input_validated": False,
        "no_n_plus_one": True,
        "no_unnecessary_rerenders": True
    }
    res = grader.grade_task("task-xyz", "Fix Pomodoro timer bug", sample_results)
    print("Graded:", res)
    print("Average Score:", grader.get_average_score())
    print("Trend:", grader.get_trend())
    print("Dimension Breakdown:", grader.get_dimension_breakdown())
