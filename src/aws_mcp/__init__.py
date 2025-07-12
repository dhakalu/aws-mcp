"""
AWS MCP Server - A Model Context Protocol server for AWS services.

This package provides a standardized interface for AI assistants to interact
with AWS services through the Model Context Protocol.
"""

__version__ = "0.1.0"
__author__ = "dhakalu"
__email__ = "dhakal.upenn@gmail.com"

from .server import AWSSMCPServer

__all__ = ["AWSSMCPServer"]
