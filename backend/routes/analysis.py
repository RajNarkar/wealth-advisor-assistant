import uuid
import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from backend.models.responses import AnalyzeRequest, AnalyzeResponse, SessionStatusResponse
from backend.agents.orchestrator import orchestrator
from backend.memory.short_term import short_term_memory
from backend.logger import get_logger

router = APIRouter(prefix="/api", tags=["Analysis"])
logger = get_logger("AnalysisRoutes")

def _execute_orchestrator_job(client_id: str, session_id: str):
    try:
        orchestrator.run_pipeline(client_id=client_id, session_id=session_id)
    except Exception as e:
        logger.error(f"Error running pipeline for session {session_id}: {e}")
        short_term_memory.add_error(session_id, str(e))
        short_term_memory.update_session(session_id, {"status": "ERROR"})

@router.post("/analyze", response_model=AnalyzeResponse)
def trigger_analysis(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    """Trigger the multi-agent wealth advisory pipeline for a given client."""
    client_id = req.client_id
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    # Initialize short term memory
    short_term_memory.init_session(session_id, client_id)

    # Launch in background task so API responds immediately
    background_tasks.add_task(_execute_orchestrator_job, client_id, session_id)

    return AnalyzeResponse(
        session_id=session_id,
        client_id=client_id,
        message="Multi-agent Wealth Advisory analysis pipeline initiated."
    )

@router.get("/session/{session_id}/status", response_model=SessionStatusResponse)
def get_session_status(session_id: str):
    """Poll pipeline execution logs and status."""
    record = short_term_memory.get_session(session_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")

    state = record.get("state", {})
    return SessionStatusResponse(
        session_id=session_id,
        client_id=record.get("client_id", ""),
        status=record.get("status", "UNKNOWN"),
        human_approved=record.get("human_approved"),
        anomalies=state.get("anomalies", []),
        analysis_report=state.get("analysis_report", {}),
        advisory_output=state.get("advisory_output"),
        errors=record.get("errors", []),
        logs=record.get("logs", [])
    )
