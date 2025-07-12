"""
Utility package for AWS MCP Server.

This package contains utility modules for authentication, helpers, and
common functionality used across the MCP server.
"""

from .auth import AWSAuth, get_default_region
from .logging import setup_logging

__all__ = ["setup_logging", "AWSAuth", "get_default_region"]
