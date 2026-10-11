import requests
from typing import Dict, Any, List, Optional

BACKEND_BASE_URL = "http://127.0.0.1:8000"

class BackendAPIClient:
    """Centralized HTTP client querying FastAPI backend endpoints."""

    def __init__(self, base_url: str = BACKEND_BASE_URL):
        self.base_url = base_url.rstrip("/")

    def get_health(self) -> Dict[str, Any]:
        try:
            resp = requests.get(f"{self.base_url}/api/health", timeout=5)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"status": "offline", "error": str(e)}

    def get_clients(self) -> List[Dict[str, Any]]:
        try:
            resp = requests.get(f"{self.base_url}/api/clients", timeout=5)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return []

    def get_client_details(self, client_id: str) -> Optional[Dict[str, Any]]:
        try:
            resp = requests.get(f"{self.base_url}/api/clients/{client_id}", timeout=5)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return None

    def trigger_analysis(self, client_id: str) -> Dict[str, Any]:
        try:
            resp = requests.post(f"{self.base_url}/api/analyze", json={"client_id": client_id}, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        try:
            resp = requests.get(f"{self.base_url}/api/session/{session_id}/status", timeout=5)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e), "status": "UNKNOWN"}

    def get_checkpoint_status(self, session_id: str) -> Dict[str, Any]:
        try:
            resp = requests.get(f"{self.base_url}/api/checkpoint/{session_id}/status", timeout=5)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def approve_checkpoint(self, session_id: str, note: str = "") -> Dict[str, Any]:
        try:
            resp = requests.post(f"{self.base_url}/api/checkpoint/{session_id}/approve", json={"note": note}, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def reject_checkpoint(self, session_id: str, note: str = "") -> Dict[str, Any]:
        try:
            resp = requests.post(f"{self.base_url}/api/checkpoint/{session_id}/reject", json={"note": note}, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def get_client_memory(self, client_id: str) -> Dict[str, Any]:
        try:
            resp = requests.get(f"{self.base_url}/api/memory/{client_id}", timeout=5)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e), "sessions": []}

    def get_active_sessions(self) -> Dict[str, Any]:
        try:
            resp = requests.get(f"{self.base_url}/api/memory/sessions/active", timeout=5)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {}

api_client = BackendAPIClient()
