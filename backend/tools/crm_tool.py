import json
import os
from typing import Dict, Any, Optional
from backend.tools.base_tool import BaseTool

CRM_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mock_data", "crm_data.json")

class CRMTool(BaseTool):
    name: str = "CRMTool"
    description: str = "Fetches client relationship metadata, KYC verification, advisor notes, and life events from CRM API."

    def __init__(self, crm_path: Optional[str] = None):
        self.crm_path = crm_path or CRM_PATH

    def run(self, client_id: str, **kwargs) -> Dict[str, Any]:
        if not os.path.exists(self.crm_path):
            raise FileNotFoundError(f"Mock CRM database not found at {self.crm_path}")

        with open(self.crm_path, "r", encoding="utf-8") as f:
            crm_records: Dict[str, Dict[str, Any]] = json.load(f)

        if client_id in crm_records:
            return crm_records[client_id]
        
        # Fallback default CRM record if client not in CRM
        return {
            "client_id": client_id,
            "kyc_status": "pending_update",
            "relationship_manager": "Unassigned General Desk",
            "tier": "Standard Advisory",
            "risk_tolerance_score": 50,
            "notes": "No CRM relationship notes on file. General profile applied.",
            "life_events": []
        }
