"""
Flask API endpoints for the pixel office dashboard.
"""
from typing import Any
import logging

try:
    from flask import Blueprint, jsonify, request, Flask
except ImportError:
    Blueprint = None
    Flask = None
    jsonify = None
    request = None

logger = logging.getLogger(__name__)

def create_telemetry_app(collector: Any) -> Any:
    """
    Create a Flask Blueprint for telemetry endpoints.
    
    Args:
        collector: Instance of TelemetryCollector
        
    Returns:
        Flask Blueprint
    """
    if Blueprint is None:
        raise ImportError("Flask is not installed. Run 'pip install flask'.")
        
    bp = Blueprint('telemetry', __name__, url_prefix='/api/telemetry')
    
    @bp.route('', methods=['GET'])
    def get_summary():
        return jsonify(collector.get_summary())
        
    @bp.route('/today', methods=['GET'])
    def get_today_summary():
        today_stats = collector.get_daily_summary()
        if today_stats:
            return jsonify(today_stats)
        return jsonify({"message": "Data untuk hari ini belum tersedia."}), 404
        
    @bp.route('/skills', methods=['GET'])
    def get_top_skills():
        n = request.args.get('n', default=5, type=int)
        top_skills = collector.get_top_skills(n)
        return jsonify({"top_skills": top_skills})
        
    @bp.route('/trend', methods=['GET'])
    def get_trend():
        metrics = collector.get_summary()
        return jsonify({"grade_trend": metrics.get("grade_trend", [])})
        
    @bp.route('/event', methods=['POST'])
    def record_event():
        data = request.json
        if not data or 'type' not in data:
            return jsonify({"error": "Missing event type"}), 400
            
        event_type = data['type']
        
        try:
            if event_type == 'task_complete':
                collector.record_task_complete(
                    task_id=data.get('task_id', 'unknown'),
                    description=data.get('description', ''),
                    duration_minutes=data.get('duration_minutes', 0),
                    was_bug=data.get('was_bug', False)
                )
            elif event_type == 'error':
                collector.record_error(data.get('category', 'unknown'))
            elif event_type == 'skill_activation':
                collector.record_skill_activation(data.get('skill_name', 'unknown'))
            elif event_type == 'skill_forged':
                collector.record_skill_forged(data.get('skill_name', 'unknown'))
            elif event_type == 'subagent_dispatch':
                collector.record_subagent_dispatch(data.get('agent_type', 'unknown'))
            elif event_type == 'grade':
                collector.record_grade(data.get('score', 0))
            else:
                return jsonify({"error": f"Unknown event type: {event_type}"}), 400
                
            return jsonify({"status": "success", "event": event_type}), 201
            
        except Exception as e:
            logger.error(f"Error recording event: {e}")
            return jsonify({"error": str(e)}), 500

    return bp

if __name__ == '__main__':
    if Flask is None:
        print("Flask is required to run the demo. Please install it.")
        import sys
        sys.exit(1)
        
    import os
    from pathlib import Path
    
    # Import collector (assuming we're running from the project root or telemetry dir)
    try:
        from collector import TelemetryCollector
    except ImportError:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from telemetry.collector import TelemetryCollector
        
    # Setup collector with a demo metrics file
    demo_metrics_path = Path(__file__).parent / "demo_metrics.json"
    demo_collector = TelemetryCollector(demo_metrics_path)
    
    # Setup Flask app
    app = Flask(__name__)
    telemetry_bp = create_telemetry_app(demo_collector)
    app.register_blueprint(telemetry_bp)
    
    print(f"Memulai server API telemetry demo pada port 19001...")
    print(f"Metrics tersimpan di: {demo_metrics_path}")
    print(f"Test endpoints:")
    print(f"  - GET http://localhost:19001/api/telemetry")
    print(f"  - GET http://localhost:19001/api/telemetry/today")
    
    app.run(port=19001, debug=True)
