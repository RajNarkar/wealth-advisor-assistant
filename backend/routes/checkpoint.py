from fastapi import APIRouter, HTTPException, BackgroundTasks
from backend.models.responses import CheckpointDecisionRequest, CheckpointDecisionResponse
from backend.agents.orchestrator import orchestrator
from backend.memory.short_term import short_term_memory
from backend.logger import get_logger

router = APIRouter(prefix="/api/checkpoint", tags=["Human Checkpoint"])
logger = get_logger("CheckpointRoutes")

@router.get("/{session_id}/status")
def get_checkpoint_status(session_id: str):
    """Inspect checkpoint status for a session."""
    record = short_term_memory.get_session(session_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")

    state = record.get("state", {})
    return {
        "session_id": session_id,
        "status": record.get("status"),
        "human_approved": record.get("human_approved"),
        "requires_human_review": state.get("analysis_report", {}).get("requires_human_review", False),
        "anomalies": state.get("anomalies", []),
        "analysis_report": state.get("analysis_report", {})
    }

@router.post("/{session_id}/approve", response_model=CheckpointDecisionResponse)
def approve_checkpoint(session_id: str, req: CheckpointDecisionRequest, background_tasks: BackgroundTasks):
    """Approve checkpoint and resume pipeline to AdvisorAgent."""
    record = short_term_memory.get_session(session_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")

    if record.get("status") not in ["AWAITING_APPROVAL", "RUNNING"]:
        raise HTTPException(status_code=400, detail=f"Session is in '{record.get('status')}' state, not awaiting approval.")

    # Resume pipeline in background
    def _resume():
        orchestrator.resume_pipeline(session_id=session_id, approved=True, note=req.note or "")

    background_tasks.add_task(_resume)

    return CheckpointDecisionResponse(
        session_id=session_id,
        decision="APPROVED",
        message="Checkpoint approved. Advisory synthesis in progress."
    )

@router.post("/{session_id}/reject", response_model=CheckpointDecisionResponse)
def reject_checkpoint(session_id: str, req: CheckpointDecisionRequest):
    """Reject checkpoint with reason, terminating advisory pipeline."""
    record = short_term_memory.get_session(session_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")

    orchestrator.resume_pipeline(session_id=session_id, approved=False, note=req.note or "")

    return CheckpointDecisionResponse(
        session_id=session_id,
        decision="REJECTED",
        message="Checkpoint rejected. Pipeline execution halted."
    )
