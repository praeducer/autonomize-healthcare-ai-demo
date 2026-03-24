"""Environment configuration."""

import os


def get_auto_approve_threshold() -> float:
    """Get confidence threshold for auto-approval."""
    return float(os.environ.get("PA_AUTO_APPROVE_THRESHOLD", "0.85"))
