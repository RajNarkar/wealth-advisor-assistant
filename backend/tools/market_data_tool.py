import json
import os
from typing import Dict, Any, List, Optional
from backend.tools.base_tool import BaseTool

MARKET_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mock_data", "market_data.json")

class MarketDataTool(BaseTool):
    name: str = "MarketDataTool"
    description: str = "Retrieves live benchmarks, macro rates, sector movements, and asset quotes."

    def __init__(self, market_path: Optional[str] = None):
        self.market_path = market_path or MARKET_PATH

    def run(self, tickers: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        if not os.path.exists(self.market_path):
            raise FileNotFoundError(f"Mock Market data store not found at {self.market_path}")

        with open(self.market_path, "r", encoding="utf-8") as f:
            market_db: Dict[str, Any] = json.load(f)

        benchmarks = market_db.get("benchmarks", {})
        macro = market_db.get("macro_indicators", {})
        quotes = market_db.get("asset_quotes", {})

        filtered_quotes = {}
        if tickers:
            for t in tickers:
                if t in quotes:
                    filtered_quotes[t] = quotes[t]
        else:
            filtered_quotes = quotes

        return {
            "benchmarks": benchmarks,
            "macro_indicators": macro,
            "quotes": filtered_quotes
        }
