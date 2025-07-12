"""
AWS MCP Server implementation.

This module contains the main MCP server that handles communication between
AI assistants and AWS services.
"""

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

            if "error" in result:
                return f"Error listing EC2 instances: {result['error']}"

            instances = result["instances"]
            if not instances:
                return f"No EC2 instances found in {self.region} with state '{state}'"

            # Format the response
            response = f"Found {result['count']} EC2 instance(s) in {self.region}:\n\n"
            for instance in instances:
                response += f"• {instance['InstanceId']} ({instance['Name']})\n"
                response += f"  Type: {instance['InstanceType']}\n"
                response += f"  State: {instance['State']}\n"
                response += f"  Zone: {instance['AvailabilityZone']}\n"
                if "PublicIP" in instance:
                    response += f"  Public IP: {instance['PublicIP']}\n"
                if "PrivateIP" in instance:
                    response += f"  Private IP: {instance['PrivateIP']}\n"
                response += "\n"

            return response.strip()

        except Exception as e:
            logger.error(f"Error in _list_ec2_instances: {e}")
            return f"Error listing EC2 instances: {str(e)}"

    async def _describe_ec2_instance(self, instance_id: str) -> str:
        """Describe a specific EC2 instance using boto3."""
        try:
            from aws_mcp.handlers.ec2 import EC2Handler

            handler = EC2Handler(self.region)
            result = handler.describe_instance(instance_id)

            if "error" in result:
                return f"Error describing instance {instance_id}: {result['error']}"

            # Format the detailed response
            response = f"EC2 Instance Details for {instance_id}:\n\n"
            response += f"Name: {result.get('Name', 'N/A')}\n"
            response += f"Instance Type: {result['InstanceType']}\n"
            response += f"State: {result['State']}\n"
            response += f"State Reason: {result['StateReason']}\n"
            response += f"Platform: {result['Platform']}\n"
            response += f"Architecture: {result['Architecture']}\n"
            response += f"Availability Zone: {result['AvailabilityZone']}\n"
            response += f"Launch Time: {result['LaunchTime']}\n"

            if result.get("VpcId"):
                response += f"VPC ID: {result['VpcId']}\n"
            if result.get("SubnetId"):
                response += f"Subnet ID: {result['SubnetId']}\n"
            if result.get("PublicIP"):
                response += f"Public IP: {result['PublicIP']}\n"
            if result.get("PrivateIP"):
                response += f"Private IP: {result['PrivateIP']}\n"
            if result.get("KeyName"):
                response += f"Key Pair: {result['KeyName']}\n"

            if result.get("SecurityGroups"):
                response += f"Security Groups: {', '.join(result['SecurityGroups'])}\n"

            return response.strip()

        except Exception as e:
            logger.error(f"Error in _describe_ec2_instance: {e}")
            return f"Error describing instance {instance_id}: {str(e)}"

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
