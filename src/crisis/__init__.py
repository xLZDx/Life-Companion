"""Crisis detection - the most safety-critical module in the product."""

from src.crisis.detector import is_crisis
from src.crisis.hotlines import HotlineEntry, get_hotlines

__all__ = ["HotlineEntry", "get_hotlines", "is_crisis"]
