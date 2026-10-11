from typing import TypedDict, Optional, List, Dict, Any

class AgentState(TypedDict):
    client_id: str
    session_id: str
    client_data: Dict[str, Any]
    crm_data: Dict[str, Any]
    market_data: Dict[str, Any]
    anomalies: List[Dict[str, Any]]
    analysis_report: Dict[str, Any]
    advisory_output: str
    human_approved: Optional[bool]
    human_override_note: str
    errors: List[str]
    logs: List[str]
    memory_context: str
    status: str
