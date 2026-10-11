import json
import os
from typing import Dict, Any, List, Optional
from backend.tools.base_tool import BaseTool
from backend.models.client import ClientData

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mock_data", "clients.json")

class ClientDataTool(BaseTool):
    name: str = "ClientDataTool"
    description: str = "Retrieves and validates client financial profile, assets, portfolio, and transaction history."

    def __init__(self, data_path: Optional[str] = None):
        self.data_path = data_path or DATA_PATH

    def run(self, client_id: str, **kwargs) -> Dict[str, Any]:
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Mock client data store not found at {self.data_path}")

        with open(self.data_path, "r", encoding="utf-8") as f:
            clients: List[Dict[str, Any]] = json.load(f)

        for client in clients:
            if client.get("client_id") == client_id:
                # Validate schema through Pydantic
                validated = ClientData(**client)
                return validated.model_dump()

        raise KeyError(f"Client with ID '{client_id}' not found in financial data repository.")

    def list_all_clients(self) -> List[Dict[str, Any]]:
        """Utility for API to list overview of available clients."""
        if not os.path.exists(self.data_path):
            return []
        with open(self.data_path, "r", encoding="utf-8") as f:
            clients: List[Dict[str, Any]] = json.load(f)
        return [
            {
                "client_id": c.get("client_id"),
                "name": c.get("name"),
                "age": c.get("age"),
                "risk_profile": c.get("risk_profile"),
                "total_portfolio_value": c.get("portfolio", {}).get("total_value", 0)
            }
            for c in clients
        ]
