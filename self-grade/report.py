from pathlib import Path
from typing import Any

try:
    from .grader import SelfGrader
except ImportError:
    from grader import SelfGrader

class GradeReporter:
    """Reporter for self-assessment grades."""

    def __init__(self, grader: SelfGrader):
        self.grader = grader

    def generate_summary(self) -> str:
        """Generate a markdown summary of all grades."""
        avg_score = self.grader.get_average_score()
        breakdown = self.grader.get_dimension_breakdown()
        history = self.grader.get_history(5)
        
        md = []
        md.append("# Self-Grading System Summary\n")
        md.append(f"**Overall Average Score:** {avg_score}/100\n")
        md.append("## Dimension Breakdown")
        for dim, score in breakdown.items():
            md.append(f"- **{dim.capitalize()}**: {score}")
            
        md.append("\n## Recent Tasks")
        for record in reversed(history):
            md.append(f"- **{record['task_id']}** ({record['task_description']}): Score {record['score']} ({record['grade']})")
            
        return "\n".join(md)

    def generate_trend_report(self) -> str:
        """Generate a markdown trend analysis."""
        trend = self.grader.get_trend()
        history = self.grader.get_history(10)
        
        md = []
        md.append("# Performance Trend Analysis\n")
        md.append(f"**Current Trend:** {trend.capitalize()}\n")
        
        md.append("## Last 10 Scores")
        for i, record in enumerate(history, 1):
            md.append(f"{i}. Task {record['task_id']}: {record['score']} ({record['grade']})")
            
        weakest = self.weakest_dimension()
        md.append(f"\n**Area for Improvement:** {weakest.capitalize()}")
        return "\n".join(md)

    def weakest_dimension(self) -> str:
        """Identify which dimension needs most improvement."""
        breakdown = self.grader.get_dimension_breakdown()
        if not breakdown:
            return "none"
        return min(breakdown.items(), key=lambda x: x[1])[0]

    def save_report(self, output_path: str | Path) -> None:
        """Save the markdown summary and trend report to a file."""
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        
        summary = self.generate_summary()
        trend = self.generate_trend_report()
        
        full_report = f"{summary}\n\n---\n\n{trend}"
        
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(full_report)


if __name__ == "__main__":
    import tempfile
    
    # Test block
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        grader = SelfGrader(tmp.name)
    
    grader.grade_task("task-1", "Test task 1", {
        "tests_passed": True, "exit_code": 0, "lint_clean": True,
        "naming_consistent": True, "single_responsibility": True,
        "no_hardcoded_secrets": True, "input_validated": True,
        "no_n_plus_one": True, "no_unnecessary_rerenders": True
    })
    
    reporter = GradeReporter(grader)
    print("Summary:")
    print(reporter.generate_summary())
    print("\nTrend Report:")
    print(reporter.generate_trend_report())
    
    report_path = Path("test_report.md")
    reporter.save_report(report_path)
    print(f"\nReport saved to {report_path.absolute()}")
