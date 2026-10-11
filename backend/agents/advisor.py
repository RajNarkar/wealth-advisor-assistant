from typing import Dict, Any
from backend.models.agent_state import AgentState
from backend.tools.gemini_tool import GeminiTool
from backend.memory.long_term import long_term_memory
from backend.logger import get_logger

logger = get_logger("AdvisorAgent")

SYSTEM_INSTRUCTION = (
    "You are an Elite AI Wealth Advisor Assistant providing institutional-grade financial guidance. "
    "Synthesize the client's financial status, portfolio allocation, recent transactions, CRM relationship context, "
    "and identified anomaly signals. "
    "Output must be structured, professional, and actionable, containing: "
    "1. Executive Financial Summary "
    "2. Anomaly & Risk Breakdown "
    "3. Strategic Rebalancing & Action Recommendations (with timeline) "
    "4. Relationship Manager Next Steps."
)

class AdvisorAgent:
    """Specialized agent leveraging Gemini LLM to generate narrative advisory reports."""

    def __init__(self, gemini_tool: GeminiTool = None):
        self.gemini_tool = gemini_tool or GeminiTool()

    def run(self, state: AgentState) -> Dict[str, Any]:
        logs = list(state.get("logs", []))
        errors = list(state.get("errors", []))
        client_data = state.get("client_data", {})
        crm_data = state.get("crm_data", {})
        market_data = state.get("market_data", {})
        analysis_report = state.get("analysis_report", {})
        anomalies = state.get("anomalies", [])
        memory_ctx = state.get("memory_context", "")
        human_note = state.get("human_override_note", "")

        logs.append("[AdvisorAgent] Formulating institutional advisory recommendations via Gemini LLM...")
        logger.info(f"Synthesizing advisory for client {client_data.get('client_id')}")

        # Construct Prompt
        prompt = f"""
CLIENT PROFILE:
- ID: {client_data.get('client_id')}
- Name: {client_data.get('name')}
- Age: {client_data.get('age')}
- Declared Risk Appetite: {client_data.get('risk_profile')}
- Annual Income: ${client_data.get('annual_income', 0):,.2f}
- Financial Goals: {', '.join(client_data.get('goals', []))}

PORTFOLIO & ASSET ALLOCATION:
- Total Portfolio Value: ${client_data.get('portfolio', {}).get('total_value', 0):,.2f}
- Allocation Percentage: {analysis_report.get('asset_allocation_pct', {})}
- Holdings: {[a.get('ticker') + ' (' + a.get('type') + '): $' + f"{a.get('value'):,.0f}" for a in client_data.get('portfolio', {}).get('assets', [])]}

CRM & RELATIONSHIP CONTEXT:
- KYC Status: {crm_data.get('kyc_status')}
- Relationship Manager: {crm_data.get('relationship_manager')}
- Client Tier: {crm_data.get('tier')}
- Relationship Notes: {crm_data.get('notes')}
- Life Events: {crm_data.get('life_events')}

QUANTITATIVE AUDIT & ANOMALIES DETECTED:
- Risk Score: {analysis_report.get('risk_score')}/100 ({analysis_report.get('risk_tier')})
- Anomalies Count: {len(anomalies)}
- Detected Anomalies: {anomalies}

HISTORICAL MEMORY CONTEXT:
{memory_ctx}

HUMAN WEALTH ADVISOR OVERRIDE / DIRECTIVE:
{human_note if human_note else "No manual override applied. Approved as analyzed."}

Please produce a comprehensive, structured advisory report.
"""

        gemini_res = self.gemini_tool.safe_run(
            prompt=prompt,
            system_instruction=SYSTEM_INSTRUCTION
        )

        advisory_text = ""
        if gemini_res["success"]:
            advisory_text = gemini_res["data"].get("text", "")
            mode = gemini_res["data"].get("mode", "live")
            logs.append(f"[AdvisorAgent] Advisory synthesis completed (Mode: {mode}).")
        else:
            errors.append(f"Gemini advisory synthesis error: {gemini_res['error']}")
            logs.append("[AdvisorAgent] ERROR: Gemini tool failure. Applying emergency fallback advisory.")
            advisory_text = "Advisory report could not be fully generated due to external service limitation."

        # Persist session to Long-Term Memory
        client_id = client_data.get("client_id", "UNKNOWN")
        session_id = state.get("session_id", "UNKNOWN")
        long_term_memory.record_session(
            client_id=client_id,
            session_id=session_id,
            analysis_report=analysis_report,
            advisory_summary=advisory_text
        )
        logs.append(f"[AdvisorAgent] Saved consultation outcome to long-term memory for client {client_id}.")

        return {
            "advisory_output": advisory_text,
            "logs": logs,
            "errors": errors,
            "status": "COMPLETED"
        }

def advisor_node(state: AgentState) -> Dict[str, Any]:
    agent = AdvisorAgent()
    return agent.run(state)
