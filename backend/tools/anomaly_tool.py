import math
import statistics
from typing import Dict, Any, List
from backend.tools.base_tool import BaseTool

class AnomalyTool(BaseTool):
    name: str = "AnomalyTool"
    description: str = "Performs statistical anomaly detection and risk signal identification on client transactions and asset allocations."

    def run(self, client_data: Dict[str, Any], market_data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        anomalies: List[Dict[str, Any]] = []

        portfolio = client_data.get("portfolio", {})
        assets = portfolio.get("assets", [])
        total_val = portfolio.get("total_value", 0.0)
        risk_profile = client_data.get("risk_profile", "moderate").lower()
        transactions = client_data.get("transactions", [])

        # 1. Transaction Outlier Detection (Z-Score & Multiplier)
        if transactions:
            amounts = [t.get("amount", 0.0) for t in transactions]
            if len(amounts) >= 2:
                mean_amt = statistics.mean(amounts)
                stdev_amt = statistics.stdev(amounts) if len(amounts) > 1 else 0.0

                for t in transactions:
                    amt = t.get("amount", 0.0)
                    z_score = (amt - mean_amt) / stdev_amt if stdev_amt > 0 else 0.0

                    if z_score >= 2.0 or (amt >= mean_amt * 2.5 and amt > 25000):
                        anomalies.append({
                            "type": "TRANSACTION_SPIKE",
                            "severity": "HIGH" if z_score >= 2.5 else "MEDIUM",
                            "item_id": t.get("txn_id"),
                            "description": f"Unusual {t.get('type').upper()} volume for {t.get('ticker')} of ${amt:,.2f} (Z-Score: {z_score:.2f}, baseline avg: ${mean_amt:,.2f}).",
                            "suggested_action": "Verify source of funds and confirm client intent for large capital movement."
                        })
            elif len(amounts) == 1 and amounts[0] > 100000:
                anomalies.append({
                    "type": "LARGE_ISOLATED_TRANSACTION",
                    "severity": "MEDIUM",
                    "item_id": transactions[0].get("txn_id"),
                    "description": f"Single large transaction of ${amounts[0]:,.2f} exceeds standard advisory threshold.",
                    "suggested_action": "Review client KYC and liquidity schedule."
                })

        # 2. Portfolio Concentration Risk
        concentration_threshold = 0.35 if risk_profile == "aggressive" else 0.25
        for asset in assets:
            weight = asset.get("weight", 0.0)
            if weight >= concentration_threshold:
                anomalies.append({
                    "type": "ASSET_CONCENTRATION_RISK",
                    "severity": "HIGH" if weight >= 0.40 else "MEDIUM",
                    "item_id": asset.get("ticker"),
                    "description": f"Ticker {asset.get('ticker')} ({asset.get('type')}) accounts for {weight*100:.1f}% of total portfolio, exceeding {concentration_threshold*100:.0f}% safety threshold.",
                    "suggested_action": f"Recommend strategic rebalancing to reduce idiosyncratic risk in {asset.get('ticker')}."
                })

        # 3. Risk Profile Allocation Mismatch
        equity_crypto_weight = sum(a.get("weight", 0.0) for a in assets if a.get("type") in ["equity", "crypto"])
        cash_weight = sum(a.get("weight", 0.0) for a in assets if a.get("type") == "cash")
        crypto_weight = sum(a.get("weight", 0.0) for a in assets if a.get("type") == "crypto")

        if risk_profile == "conservative" and equity_crypto_weight > 0.20:
            anomalies.append({
                "type": "RISK_PROFILE_MISMATCH",
                "severity": "HIGH",
                "item_id": "ALLOCATION",
                "description": f"Conservative client holds {equity_crypto_weight*100:.1f}% in volatile assets (target < 20%).",
                "suggested_action": "Reallocate excess equity/crypto towards high-grade fixed income instruments (e.g. UST10Y)."
            })

        if risk_profile == "conservative" and crypto_weight > 0.0:
            anomalies.append({
                "type": "PROHIBITED_SPECULATIVE_ASSET",
                "severity": "HIGH",
                "item_id": "CRYPTO",
                "description": "Cryptocurrency detected in a Conservative profile portfolio.",
                "suggested_action": "Advise client on immediate liquidation of speculative crypto positions."
            })

        if risk_profile == "aggressive" and cash_weight > 0.35:
            anomalies.append({
                "type": "CASH_DRAG_RISK",
                "severity": "LOW",
                "item_id": "CASH",
                "description": f"Aggressive client holds {cash_weight*100:.1f}% in idle cash, causing real purchasing power drag.",
                "suggested_action": "Deploy idle cash into broad market index ETFs or growth equities."
            })

        # 4. Rapid Liquidation / Capital Flight Check
        recent_sells = [t.get("amount", 0.0) for t in transactions if t.get("type") == "sell"]
        total_recent_sell = sum(recent_sells)
        if total_val > 0 and (total_recent_sell / total_val) >= 0.20:
            anomalies.append({
                "type": "RAPID_LIQUIDATION_SIGNAL",
                "severity": "HIGH",
                "item_id": "SELL_PRESSURE",
                "description": f"Recent sell orders total ${total_recent_sell:,.2f} ({total_recent_sell/total_val*100:.1f}% of total portfolio value).",
                "suggested_action": "Conduct immediate outreach to confirm if client is experiencing unexpected liquidity demands."
            })

        return {
            "total_anomalies": len(anomalies),
            "high_severity_count": sum(1 for a in anomalies if a.get("severity") == "HIGH"),
            "anomalies": anomalies
        }
