"""
Fallback Chain for uDOS
Ensures reliability by trying multiple models when one fails
"""

import time
from typing import Callable, Dict, List, Optional, Any
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FallbackChain:
    """Manages fallback logic for model calls"""
    
    def __init__(self):
        # Define fallback chains for different intents
        self.chains: Dict[str, List[str]] = {
            "code_gen": ["deepseek", "vibe", "mistral"],
            "debug": ["deepseek", "vibe", "mistral"],
            "refactor": ["deepseek", "vibe", "mistral"],
            "code_complete": ["deepseek", "vibe"],
            "code_analysis": ["deepseek", "vibe", "mistral"],
            "general": ["mistral", "vibe"],
            "creative": ["vibe", "mistral"],
            "math": ["deepseek", "mistral", "vibe"]
        }
        
        # Store model functions
        self.models: Dict[str, Callable] = {}
        
        # Statistics
        self.stats: Dict[str, Dict[str, int]] = {}
        self._reset_stats()
    
    def register_model(self, name: str, model_fn: Callable):
        """Register a model function"""
        self.models[name] = model_fn
        if name not in self.stats:
            self.stats[name] = {"success": 0, "fail": 0, "latency": []}
    
    def _reset_stats(self):
        """Reset statistics"""
        self.stats = {
            name: {"success": 0, "fail": 0, "latency": []}
            for name in ["deepseek", "vibe", "mistral"]
        }
    
    def execute(self, intent: str, query: str, context: Dict[str, Any] = None, 
                max_retries: int = 3, timeout: float = 10.0) -> Any:
        """Execute with fallback chain"""
        if context is None:
            context = {}
        
        chain = self.chains.get(intent, ["mistral"])
        last_error = None
        
        for attempt in range(max_retries):
            for model_name in chain:
                if model_name not in self.models:
                    logger.warning(f"Model {model_name} not registered")
                    continue
                
                start_time = time.time()
                try:
                    result = self.models[model_name](query, context)
                    
                    # Validate result
                    if self._validate_result(result, intent):
                        latency = time.time() - start_time
                        self.stats[model_name]["success"] += 1
                        self.stats[model_name]["latency"].append(latency)
                        logger.info(f"✅ {model_name} succeeded in {latency:.2f}s")
                        return result
                    else:
                        raise ValueError("Invalid result format")
                        
                except Exception as e:
                    latency = time.time() - start_time
                    self.stats[model_name]["fail"] += 1
                    self.stats[model_name]["latency"].append(latency)
                    last_error = e
                    logger.warning(f"❌ {model_name} failed: {str(e)} ({latency:.2f}s)")
                    
                    # Exponential backoff
                    if attempt < max_retries - 1:
                        time.sleep(min(2 ** attempt, 5))
        
        logger.error(f"All models failed for intent '{intent}': {str(last_error)}")
        raise RuntimeError(f"All models failed after {max_retries} retries")
    
    def _validate_result(self, result: Any, intent: str) -> bool:
        """Validate model output based on intent"""
        if result is None:
            return False
        
        # Basic validation
        if isinstance(result, str):
            return len(result) > 10  # Minimum length
        elif isinstance(result, dict):
            return bool(result)  # Non-empty dict
        elif isinstance(result, list):
            return len(result) > 0  # Non-empty list
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for all models"""
        return {
            model: {
                "success": stats["success"],
                "fail": stats["fail"],
                "success_rate": stats["success"] / (stats["success"] + stats["fail"]) 
                              if (stats["success"] + stats["fail"]) > 0 else 0,
                "avg_latency": sum(stats["latency"]) / len(stats["latency"]) 
                             if stats["latency"] else 0
            }
            for model, stats in self.stats.items()
        }
    
    def log_fallback(self, intent: str, from_model: str, to_model: str, reason: str):
        """Log fallback event"""
        logger.info(f"🔄 Fallback: {intent} from {from_model} to {to_model} ({reason})")


# Global fallback chain instance
fallback_chain = FallbackChain()
