"""
AWS MCP Server implementation.

This module implements the main MCP server that handles communication between
AI assistants and AWS services.
"""

import json
import logging

from mcp.server.fastmcp import FastMCP

from aws_mcp.utils import get_default_region

logger = logging.getLogger(__name__)


class AWSSMCPServer:
    """
    AWS Model Context Protocol Server.

    This server provides a bridge between AI assistants and AWS services,
    allowing natural language interactions with cloud infrastructure.
    """

    def __init__(self) -> None:
        """
        Initialize the AWS MCP Server.
        """
        self.region = get_default_region()
        self.mcp_server: FastMCP = FastMCP("aws-mcp")
        self._register_tools()

    def _register_tools(self) -> None:
        """Set up MCP protocol handlers."""

        @self.mcp_server.tool(
            name="list_ec2_instances",
            description="List EC2 instances in the current region",
        )
        async def list_ec2_instances(state: str = "all") -> str:
            return await self._list_ec2_instances(state)

        @self.mcp_server.tool(
            name="describe_ec2_instance",
            description="Get detailed information about a specific EC2 instance",
        )
        async def describe_ec2_instance(instance_id: str) -> str:
            return await self._describe_ec2_instance(instance_id)


    async def start(self) -> None:
        """Start the MCP server using http transport."""
        await self.mcp_server.run_streamable_http_async()

    async def stop(self) -> None:
        """Stop the MCP server."""
        logger.info("Stopping AWS MCP Server...")
        # The server will stop when the stdio streams are closed


async def run() -> None:
    """
    Run the MCP server using stdio transport.

    This is the main entry point for the MCP server.
    """
    server = AWSSMCPServer()
    await server.start()
