import uuid
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from backend.models.agent_state import AgentState
from backend.agents.data_fetcher import data_fetcher_node
from backend.agents.analyzer import analyzer_node
from backend.agents.human_checkpoint import human_checkpoint_node
from backend.agents.advisor import advisor_node
from backend.memory.short_term import short_term_memory
from backend.logger import get_logger

logger = get_logger("Orchestrator")

# Conditional Edge Route Evaluators
def route_after_data_fetch(state: AgentState) -> Literal["analyzer", "__end__"]:
    if state.get("status") == "ERROR" or len(state.get("errors", [])) > 0 and not state.get("client_data"):
        return END
    return "analyzer"

def route_after_analysis(state: AgentState) -> Literal["checkpoint", "__end__"]:
    if state.get("status") == "ERROR":
        return END
    return "checkpoint"

def route_after_checkpoint(state: AgentState) -> Literal["advisor", "__end__"]:
    status = state.get("status")
    if status == "APPROVED":
        return "advisor"
    elif status == "REJECTED":
        return END
    elif status == "AWAITING_APPROVAL":
        # Interrupt / Pause point
        return END
    return END

def build_agent_graph():
    """Builds and compiles the LangGraph StateGraph for Wealth Advisor workflow."""
    workflow = StateGraph(AgentState)

    # Register Nodes
    workflow.add_node("data_fetcher", data_fetcher_node)
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("checkpoint", human_checkpoint_node)
    workflow.add_node("advisor", advisor_node)

    # Define Graph Edges
    workflow.add_edge(START, "data_fetcher")
    workflow.add_conditional_edges("data_fetcher", route_after_data_fetch, {
        "analyzer": "analyzer",
        END: END
    })
    workflow.add_conditional_edges("analyzer", route_after_analysis, {
        "checkpoint": "checkpoint",
        END: END
    })
    workflow.add_conditional_edges("checkpoint", route_after_checkpoint, {
        "advisor": "advisor",
        END: END
    })
    workflow.add_edge("advisor", END)

    # In-memory checkpointer for state persistence
    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)
    return app

# Singleton compiled graph
agent_graph = build_agent_graph()

class Orchestrator:
    """Central orchestrator driving the execution flow, state transitions, and checkpoint resumption."""

    @staticmethod
    def run_pipeline(client_id: str, session_id: str = None) -> Dict[str, Any]:
        session_id = session_id or f"sess_{uuid.uuid4().hex[:8]}"
        initial_state: AgentState = {
            "client_id": client_id,
            "session_id": session_id,
            "client_data": {},
            "crm_data": {},
            "market_data": {},
            "anomalies": [],
            "analysis_report": {},
            "advisory_output": "",
            "human_approved": None,
            "human_override_note": "",
            "errors": [],
            "logs": [f"[Orchestrator] Starting session {session_id} for client {client_id}"],
            "memory_context": "",
            "status": "INITIALIZED"
        }

        short_term_memory.init_session(session_id, client_id, initial_state)
        config = {"configurable": {"thread_id": session_id}}

        logger.info(f"Invoking agent graph for session {session_id}")
        output_state = agent_graph.invoke(initial_state, config=config)

        # Sync short term memory
        short_term_memory.update_session(session_id, {
            "status": output_state.get("status"),
            "human_approved": output_state.get("human_approved"),
            "state": output_state,
            "logs": output_state.get("logs", []),
            "errors": output_state.get("errors", [])
        })

        return output_state

    @staticmethod
    def resume_pipeline(session_id: str, approved: bool, note: str = "") -> Dict[str, Any]:
        session_record = short_term_memory.get_session(session_id)
        if not session_record:
            raise KeyError(f"Session '{session_id}' not found.")

        current_state: AgentState = session_record.get("state", {})
        current_state["human_approved"] = approved
        current_state["human_override_note"] = note

        short_term_memory.set_checkpoint_decision(session_id, approved, note)

        if not approved:
            current_state["status"] = "REJECTED"
            current_state["advisory_output"] = f"Advisory generation suspended: Rejected by Wealth Advisor. Note: {note}"
            current_state["logs"].append(f"[Orchestrator] Pipeline ended with REJECTED status by Human Advisor.")
            short_term_memory.update_session(session_id, {
                "status": "REJECTED",
                "state": current_state,
                "logs": current_state.get("logs", [])
            })
            return current_state

        # If approved, run human_checkpoint then advisor
        config = {"configurable": {"thread_id": session_id}}
        current_state["status"] = "APPROVED"

        # Resume through graph or direct node transition
        advisor_res = advisor_node(current_state)
        current_state.update(advisor_res)
        current_state["status"] = "COMPLETED"

        short_term_memory.update_session(session_id, {
            "status": "COMPLETED",
            "state": current_state,
            "logs": current_state.get("logs", []),
            "errors": current_state.get("errors", [])
        })

        return current_state

orchestrator = Orchestrator()
