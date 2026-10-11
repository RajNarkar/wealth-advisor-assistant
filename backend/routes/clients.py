from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from backend.tools.client_data_tool import ClientDataTool

router = APIRouter(prefix="/api/clients", tags=["Clients"])
client_tool = ClientDataTool()

@router.get("", response_model=List[Dict[str, Any]])
def list_clients():
    """Retrieve summary directory of all available clients."""
    return client_tool.list_all_clients()

@router.get("/{client_id}", response_model=Dict[str, Any])
def get_client_details(client_id: str):
    """Retrieve full financial profile and transactions for a client."""
    res = client_tool.safe_run(client_id=client_id)
    if not res["success"]:
        raise HTTPException(status_code=404, detail=res["error"])
    return res["data"]
