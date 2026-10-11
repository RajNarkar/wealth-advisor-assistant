import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.agents.orchestrator import orchestrator
from backend.tools.client_data_tool import ClientDataTool
from backend.memory.long_term import long_term_memory
from backend.memory.short_term import short_term_memory

def test_full_pipeline():
    print("=== TEST 1: LIST CLIENTS ===")
    tool = ClientDataTool()
    clients = tool.list_all_clients()
    print(f"Loaded {len(clients)} clients: {[c['client_id'] for c in clients]}")
    assert len(clients) >= 3, "Expected at least 3 mock clients"

    print("\n=== TEST 2: RUN ORCHESTRATOR FOR CLIENT C001 ===")
    state = orchestrator.run_pipeline("C001", session_id="test_sess_001")
    print(f"Session Status: {state.get('status')}")
    print(f"Anomalies detected: {len(state.get('anomalies', []))}")
    for anom in state.get("anomalies", []):
        print(f" - [{anom.get('severity')}] {anom.get('type')}: {anom.get('description')}")
    print(f"Logs captured: {len(state.get('logs', []))}")

    # Checkpoint review verification
    if state.get("status") == "AWAITING_APPROVAL":
        print("\n=== TEST 3: HUMAN CHECKPOINT APPROVAL ===")
        resumed_state = orchestrator.resume_pipeline(
            "test_sess_001",
            approved=True,
            note="Test Advisor manual approval verified."
        )
        print(f"Resumed Status: {resumed_state.get('status')}")
        print("Advisory Output Preview:")
        print(resumed_state.get("advisory_output")[:300] + "...")
        assert resumed_state.get("status") == "COMPLETED", "Expected status COMPLETED after approval"

    print("\n=== TEST 4: LONG TERM MEMORY ===")
    hist = long_term_memory.get_history("C001")
    print(f"Recorded historical sessions for C001: {hist.get('sessions_count')}")
    assert hist.get("sessions_count", 0) >= 1, "Expected at least 1 session recorded in memory"

    print("\n=== ALL TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    test_full_pipeline()
