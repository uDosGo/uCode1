import os
import json
from pathlib import Path


DEV_MODE_FILE = Path.home() / ".udos" / "dev_mode"


def enable_dev_mode(password=None):
    """Enable Dev Mode and persist state."""
    config = {"enabled": True}
    if password:
        config["password"] = _hash_password(password)

    DEV_MODE_FILE.parent.mkdir(exist_ok=True, parents=True)
    DEV_MODE_FILE.write_text(json.dumps(config))
    os.environ["UDOS_DEV_MODE"] = "1"


def disable_dev_mode():
    """Disable Dev Mode and clean up."""
    DEV_MODE_FILE.unlink(missing_ok=True)
    os.environ.pop("UDOS_DEV_MODE", None)


def check_dev_mode():
    """Check if Dev Mode is active."""
    return DEV_MODE_FILE.exists() and json.loads(DEV_MODE_FILE.read_text())["enabled"]


def get_dev_config():
    """Get full Dev Mode config (for status)."""
    return json.loads(DEV_MODE_FILE.read_text()) if check_dev_mode() else {}


def _hash_password(password):
    """Hash password for storage (simplified)."""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()
