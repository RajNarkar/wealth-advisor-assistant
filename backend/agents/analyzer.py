from typing import Dict, Any, List
from backend.models.agent_state import AgentState
from backend.tools.anomaly_tool import AnomalyTool
from backend.logger import get_logger

logger = get_logger("AnalyzerAgent")

class AnalyzerAgent:
    """Specialized agent performing portfolio risk auditing, metric synthesis, and anomaly identification."""

    def __init__(self, anomaly_tool: AnomalyTool = None):
        self.anomaly_tool = anomaly_tool or AnomalyTool()

    def run(self, state: AgentState) -> Dict[str, Any]:
        logs = list(state.get("logs", []))
        errors = list(state.get("errors", []))
        client_data = state.get("client_data", {})
        market_data = state.get("market_data", {})

        logs.append("[AnalyzerAgent] Commencing quantitative analysis and anomaly detection...")
        logger.info(f"Analyzing client {client_data.get('client_id')}")

        if not client_data:
            err_msg = "Cannot analyze empty client data."
            errors.append(err_msg)
            logs.append(f"[AnalyzerAgent] ERROR: {err_msg}")
            return {
                "anomalies": [],
                "analysis_report": {},
                "logs": logs,
                "errors": errors,
                "status": "ERROR"
            }

        portfolio = client_data.get("portfolio", {})
        assets = portfolio.get("assets", [])
        total_val = portfolio.get("total_value", 0.0)
        risk_profile = client_data.get("risk_profile", "moderate")

        # 1. Asset Breakdown Aggregation
        allocation_by_type: Dict[str, float] = {}
        for a in assets:
            atype = a.get("type", "other")
            val = a.get("value", 0.0)
            allocation_by_type[atype] = allocation_by_type.get(atype, 0.0) + val

        allocation_pct: Dict[str, float] = {}
        if total_val > 0:
            for k, v in allocation_by_type.items():
                allocation_pct[k] = round((v / total_val) * 100, 2)

        # 2. Run Anomaly Detection Tool
        anomaly_res = self.anomaly_tool.safe_run(client_data=client_data, market_data=market_data)
        detected_anomalies: List[Dict[str, Any]] = []
        if anomaly_res["success"]:
            anomaly_payload = anomaly_res["data"]
            detected_anomalies = anomaly_payload.get("anomalies", [])
            logs.append(f"[AnalyzerAgent] Detected {len(detected_anomalies)} anomaly signal(s) ({anomaly_payload.get('high_severity_count', 0)} High Severity).")
        else:
            errors.append(f"Anomaly tool error: {anomaly_res['error']}")
            logs.append(f"[AnalyzerAgent] WARNING: Anomaly detection tool encountered an exception.")

        # 3. Calculate Risk Score (0 = extremely conservative/safe, 100 = critical exposure)
        base_score = 40
        if risk_profile == "aggressive":
            base_score = 65
        elif risk_profile == "conservative":
            base_score = 25

        # Penalize for anomalies and concentration
        risk_score = base_score + (len(detected_anomalies) * 10)
        for anom in detected_anomalies:
            if anom.get("severity") == "HIGH":
                risk_score += 15
        risk_score = min(max(risk_score, 10), 98)

        # 4. Construct Structured Analysis Report
        analysis_report = {
            "client_id": client_data.get("client_id"),
            "total_portfolio_value": total_val,
            "risk_score": risk_score,
            "risk_tier": "CRITICAL" if risk_score > 75 else "ELEVATED" if risk_score > 50 else "MODERATE" if risk_score > 30 else "STABLE",
            "asset_allocation_pct": allocation_pct,
            "total_anomalies": len(detected_anomalies),
            "anomalies": detected_anomalies,
            "requires_human_review": len(detected_anomalies) > 0 or risk_score >= 60
        }

        logs.append(f"[AnalyzerAgent] Financial analysis finalized. Risk Score: {risk_score}/100 ({analysis_report['risk_tier']}).")

        return {
            "anomalies": detected_anomalies,
            "analysis_report": analysis_report,
            "logs": logs,
            "errors": errors,
            "status": "ANALYZED"
        }

def analyzer_node(state: AgentState) -> Dict[str, Any]:
    agent = AnalyzerAgent()
    return agent.run(state)
