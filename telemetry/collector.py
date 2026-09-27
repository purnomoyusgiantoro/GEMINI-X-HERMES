"""
Metrics collection engine for GEMINI X HERMES v2.
"""
import json
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)

class TelemetryCollector:
    """Collects and manages cognitive telemetry metrics."""
    
    def __init__(self, metrics_path: Union[str, Path]):
        """Initialize the telemetry collector."""
        self.metrics_path = Path(metrics_path)
        self.metrics = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Load metrics from file or return default structure if not found."""
        if self.metrics_path.exists():
            try:
                with open(self.metrics_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load metrics: {e}")
                
        # Default structure
        return {
            "session_start": None,
            "total_tasks_completed": 0,
            "total_bugs_solved": 0,
            "total_errors_encountered": 0,
            "total_skills_forged": 0,
            "total_subagent_dispatches": 0,
            "average_resolution_minutes": 0,
            "skill_activations": {},
            "daily_log": [],
            "grade_trend": []
        }
        
    def _save(self) -> None:
        """Save current metrics to file."""
        try:
            self.metrics_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.metrics_path, "w", encoding="utf-8") as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    def _get_or_create_daily_entry(self, today_str: str) -> Dict[str, Any]:
        """Get the daily log entry for today, or create it if missing."""
        for entry in self.metrics["daily_log"]:
            if entry["date"] == today_str:
                return entry
                
        # Create new entry
        new_entry = {
            "date": today_str,
            "tasks_completed": 0,
            "bugs_solved": 0,
            "errors_encountered": 0,
            "avg_grade": 0,
            "skills_forged": 0,
            "focus_minutes": 0
        }
        self.metrics["daily_log"].append(new_entry)
        return new_entry

    def start_session(self) -> None:
        """Record session start time."""
        self.metrics["session_start"] = datetime.utcnow().isoformat()
        self._save()
        
    def record_task_complete(self, task_id: str, description: str, duration_minutes: float, was_bug: bool = False) -> None:
        """Record completion of a task or bug fix."""
        self.metrics["total_tasks_completed"] += 1
        if was_bug:
            self.metrics["total_bugs_solved"] += 1
            
        # Update running average resolution time
        total = self.metrics["total_tasks_completed"]
        current_avg = self.metrics["average_resolution_minutes"]
        self.metrics["average_resolution_minutes"] = ((current_avg * (total - 1)) + duration_minutes) / total
        
        # Update daily log
        today_str = date.today().isoformat()
        daily = self._get_or_create_daily_entry(today_str)
        daily["tasks_completed"] += 1
        if was_bug:
            daily["bugs_solved"] += 1
        daily["focus_minutes"] += duration_minutes
        
        self._save()

    def record_error(self, error_category: str) -> None:
        """Record an encountered error."""
        self.metrics["total_errors_encountered"] += 1
        
        today_str = date.today().isoformat()
        daily = self._get_or_create_daily_entry(today_str)
        daily["errors_encountered"] += 1
        
        self._save()
        
    def record_skill_activation(self, skill_name: str) -> None:
        """Record activation of a specific skill."""
        if skill_name not in self.metrics["skill_activations"]:
            self.metrics["skill_activations"][skill_name] = 0
        self.metrics["skill_activations"][skill_name] += 1
        self._save()
        
    def record_skill_forged(self, skill_name: str) -> None:
        """Record forging of a new skill."""
        self.metrics["total_skills_forged"] += 1
        
        today_str = date.today().isoformat()
        daily = self._get_or_create_daily_entry(today_str)
        daily["skills_forged"] += 1
        
        self._save()
        
    def record_subagent_dispatch(self, agent_type: str) -> None:
        """Record dispatch of a subagent."""
        self.metrics["total_subagent_dispatches"] += 1
        self._save()
        
    def record_grade(self, score: float) -> None:
        """Record a performance grade."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "score": score
        }
        self.metrics["grade_trend"].append(entry)
        
        # Update daily average
        today_str = date.today().isoformat()
        daily = self._get_or_create_daily_entry(today_str)
        
        # Recalculate daily average
        today_grades = [
            g["score"] for g in self.metrics["grade_trend"] 
            if g["timestamp"].startswith(today_str)
        ]
        if today_grades:
            daily["avg_grade"] = sum(today_grades) / len(today_grades)
            
        self._save()
        
    def get_summary(self) -> Dict[str, Any]:
        """Return all current metrics."""
        return dict(self.metrics)
        
    def get_daily_summary(self, target_date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Return stats for a specific day (defaults to today)."""
        if target_date is None:
            target_date = date.today().isoformat()
            
        for entry in self.metrics["daily_log"]:
            if entry["date"] == target_date:
                return dict(entry)
        return None
        
    def get_top_skills(self, n: int = 5) -> List[tuple[str, int]]:
        """Return the most frequently activated skills."""
        activations = self.metrics.get("skill_activations", {})
        sorted_skills = sorted(activations.items(), key=lambda x: x[1], reverse=True)
        return sorted_skills[:n]
