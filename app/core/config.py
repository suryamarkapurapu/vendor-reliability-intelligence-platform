"""
Core configuration module re-export.
"""

from app.config import Settings, get_settings, settings

__all__ = ["Settings", "get_settings", "settings"]
