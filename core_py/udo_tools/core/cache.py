"""
Code Pattern Cache for uDOS
Optimizes common code generation patterns by caching templates
"""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple
from rapidfuzz import fuzz


class CodePatternCache:
    """Cache for common code patterns to reduce API calls"""
    
    def __init__(self, cache_file: Path = None):
        if cache_file is None:
            cache_file = Path.home() / ".udos" / "pattern_cache.json"
        self.cache_file = cache_file
        self.patterns: Dict[str, Dict[str, str]] = {}
        self.hits = 0
        self.misses = 0
        self._load_cache()
    
    def _load_cache(self):
        """Load cache from file"""
        if self.cache_file.exists():
            try:
                data = json.loads(self.cache_file.read_text())
                self.patterns = data.get("patterns", {})
                self.hits = data.get("hits", 0)
                self.misses = data.get("misses", 0)
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_cache(self):
        """Save cache to file"""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "patterns": self.patterns,
            "hits": self.hits,
            "misses": self.misses
        }
        self.cache_file.write_text(json.dumps(data, indent=2))
    
    def normalize_query(self, query: str) -> str:
        """Normalize query for pattern matching"""
        # Remove common prefixes
        for prefix in ["write ", "create ", "generate ", "make ", "code ", "function "]:
            if query.lower().startswith(prefix):
                query = query[len(prefix):]
                break
        # Remove language specifiers
        for lang in ["python", "javascript", "java", "rust", "go", "c++", "c#"]:
            if f" in {lang}" in query.lower():
                query = query.lower().replace(f" in {lang}", "")
            if f" {lang} " in query.lower():
                query = query.lower().replace(f" {lang} ", " ")
        return query.strip()
    
    def fuzzy_match(self, query: str, pattern: str, threshold: int = 85) -> bool:
        """Fuzzy match query against pattern"""
        return fuzz.token_set_ratio(query.lower(), pattern.lower()) >= threshold
    
    def get(self, intent: str, lang: str, query: str) -> Optional[str]:
        """Get cached pattern if available"""
        normalized = self.normalize_query(query)
        
        # Check exact matches first
        for pattern, variants in self.patterns.items():
            if normalized.lower() == pattern.lower():
                if lang in variants:
                    self.hits += 1
                    self._save_cache()
                    return variants[lang]
                self.misses += 1
                return None
        
        # Check fuzzy matches
        for pattern, variants in self.patterns.items():
            if self.fuzzy_match(normalized, pattern):
                if lang in variants:
                    self.hits += 1
                    self._save_cache()
                    return variants[lang]
                self.misses += 1
                return None
        
        self.misses += 1
        self._save_cache()
        return None
    
    def add(self, intent: str, lang: str, code: str, query: str = None):
        """Add new pattern to cache"""
        pattern = query if query else intent
        normalized = self.normalize_query(pattern)
        
        if normalized not in self.patterns:
            self.patterns[normalized] = {}
        
        self.patterns[normalized][lang] = code
        self._save_cache()
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0,
            "patterns": len(self.patterns)
        }
    
    def clear(self):
        """Clear cache"""
        self.patterns = {}
        self.hits = 0
        self.misses = 0
        self._save_cache()
