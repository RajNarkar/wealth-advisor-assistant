from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class AnalyzeRequest(BaseModel):
    client_id: str

class AnalyzeResponse(BaseModel):
    session_id: str
    client_id: str
    message: str

class SessionStatusResponse(BaseModel):
    session_id: str
    client_id: str
    status: str
    human_approved: Optional[bool] = None
    anomalies: List[Dict[str, Any]] = []
    analysis_report: Dict[str, Any] = {}
    advisory_output: Optional[str] = None
    errors: List[str] = []
    logs: List[str] = []

class CheckpointDecisionRequest(BaseModel):
    note: Optional[str] = ""

class CheckpointDecisionResponse(BaseModel):
    session_id: str
    decision: str
    message: str
