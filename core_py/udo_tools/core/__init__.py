"""
Core DevOnly Actions for uDosConnect
"""

from .cache import CodePatternCache
from .fallback import FallbackChain
from .intent_classifier import IntentClassifier


# Global instances
pattern_cache = CodePatternCache()
fallback_chain = FallbackChain()
intent_classifier = IntentClassifier()


def execute_dev_action(tool, args):
    """Execute DevOnly MCP actions."""
    from .mistral import edit_mistral_prompt, get_mistral_config, reset_mistral_config
    
    dev_actions = {
        "mistral-prompt-edit": edit_mistral_prompt,
        "mistral-prompt-get": get_mistral_config,
        "mistral-prompt-reset": reset_mistral_config,
        "cache-stats": lambda: pattern_cache.get_stats(),
        "fallback-stats": lambda: fallback_chain.get_stats(),
        "classify-intent": lambda q: intent_classifier.classify(q["query"])
    }
    
    if tool not in dev_actions:
        raise ValueError(f"Unknown DevOnly tool: {tool}")
    
    return dev_actions[tool](**args)


def route_query(query: str, context: dict = None) -> str:
    """Route query to appropriate model with full pipeline"""
    if context is None:
        context = {}
    
    # Step 1: Check cache
    intent, _ = intent_classifier.classify(query)
    cached = pattern_cache.get(intent, context.get("language", "python"), query)
    if cached:
        return cached
    
    # Step 2: Execute with fallback
    try:
        result = fallback_chain.execute(intent, query, context)
        
        # Step 3: Cache successful results
        if intent in ["code_gen", "debug", "refactor"]:
            pattern_cache.add(intent, context.get("language", "python"), result, query)
        
        return result
    except Exception as e:
        # Final fallback to Mistral
        from .mistral import get_mistral_config
        config = get_mistral_config()
        return f"All models failed. Error: {str(e)}"

# Add rate limiter
from .rate_limiter import RateLimiter

# Global rate limiter instance
rate_limiter = RateLimiter()

# Add rate limit actions
dev_actions["rate-limit-adjust"] = rate_limiter.adjust_limit
dev_actions["rate-limit-get"] = rate_limiter.get_limits
dev_actions["rate-limit-reset"] = rate_limiter.reset_limits
