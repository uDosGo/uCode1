import click


def confirm_action(prompt):
    """Ask for confirmation before dangerous actions."""
    return click.confirm(f"⚠️ {prompt} Continue?")


def validate_password(input_password, stored_hash):
    """Validate dev mode password (if set)."""
    import hashlib
    return hashlib.sha256(input_password.encode()).hexdigest() == stored_hash
