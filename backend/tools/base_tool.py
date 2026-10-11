from abc import ABC, abstractmethod
from typing import Any, Dict
from backend.logger import get_logger

logger = get_logger("BaseTool")

class BaseTool(ABC):
    name: str = "BaseTool"
    description: str = "Abstract base class for all system tools."

    @abstractmethod
    def run(self, **kwargs) -> Dict[str, Any]:
        """Execute the core logic of the tool."""
        pass

    def safe_run(self, **kwargs) -> Dict[str, Any]:
        """Safe wrapper executing tool with exception capture and logging."""
        try:
            logger.info(f"Executing tool [{self.name}] with args: {list(kwargs.keys())}")
            result = self.run(**kwargs)
            return {
                "success": True,
                "tool_name": self.name,
                "data": result,
                "error": None
            }
        except Exception as e:
            logger.error(f"Error in tool [{self.name}]: {str(e)}")
            return {
                "success": False,
                "tool_name": self.name,
                "data": None,
                "error": str(e)
            }
