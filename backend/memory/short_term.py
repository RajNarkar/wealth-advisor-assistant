import time
from typing import Dict, Any, Optional
from backend.logger import get_logger

logger = get_logger("ShortTermMemory")

class ShortTermMemory:
    """In-memory session context storage for running pipelines and checkpoint interrupts."""

    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def init_session(self, session_id: str, client_id: str, initial_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        session_record = {
            "session_id": session_id,
            "client_id": client_id,
            "created_at": time.time(),
            "updated_at": time.time(),
            "status": "RUNNING",  # RUNNING, AWAITING_APPROVAL, APPROVED, REJECTED, COMPLETED, ERROR
            "human_approved": None,
            "human_override_note": "",
            "state": initial_data or {},
            "logs": [],
            "errors": []
        }
        self._sessions[session_id] = session_record
        logger.info(f"Initialized short-term session [{session_id}] for client [{client_id}].")
        return session_record

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self._sessions.get(session_id)

    def update_session(self, session_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if session_id not in self._sessions:
            logger.warning(f"Attempted to update non-existent session [{session_id}].")
            return None
        self._sessions[session_id].update(updates)
        self._sessions[session_id]["updated_at"] = time.time()
        return self._sessions[session_id]

    def add_log(self, session_id: str, message: str):
        if session_id in self._sessions:
            self._sessions[session_id]["logs"].append(message)
            logger.info(f"[{session_id}] {message}")

    def add_error(self, session_id: str, error_msg: str):
        if session_id in self._sessions:
            self._sessions[session_id]["errors"].append(error_msg)
            logger.error(f"[{session_id}] {error_msg}")

    def set_checkpoint_decision(self, session_id: str, approved: bool, note: str = ""):
        if session_id in self._sessions:
            self._sessions[session_id]["human_approved"] = approved
            self._sessions[session_id]["human_override_note"] = note
            self._sessions[session_id]["status"] = "APPROVED" if approved else "REJECTED"
            self.add_log(session_id, f"Human Checkpoint Decision: {'APPROVED' if approved else 'REJECTED'}. Note: '{note}'")

    def list_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        return self._sessions

short_term_memory = ShortTermMemory()
