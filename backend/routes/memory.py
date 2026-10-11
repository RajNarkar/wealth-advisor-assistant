from fastapi import APIRouter
from typing import Dict, Any
from backend.memory.long_term import long_term_memory
from backend.memory.short_term import short_term_memory

router = APIRouter(prefix="/api/memory", tags=["Memory Layer"])

@router.get("/{client_id}", response_model=Dict[str, Any])
def get_client_long_term_memory(client_id: str):
    """Retrieve long-term historical advisory consultation summaries for a client."""
    return long_term_memory.get_history(client_id)

@router.get("/sessions/active", response_model=Dict[str, Any])
def get_active_sessions_memory():
    """Retrieve short-term session state snapshots."""
    return short_term_memory.list_active_sessions()
