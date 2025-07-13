"""
AWS MCP Server implementation.

This module implements the main MCP server that handles communication between
AI assistants and AWS services.
"""

import logging

from mcp.server.fastmcp import FastMCP

import aws_mcp.handlers.ec2 as ec2_handlers
from aws_mcp.utils import get_default_region

logger = logging.getLogger(__name__)


region = get_default_region()
mcp_server: FastMCP = FastMCP("aws-mcp")


@mcp_server.tool(
    name="list_ec2_instances",
    description="List EC2 instances in the current region",
)
async def list_ec2_instances(region: str, state: str = "all") -> str:
    return await ec2_handlers.list_ec2_instances(region, state)


@mcp_server.tool(
    name="describe_ec2_instance",
    description="Get detailed information about a specific EC2 instance",
)
async def describe_ec2_instance(region: str, instance_id: str) -> str:
    return await ec2_handlers.describe_ec2_instance(region, instance_id)


async def run() -> None:
    """
    Run the MCP server using streamable HTTP transport.
    This function starts the server and listens for incoming requests.
    """
    await mcp_server.run_streamable_http_async()
