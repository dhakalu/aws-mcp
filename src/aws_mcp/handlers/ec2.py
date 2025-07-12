"""
EC2 service handler for AWS MCP Server.

This module provides functionality for managing EC2 instances through
natural language commands via the Model Context Protocol.
"""

import logging
from typing import Any

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class EC2Handler:
    """Handler for Amazon EC2 operations."""

    def __init__(self, region: str = "us-east-1"):
        """
        Initialize the EC2 handler.

        Args:
            region: AWS region to operate in
        """
        self.region = region
        self.client = boto3.client("ec2", region_name=region)
        logger.info(f"EC2 handler initialized for region: {region}")

    def list_instances(self, state: str = "all") -> dict[str, Any]:
        """
        List EC2 instances in the region.

        Args:
            state: Instance state filter ('running', 'stopped', 'pending', 'terminated', 'all')

        Returns:
            Dictionary containing instance information
        """
        try:
            filters = []
            if state != "all":
                filters.append({"Name": "instance-state-name", "Values": [state]})

            response = self.client.describe_instances(Filters=filters)

            instances = []
            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    instance_info = {
                        "InstanceId": instance["InstanceId"],
                        "InstanceType": instance["InstanceType"],
                        "State": instance["State"]["Name"],
                        "LaunchTime": instance["LaunchTime"].isoformat(),
                        "AvailabilityZone": instance["Placement"]["AvailabilityZone"],
                    }

                    # Add name tag if available
                    name = "N/A"
                    for tag in instance.get("Tags", []):
                        if tag["Key"] == "Name":
                            name = tag["Value"]
                            break
                    instance_info["Name"] = name

                    # Add IP addresses if available
                    if "PublicIpAddress" in instance:
                        instance_info["PublicIP"] = instance["PublicIpAddress"]
                    if "PrivateIpAddress" in instance:
                        instance_info["PrivateIP"] = instance["PrivateIpAddress"]

                    instances.append(instance_info)

            logger.info(f"Listed {len(instances)} EC2 instances with state '{state}'")
            return {"instances": instances, "count": len(instances)}

        except ClientError as e:
            logger.error(f"Failed to list EC2 instances: {e}")
            return {"error": str(e), "instances": [], "count": 0}
        except Exception as e:
            logger.error(f"Unexpected error listing EC2 instances: {e}")
            return {"error": str(e), "instances": [], "count": 0}

    def describe_instance(self, instance_id: str) -> dict[str, Any]:
        """
        Get detailed information about a specific EC2 instance.

        Args:
            instance_id: The EC2 instance ID

        Returns:
            Dictionary containing detailed instance information
        """
        try:
            response = self.client.describe_instances(InstanceIds=[instance_id])

            if not response["Reservations"]:
                return {"error": f"Instance {instance_id} not found"}

            instance = response["Reservations"][0]["Instances"][0]

            # Extract relevant information
            instance_info = {
                "InstanceId": instance["InstanceId"],
                "InstanceType": instance["InstanceType"],
                "State": instance["State"]["Name"],
                "StateReason": instance.get("StateReason", {}).get("Message", "N/A"),
                "LaunchTime": instance["LaunchTime"].isoformat(),
                "Platform": instance.get("Platform", "Linux/Unix"),
                "Architecture": instance["Architecture"],
                "VpcId": instance.get("VpcId"),
                "SubnetId": instance.get("SubnetId"),
                "AvailabilityZone": instance["Placement"]["AvailabilityZone"],
                "SecurityGroups": [sg["GroupName"] for sg in instance["SecurityGroups"]],
                "KeyName": instance.get("KeyName"),
            }

            # Add name tag if available
            for tag in instance.get("Tags", []):
                if tag["Key"] == "Name":
                    instance_info["Name"] = tag["Value"]
                    break

            # Add IP addresses if available
            if "PublicIpAddress" in instance:
                instance_info["PublicIP"] = instance["PublicIpAddress"]
            if "PrivateIpAddress" in instance:
                instance_info["PrivateIP"] = instance["PrivateIpAddress"]

            logger.info(f"Retrieved details for instance {instance_id}")
            return instance_info

        except ClientError as e:
            logger.error(f"Failed to describe instance {instance_id}: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error describing instance {instance_id}: {e}")
            return {"error": str(e)}
