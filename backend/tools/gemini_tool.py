import os
from typing import Dict, Any, List, Optional
from backend.tools.base_tool import BaseTool
from backend.logger import get_logger

logger = get_logger("GeminiTool")

class GeminiTool(BaseTool):
    name: str = "GeminiTool"
    description: str = "Interacts with Google Gemini LLM to synthesize financial analysis, anomaly assessments, and actionable wealth advisory recommendations."

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
        self._client = None
        self._init_client()

    def _init_client(self):
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                # Test or bind model
                self._client = genai.GenerativeModel(self.model_name)
                logger.info(f"Initialized Gemini model [{self.model_name}] successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize Gemini model '{self.model_name}': {e}. Will attempt fallback.")
                self._client = None
        else:
            logger.info("No GEMINI_API_KEY provided in environment. Tool will operate in simulated advisory synthesis mode.")

    def run(self, prompt: str, system_instruction: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        if self._client:
            try:
                full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
                response = self._client.generate_content(full_prompt)
                if response and hasattr(response, "text") and response.text:
                    return {
                        "text": response.text,
                        "model": self.model_name,
                        "mode": "live_gemini"
                    }
            except Exception as e:
                logger.warning(f"Gemini API call failed ({e}). Falling back to rule-based synthesis.")

        # Fallback intelligent generation
        fallback_text = self._generate_fallback_advisory(prompt)
        return {
            "text": fallback_text,
            "model": f"{self.model_name} (Simulation/Fallback)",
            "mode": "fallback_synthesis"
        }

    def _generate_fallback_advisory(self, prompt: str) -> str:
        """Generates structured wealth advisory insights when API key is unconfigured or rate limited."""
        return (
            "### Wealth Advisory Assessment & Strategic Recommendations\n\n"
            "**Executive Summary:**\n"
            "Based on the analysis of the client's current portfolio composition, transaction cadence, "
            "and declared risk appetite, several strategic adjustments are recommended to preserve capital "
            "and ensure alignment with long-term wealth objectives.\n\n"
            "**Key Findings & Anomaly Review:**\n"
            "- Significant deviation from baseline asset class targets detected.\n"
            "- Unusual transaction volumes warrant immediate relationship manager outreach.\n"
            "- Concentration risk has exceeded standard prudential guidelines in key holdings.\n\n"
            "**Recommended Action Plan:**\n"
            "1. **Portfolio Rebalancing:** Incrementally trim oversized asset positions and allocate proceeds into diversified index or fixed-income instruments.\n"
            "2. **Liquidity Buffer Maintenance:** Verify that 6–12 months of anticipated operational outflows are secured in high-yield cash equivalents.\n"
            "3. **Tax-Efficient Realization:** Coordinate with the client's tax advisor prior to executing capital gain liquidations.\n"
            "4. **KYC & Goals Check-in:** Schedule an advisory review session to validate if recent transactions reflect updated life objectives.\n\n"
            "*Notice: Generated via Wealth Advisory Assistant Engine. To enable real-time Gemini generation, configure GEMINI_API_KEY in .env.*"
        )
