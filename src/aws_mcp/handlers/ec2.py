"""
EC2 service handler for AWS MCP Server.

This module provides functionality for managing EC2 instances through
natural language commands via the Model Context Protocol.
"""

import logging
from typing import NotRequired, TypedDict

import boto3


class InstanceInfo(TypedDict):
    """TypedDict for EC2 instance information."""

    InstanceId: str
    InstanceType: str
    State: str
    LaunchTime: str
    AvailabilityZone: str
    Name: str
    PublicIP: NotRequired[str]
    PrivateIP: NotRequired[str]


class InstanceListResponse(TypedDict):
    """TypedDict for list instances response."""

    Instances: list[InstanceInfo]
    Count: int


class InstanceDetailInfo(TypedDict):
    """TypedDict for detailed EC2 instance information."""

    InstanceId: str
    InstanceType: str
    State: str
    StateReason: str
    LaunchTime: str
    Platform: str
    Architecture: str
    AvailabilityZone: str
    SecurityGroups: list[str]
    VpcId: NotRequired[str]
    SubnetId: NotRequired[str]
    KeyName: NotRequired[str]
    Name: NotRequired[str]
    PublicIP: NotRequired[str]
    PrivateIP: NotRequired[str]


class InstanceDetailResponse(InstanceDetailInfo):
    """TypedDict for describe instance response."""

    pass


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

    def list_instances(self, state: str = "all") -> InstanceListResponse:
        """
        List EC2 instances in the region.

        Args:
            state: Instance state filter ('running', 'stopped', 'pending', 'terminated', 'all')

        Returns:
            InstanceListResponse containing:
            - Instances: List of instance dictionaries
            - Count: Number of instances

        Raises:
            ClientError: If AWS API call fails
            Exception: For other unexpected errors
        """
        filters = []
        if state != "all":
            filters.append({"Name": "instance-state-name", "Values": [state]})

        response = self.client.describe_instances(Filters=filters)

        instances: list[InstanceInfo] = []
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                # Add name tag if available
                name = "N/A"
                for tag in instance.get("Tags", []):
                    if tag["Key"] == "Name":
                        name = tag["Value"]
                        break

                # Create the instance info with all required fields
                instance_info: InstanceInfo = {
                    "InstanceId": instance["InstanceId"],
                    "InstanceType": instance["InstanceType"],
                    "State": instance["State"]["Name"],
                    "LaunchTime": instance["LaunchTime"].isoformat(),
                    "AvailabilityZone": instance["Placement"]["AvailabilityZone"],
                    "Name": name,
                }

                # Add IP addresses if available
                if "PublicIpAddress" in instance:
                    instance_info["PublicIP"] = instance["PublicIpAddress"]
                if "PrivateIpAddress" in instance:
                    instance_info["PrivateIP"] = instance["PrivateIpAddress"]

                instances.append(instance_info)

        logger.info(f"Listed {len(instances)} EC2 instances with state '{state}'")
        result: InstanceListResponse = {"Instances": instances, "Count": len(instances)}
        return result

    def describe_instance(self, instance_id: str) -> InstanceDetailResponse:
        """
        Get detailed information about a specific EC2 instance.

        Args:
            instance_id: The EC2 instance ID

        Returns:
            InstanceDetailResponse containing detailed instance information

        Raises:
            ClientError: If AWS API call fails
            ValueError: If instance not found
            Exception: For other unexpected errors
        """
        response = self.client.describe_instances(InstanceIds=[instance_id])

        if not response["Reservations"]:
            raise ValueError(f"Instance {instance_id} not found")

        instance = response["Reservations"][0]["Instances"][0]

        # Add name tag if available
        name: str | None = None
        for tag in instance.get("Tags", []):
            if tag["Key"] == "Name":
                name = tag["Value"]
                break

        # Extract relevant information
        instance_info: InstanceDetailResponse = {
            "InstanceId": instance["InstanceId"],
            "InstanceType": instance["InstanceType"],
            "State": instance["State"]["Name"],
            "StateReason": instance.get("StateReason", {}).get("Message", "N/A"),
            "LaunchTime": instance["LaunchTime"].isoformat(),
            "Platform": instance.get("Platform", "Linux/Unix"),
            "Architecture": instance["Architecture"],
            "AvailabilityZone": instance["Placement"]["AvailabilityZone"],
            "SecurityGroups": [sg["GroupName"] for sg in instance["SecurityGroups"]],
        }

        # Add optional fields
        if instance.get("VpcId"):
            instance_info["VpcId"] = instance["VpcId"]
        if instance.get("SubnetId"):
            instance_info["SubnetId"] = instance["SubnetId"]
        if instance.get("KeyName"):
            instance_info["KeyName"] = instance["KeyName"]
        if name:
            instance_info["Name"] = name

        # Add IP addresses if available
        if "PublicIpAddress" in instance:
            instance_info["PublicIP"] = instance["PublicIpAddress"]
        if "PrivateIpAddress" in instance:
            instance_info["PrivateIP"] = instance["PrivateIpAddress"]

        logger.info(f"Retrieved details for instance {instance_id}")
        return instance_info
