"""
AWS MCP Server implementation.

This module contains the main MCP server that handles communication between
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

    async def _list_ec2_instances(self, state: str = "all") -> str:
        """List EC2 instances using boto3."""
        try:
            from aws_mcp.handlers.ec2 import EC2Handler

            handler = EC2Handler(self.region)
            result = handler.list_instances(state)

            instances = result["Instances"]
            if not instances:
                return json.dumps(
                    {
                        "Error": False,
                        "Message": f"No EC2 instances found in {self.region} with state '{state}'",
                        "Instances": [],
                        "Count": 0,
                        "Region": self.region,
                        "StateFilter": state,
                    }
                )

            return json.dumps(
                {
                    "Error": False,
                    "Message": f"Found {result['Count']} EC2 instance(s) in {self.region}",
                    "Instances": instances,
                    "Count": result["Count"],
                    "Region": self.region,
                    "StateFilter": state,
                }
            )

        except Exception as e:
            logger.error(f"Error in _list_ec2_instances: {e}")
            return json.dumps(
                {
                    "Error": True,
                    "Message": f"Error listing EC2 instances: {str(e)}",
                    "Instances": [],
                    "Count": 0,
                }
            )

    async def _describe_ec2_instance(self, instance_id: str) -> str:
        """Describe a specific EC2 instance using boto3."""
        try:
            from aws_mcp.handlers.ec2 import EC2Handler

            handler = EC2Handler(self.region)
            result = handler.describe_instance(instance_id)

            return json.dumps(
                {
                    "Error": False,
                    "Message": f"Successfully retrieved details for instance {instance_id}",
                    "Instance": result,
                    "InstanceId": instance_id,
                    "Region": self.region,
                }
            )

        except ValueError as e:
            # Instance not found
            logger.warning(f"Instance not found: {e}")
            return json.dumps(
                {
                    "Error": True,
                    "Message": str(e),
                    "Instance": None,
                    "InstanceId": instance_id,
                }
            )
        except Exception as e:
            logger.error(f"Error in _describe_ec2_instance: {e}")
            return json.dumps(
                {
                    "Error": True,
                    "Message": f"Error describing instance {instance_id}: {str(e)}",
                    "Instance": None,
                    "InstanceId": instance_id,
                }
            )

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
