"""
EC2 handlers for AWS Model Context Protocol (MCP) Server.

This module bridges the MCP server with AWS EC2 service functionalities, providing error
handling and response formatting for various EC2 operations.
"""

import json
import logging

from aws_mcp.service.ec2 import EC2Service

logger = logging.getLogger(__name__)


async def list_ec2_instances(region: str, state: str = "all") -> str:
    """List EC2 instances"""
    try:

        service = EC2Service(region)
        result = service.list_instances(state)

        instances = result["Instances"]
        if not instances:
            return json.dumps(
                {
                    "Error": False,
                    "Message": f"No EC2 instances found in {region} with state '{state}'",
                    "Instances": [],
                    "Count": 0,
                    "Region": region,
                    "StateFilter": state,
                }
            )

        return json.dumps(
            {
                "Error": False,
                "Instances": instances,
                "Count": result["Count"],
                "Region": region,
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


async def describe_ec2_instance(region: str, instance_id: str) -> str:
    """Describe a specific EC2 instance"""
    try:
        service = EC2Service(region)
        result = service.describe_instance(instance_id)

        return json.dumps(
            {
                "Error": False,
                "Message": f"Successfully retrieved details for instance {instance_id}",
                "Instance": result,
                "InstanceId": instance_id,
                "Region": region,
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
