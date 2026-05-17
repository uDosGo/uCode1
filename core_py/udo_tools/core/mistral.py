"""
Mistral Prompt Engineering Module
Handles system prompts, context windows, and temperature settings.
"""

import json
from pathlib import Path
from typing import Dict, Any


# Default configuration
DEFAULT_CONFIG = {
    "system_prompt": "You are a helpful assistant for uDosConnect.",
    "context_window": 4096,
    "temperature": 0.7,
    "max_tokens": 2048,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}


class MistralConfig:
    """Manage Mistral prompt configurations."""
    
    def __init__(self, config_path: Path = None):
        if config_path is None:
            config_path = Path.home() / ".udos" / "mistral_config.json"
        self.config_path = config_path
        self.config = DEFAULT_CONFIG.copy()
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                self.config.update(json.loads(self.config_path.read_text()))
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_config(self):
        """Save configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(json.dumps(self.config, indent=2))
    
    def edit_prompt(self, **kwargs):
        """Edit Mistral prompt settings."""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
        self._save_config()
        return {"status": "success", "changes": kwargs}
    
    def get_config(self):
        """Get current configuration."""
        return self.config.copy()
    
    def reset_config(self):
        """Reset configuration to defaults."""
        self.config = DEFAULT_CONFIG.copy()
        self._save_config()
        return {"status": "success", "config": self.config}


# Global Mistral configuration instance
mistral_config = MistralConfig()


def edit_mistral_prompt(**kwargs):
    """Edit Mistral prompt settings."""
    return mistral_config.edit_prompt(**kwargs)


def get_mistral_config():
    """Get current Mistral configuration."""
    return mistral_config.get_config()


def reset_mistral_config():
    """Reset Mistral configuration to defaults."""
    return mistral_config.reset_config()
