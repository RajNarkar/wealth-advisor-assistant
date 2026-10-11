from typing import Dict, Any
from backend.models.agent_state import AgentState
from backend.logger import get_logger

logger = get_logger("HumanCheckpointNode")

class HumanCheckpointNode:
    """Manages Human-in-the-Loop review checkpoint for high-risk signals or anomaly overrides."""

    def run(self, state: AgentState) -> Dict[str, Any]:
        logs = list(state.get("logs", []))
        report = state.get("analysis_report", {})
        requires_review = report.get("requires_human_review", False)
        current_approval = state.get("human_approved")

        if current_approval is True:
            note = state.get("human_override_note", "")
            logs.append(f"[HumanCheckpoint] Review APPROVED by human wealth advisor. Advisor Note: '{note}'")
            logger.info(f"Session {state.get('session_id')} approved by human.")
            return {
                "logs": logs,
                "status": "APPROVED"
            }
        elif current_approval is False:
            note = state.get("human_override_note", "")
            logs.append(f"[HumanCheckpoint] Review REJECTED by human wealth advisor. Advisor Note: '{note}'")
            logger.warning(f"Session {state.get('session_id')} rejected by human.")
            return {
                "logs": logs,
                "status": "REJECTED"
            }

        # If review is required and decision is still pending:
        if requires_review and current_approval is None:
            logs.append(f"[HumanCheckpoint] Checkpoint triggered: Anomalies or elevated risk require Human Advisor verification.")
            logger.info(f"Session {state.get('session_id')} awaiting human approval.")
            return {
                "logs": logs,
                "status": "AWAITING_APPROVAL"
            }

        # If no review is required:
        logs.append("[HumanCheckpoint] No critical risk factors identified. Auto-approved for advisory synthesis.")
        return {
            "human_approved": True,
            "human_override_note": "System auto-approved (low risk score, zero anomalies).",
            "logs": logs,
            "status": "APPROVED"
        }

def human_checkpoint_node(state: AgentState) -> Dict[str, Any]:
    node = HumanCheckpointNode()
    return node.run(state)
