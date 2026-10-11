import json
import os
import time
from typing import Dict, Any, List, Optional
from backend.logger import get_logger

logger = get_logger("LongTermMemory")
DEFAULT_STORE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory_store")

class LongTermMemory:
    """Persistent JSON-based historical memory for clients across sessions."""

    def __init__(self, store_dir: Optional[str] = None):
        self.store_dir = store_dir or DEFAULT_STORE_DIR
        os.makedirs(self.store_dir, exist_ok=True)

    def _get_file_path(self, client_id: str) -> str:
        return os.path.join(self.store_dir, f"{client_id}.json")

    def get_history(self, client_id: str) -> Dict[str, Any]:
        path = self._get_file_path(client_id)
        if not os.path.exists(path):
            return {
                "client_id": client_id,
                "sessions_count": 0,
                "sessions": [],
                "cumulative_notes": "First engagement. No historical session record exists."
            }
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read long-term memory for client {client_id}: {e}")
            return {"client_id": client_id, "sessions_count": 0, "sessions": [], "cumulative_notes": "Memory read error."}

    def get_formatted_memory_context(self, client_id: str) -> str:
        data = self.get_history(client_id)
        sessions = data.get("sessions", [])
        if not sessions:
            return "No previous advisory consultations on record. Treat as initial review."

        lines = [f"Client {client_id} Historical Consultations Summary ({len(sessions)} prior session(s)):"]
        for s in sessions[-3:]:  # Last 3 sessions for prompt token efficiency
            date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(s.get("timestamp", time.time())))
            anomalies = s.get("anomalies_detected", 0)
            summary = s.get("summary", "N/A")
            lines.append(f"- Date: {date_str} | Anomalies: {anomalies} | Notes: {summary}")

        if data.get("cumulative_notes"):
            lines.append(f"Cumulative Pattern Notes: {data.get('cumulative_notes')}")

        return "\n".join(lines)

    def record_session(
        self,
        client_id: str,
        session_id: str,
        analysis_report: Dict[str, Any],
        advisory_summary: str
    ):
        data = self.get_history(client_id)
        sessions: List[Dict[str, Any]] = data.get("sessions", [])

        anomalies_count = len(analysis_report.get("anomalies", []))
        new_entry = {
            "session_id": session_id,
            "timestamp": time.time(),
            "anomalies_detected": anomalies_count,
            "risk_score": analysis_report.get("risk_score", 50),
            "summary": advisory_summary[:200] + "..." if len(advisory_summary) > 200 else advisory_summary
        }
        sessions.append(new_entry)
        data["sessions"] = sessions
        data["sessions_count"] = len(sessions)
        data["last_updated"] = time.time()

        # Update cumulative note
        if anomalies_count > 0:
            data["cumulative_notes"] = f"Client has recurring anomaly flags ({anomalies_count} in latest session). Continuous monitoring advised."
        else:
            data["cumulative_notes"] = "Client portfolio stabilized within expected parameters."

        path = self._get_file_path(client_id)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            logger.info(f"Updated long-term memory for client [{client_id}]. Total sessions: {len(sessions)}")
        except Exception as e:
            logger.error(f"Failed to write long-term memory for client {client_id}: {e}")

long_term_memory = LongTermMemory()
