from typing import Dict, Any
from backend.models.agent_state import AgentState
from backend.tools.client_data_tool import ClientDataTool
from backend.tools.crm_tool import CRMTool
from backend.tools.market_data_tool import MarketDataTool
from backend.memory.long_term import long_term_memory
from backend.logger import get_logger

logger = get_logger("DataFetcherAgent")

class DataFetcherAgent:
    """Specialized agent responsible for retrieving and unifying client financials, CRM context, and market data."""

    def __init__(self, client_tool: ClientDataTool = None, crm_tool: CRMTool = None, market_tool: MarketDataTool = None):
        self.client_tool = client_tool or ClientDataTool()
        self.crm_tool = crm_tool or CRMTool()
        self.market_tool = market_tool or MarketDataTool()

    def run(self, state: AgentState) -> Dict[str, Any]:
        client_id = state.get("client_id")
        logs = list(state.get("logs", []))
        errors = list(state.get("errors", []))

        logs.append(f"[DataFetcherAgent] Initiated data ingestion for Client: {client_id}")
        logger.info(f"Ingesting records for client {client_id}")

        # 1. Fetch Client Profile & Transactions
        client_res = self.client_tool.safe_run(client_id=client_id)
        if not client_res["success"]:
            err_msg = f"Failed to ingest client data: {client_res['error']}"
            errors.append(err_msg)
            logs.append(f"[DataFetcherAgent] ERROR: {err_msg}")
            return {
                "client_data": {},
                "crm_data": {},
                "market_data": {},
                "memory_context": "None",
                "logs": logs,
                "errors": errors,
                "status": "ERROR"
            }
        client_data = client_res["data"]
        logs.append(f"[DataFetcherAgent] Successfully retrieved profile for {client_data.get('name')} (Risk Profile: {client_data.get('risk_profile')})")

        # 2. Extract Portfolio Tickers
        tickers = [a.get("ticker") for a in client_data.get("portfolio", {}).get("assets", []) if a.get("ticker")]

        # 3. Fetch CRM Relationship Context
        crm_res = self.crm_tool.safe_run(client_id=client_id)
        if crm_res["success"]:
            crm_data = crm_res["data"]
            logs.append(f"[DataFetcherAgent] Retrieved CRM context (KYC: {crm_data.get('kyc_status')}, RM: {crm_data.get('relationship_manager')})")
        else:
            crm_data = {"kyc_status": "unverified", "notes": "CRM data fetch failed."}
            logs.append(f"[DataFetcherAgent] WARNING: CRM fetch failed, utilizing fallback profile.")

        # 4. Fetch Market Data & Benchmarks
        market_res = self.market_tool.safe_run(tickers=tickers)
        if market_res["success"]:
            market_data = market_res["data"]
            logs.append(f"[DataFetcherAgent] Retrieved live benchmark data for {len(market_data.get('quotes', {}))} ticker(s).")
        else:
            market_data = {}
            logs.append(f"[DataFetcherAgent] WARNING: Market data fetch failed.")

        # 5. Fetch Long-Term Memory
        memory_ctx = long_term_memory.get_formatted_memory_context(client_id)
        logs.append(f"[DataFetcherAgent] Injected historical session memory context.")

        return {
            "client_data": client_data,
            "crm_data": crm_data,
            "market_data": market_data,
            "memory_context": memory_ctx,
            "logs": logs,
            "errors": errors,
            "status": "DATA_FETCHED"
        }

def data_fetcher_node(state: AgentState) -> Dict[str, Any]:
    agent = DataFetcherAgent()
    return agent.run(state)
