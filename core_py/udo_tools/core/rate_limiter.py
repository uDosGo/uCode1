"""
Rate Limiter Module
"""

class RateLimiter:
    """Manage rate limits for DevOnly actions"""
    
    def __init__(self):
        self.limits = {
            "mistral": 5000,
            "vibe": 1000,
            "deepseek": 2000
        }
    
    def adjust_limit(self, tool, limit, window):
        """Adjust rate limit for a tool"""
        if tool not in self.limits:
            raise ValueError(f"Unknown tool: {tool}")
        
        self.limits[tool] = limit
        return {"status": "success", "new_limit": limit, "window": window}
    
    def get_limits(self):
        """Get all rate limits"""
        return {"status": "success", "limits": self.limits}
    
    def reset_limits(self):
        """Reset to default limits"""
        self.limits = {
            "mistral": 5000,
            "vibe": 1000,
            "deepseek": 2000
        }
        return {"status": "success", "limits": self.limits}
