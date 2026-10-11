import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_api_endpoints():
    print("=== TEST API: HEALTH ===")
    r = client.get("/api/health")
    assert r.status_code == 200
    print("Health response:", r.json())

    print("\n=== TEST API: LIST CLIENTS ===")
    r = client.get("/api/clients")
    assert r.status_code == 200
    clients = r.json()
    print(f"Clients found: {len(clients)}")
    assert len(clients) >= 3

    print("\n=== TEST API: GET CLIENT C002 (David Sterling) ===")
    r = client.get("/api/clients/C002")
    assert r.status_code == 200
    c2 = r.json()
    print(f"Client name: {c2['name']}, Risk Profile: {c2['risk_profile']}")

    print("\n=== TEST API: TRIGGER ANALYSIS FOR C002 ===")
    r = client.post("/api/analyze", json={"client_id": "C002"})
    assert r.status_code == 200
    data = r.json()
    session_id = data["session_id"]
    print("Session initiated:", session_id)

    # Wait 1-2 seconds for background orchestrator to process
    time.sleep(2)

    print("\n=== TEST API: POLL SESSION STATUS ===")
    r = client.get(f"/api/session/{session_id}/status")
    assert r.status_code == 200
    status_data = r.json()
    print(f"Status: {status_data['status']}")
    print(f"Anomalies found: {len(status_data['anomalies'])}")
    for a in status_data['anomalies']:
        print(f" - [{a['severity']}] {a['type']}: {a['description']}")

    # If awaiting approval, approve it
    if status_data["status"] == "AWAITING_APPROVAL":
        print("\n=== TEST API: APPROVE CHECKPOINT ===")
        r = client.post(f"/api/checkpoint/{session_id}/approve", json={"note": "Approved high-growth risk."})
        assert r.status_code == 200
        print("Checkpoint response:", r.json())

        # Wait for advisor generation
        time.sleep(2)
        r = client.get(f"/api/session/{session_id}/status")
        final_status = r.json()
        print(f"Final Status: {final_status['status']}")
        assert final_status["status"] == "COMPLETED"
        print("Advisory generated length:", len(final_status.get("advisory_output", "")))

    print("\n=== TEST API: GET CLIENT MEMORY ===")
    r = client.get("/api/memory/C002")
    assert r.status_code == 200
    mem = r.json()
    print(f"Memory sessions recorded: {mem.get('sessions_count')}")

    print("\n=== ALL FASTAPI ROUTE TESTS PASSED! ===")

if __name__ == "__main__":
    test_api_endpoints()
