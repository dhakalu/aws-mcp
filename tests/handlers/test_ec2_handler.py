"""
Unit tests for EC2 handlers.

Tests cover all handler functionality with mocked services to ensure
reliable testing without actual AWS API calls.
"""

import json
from unittest.mock import Mock, patch

import pytest

from aws_mcp.handlers.ec2 import describe_ec2_instance, list_ec2_instances


class TestListEC2Instances:
    """Test cases for list_ec2_instances handler."""

    @pytest.mark.asyncio
    @patch("aws_mcp.handlers.ec2.EC2Service")
    async def test_list_instances_success_with_instances(self, mock_ec2_service_class):
        """Test successful listing of EC2 instances when instances exist."""
        # Setup mock service
        mock_service = Mock()
        mock_ec2_service_class.return_value = mock_service

        mock_instances = [
            {
                "InstanceId": "i-1234567890abcdef0",
                "InstanceType": "t3.micro",
                "State": "running",
                "LaunchTime": "2023-01-01T12:00:00+00:00",
                "AvailabilityZone": "us-east-1a",
                "Name": "test-instance-1",
                "PublicIP": "1.2.3.4",
                "PrivateIP": "10.0.1.10",
            },
            {
                "InstanceId": "i-0987654321fedcba0",
                "InstanceType": "t3.small",
                "State": "stopped",
                "LaunchTime": "2023-01-02T10:30:00+00:00",
                "AvailabilityZone": "us-east-1b",
                "Name": "test-instance-2",
                "PrivateIP": "10.0.1.20",
            },
        ]

        mock_service.list_instances.return_value = {"Instances": mock_instances, "Count": 2}

        # Call the handler
        result = await list_ec2_instances("us-east-1", "running")

        # Parse and verify the response
        response = json.loads(result)
        assert response["Error"] is False
        assert response["Count"] == 2
        assert response["Region"] == "us-east-1"
        assert response["StateFilter"] == "running"
        assert len(response["Instances"]) == 2
        assert response["Instances"][0]["InstanceId"] == "i-1234567890abcdef0"

        # Verify service was called correctly
        mock_ec2_service_class.assert_called_once_with("us-east-1")
        mock_service.list_instances.assert_called_once_with("running")

    @pytest.mark.asyncio
    @patch("aws_mcp.handlers.ec2.EC2Service")
    async def test_list_instances_success_empty_response(self, mock_ec2_service_class):
        """Test successful listing when no instances exist."""
        # Setup mock service
        mock_service = Mock()
        mock_ec2_service_class.return_value = mock_service

        mock_service.list_instances.return_value = {"Instances": [], "Count": 0}

        # Call the handler
        result = await list_ec2_instances("eu-west-1", "terminated")

        # Parse and verify the response
        response = json.loads(result)
        assert response["Error"] is False
        assert response["Message"] == "No EC2 instances found in eu-west-1 with state 'terminated'"
        assert response["Count"] == 0
        assert response["Region"] == "eu-west-1"
        assert response["StateFilter"] == "terminated"
        assert response["Instances"] == []

        # Verify service was called correctly
        mock_ec2_service_class.assert_called_once_with("eu-west-1")
        mock_service.list_instances.assert_called_once_with("terminated")

    @pytest.mark.asyncio
    @patch("aws_mcp.handlers.ec2.EC2Service")
    async def test_list_instances_default_state(self, mock_ec2_service_class):
        """Test listing instances with default state parameter."""
        # Setup mock service
        mock_service = Mock()
        mock_ec2_service_class.return_value = mock_service

        mock_service.list_instances.return_value = {"Instances": [], "Count": 0}

        # Call the handler without state parameter
        await list_ec2_instances("us-west-2")

        # Verify service was called with default "all" state
        mock_service.list_instances.assert_called_once_with("all")

    @pytest.mark.asyncio
    @patch("aws_mcp.handlers.ec2.EC2Service")
    async def test_list_instances_service_exception(self, mock_ec2_service_class):
        """Test handling of service exceptions."""
        # Setup mock service to raise exception
        mock_service = Mock()
        mock_ec2_service_class.return_value = mock_service
        mock_service.list_instances.side_effect = Exception("AWS API Error")

        # Call the handler
        result = await list_ec2_instances("us-east-1", "running")

        # Parse and verify error response
        response = json.loads(result)
        assert response["Error"] is True
        assert "Error listing EC2 instances: AWS API Error" in response["Message"]
        assert response["Count"] == 0
        assert response["Instances"] == []

    @pytest.mark.asyncio
    @patch("aws_mcp.handlers.ec2.EC2Service")
    async def test_list_instances_service_initialization_error(self, mock_ec2_service_class):
        """Test handling of service initialization errors."""
        # Setup mock to raise exception during initialization
        mock_ec2_service_class.side_effect = Exception("Invalid region")

        # Call the handler
        result = await list_ec2_instances("invalid-region", "running")

        # Parse and verify error response
        response = json.loads(result)
        assert response["Error"] is True
        assert "Error listing EC2 instances: Invalid region" in response["Message"]
        assert response["Count"] == 0
        assert response["Instances"] == []


class TestDescribeEC2Instance:
    """Test cases for describe_ec2_instance handler."""

    @pytest.mark.asyncio
    @patch("aws_mcp.handlers.ec2.EC2Service")
    async def test_describe_instance_success(self, mock_ec2_service_class):
        """Test successful description of an EC2 instance."""
        # Setup mock service
        mock_service = Mock()
        mock_ec2_service_class.return_value = mock_service

        mock_instance_detail = {
            "InstanceId": "i-1234567890abcdef0",
            "InstanceType": "t3.micro",
            "State": "running",
            "StateReason": "User initiated",
            "LaunchTime": "2023-01-01T12:00:00+00:00",
            "Platform": "Linux/Unix",
            "Architecture": "x86_64",
            "AvailabilityZone": "us-east-1a",
            "SecurityGroups": ["default", "web-sg"],
            "VpcId": "vpc-12345678",
            "SubnetId": "subnet-87654321",
            "KeyName": "my-key-pair",
            "Name": "test-instance",
            "PublicIP": "1.2.3.4",
            "PrivateIP": "10.0.1.10",
        }

        mock_service.describe_instance.return_value = mock_instance_detail

        # Call the handler
        result = await describe_ec2_instance("us-east-1", "i-1234567890abcdef0")

        # Parse and verify the response
        response = json.loads(result)
        assert response["Error"] is False
        assert (
            response["Message"] == "Successfully retrieved details for instance i-1234567890abcdef0"
        )
        assert response["InstanceId"] == "i-1234567890abcdef0"
        assert response["Region"] == "us-east-1"
        assert response["Instance"] == mock_instance_detail
        assert response["Instance"]["InstanceType"] == "t3.micro"
        assert response["Instance"]["State"] == "running"

        # Verify service was called correctly
        mock_ec2_service_class.assert_called_once_with("us-east-1")
        mock_service.describe_instance.assert_called_once_with("i-1234567890abcdef0")

    @pytest.mark.asyncio
    @patch("aws_mcp.handlers.ec2.EC2Service")
    async def test_describe_instance_not_found(self, mock_ec2_service_class):
        """Test handling when instance is not found."""
        # Setup mock service to raise ValueError (instance not found)
        mock_service = Mock()
        mock_ec2_service_class.return_value = mock_service
        mock_service.describe_instance.side_effect = ValueError("Instance i-nonexistent not found")

        # Call the handler
        result = await describe_ec2_instance("us-east-1", "i-nonexistent")

        # Parse and verify error response
        response = json.loads(result)
        assert response["Error"] is True
        assert response["Message"] == "Instance i-nonexistent not found"
        assert response["Instance"] is None
        assert response["InstanceId"] == "i-nonexistent"

    @pytest.mark.asyncio
    @patch("aws_mcp.handlers.ec2.EC2Service")
    async def test_describe_instance_service_exception(self, mock_ec2_service_class):
        """Test handling of general service exceptions."""
        # Setup mock service to raise general exception
        mock_service = Mock()
        mock_ec2_service_class.return_value = mock_service
        mock_service.describe_instance.side_effect = Exception("AWS API Error")

        # Call the handler
        result = await describe_ec2_instance("us-east-1", "i-1234567890abcdef0")

        # Parse and verify error response
        response = json.loads(result)
        assert response["Error"] is True
        assert "Error describing instance i-1234567890abcdef0: AWS API Error" in response["Message"]
        assert response["Instance"] is None
        assert response["InstanceId"] == "i-1234567890abcdef0"

    @pytest.mark.asyncio
    @patch("aws_mcp.handlers.ec2.EC2Service")
    async def test_describe_instance_service_initialization_error(self, mock_ec2_service_class):
        """Test handling of service initialization errors."""
        # Setup mock to raise exception during initialization
        mock_ec2_service_class.side_effect = Exception("Invalid region")

        # Call the handler
        result = await describe_ec2_instance("invalid-region", "i-1234567890abcdef0")

        # Parse and verify error response
        response = json.loads(result)
        assert response["Error"] is True
        assert (
            "Error describing instance i-1234567890abcdef0: Invalid region" in response["Message"]
        )
        assert response["Instance"] is None
        assert response["InstanceId"] == "i-1234567890abcdef0"

    @pytest.mark.asyncio
    @patch("aws_mcp.handlers.ec2.EC2Service")
    async def test_describe_instance_minimal_response(self, mock_ec2_service_class):
        """Test description with minimal instance data (only required fields)."""
        # Setup mock service
        mock_service = Mock()
        mock_ec2_service_class.return_value = mock_service

        # Minimal instance detail with only required fields
        mock_instance_detail = {
            "InstanceId": "i-minimal123",
            "InstanceType": "t2.nano",
            "State": "stopped",
            "StateReason": "User initiated",
            "LaunchTime": "2023-01-01T12:00:00+00:00",
            "Platform": "Linux/Unix",
            "Architecture": "x86_64",
            "AvailabilityZone": "us-west-2a",
            "SecurityGroups": ["default"],
        }

        mock_service.describe_instance.return_value = mock_instance_detail

        # Call the handler
        result = await describe_ec2_instance("us-west-2", "i-minimal123")

        # Parse and verify the response
        response = json.loads(result)
        assert response["Error"] is False
        assert response["Instance"]["InstanceId"] == "i-minimal123"
        assert response["Instance"]["State"] == "stopped"
        assert "VpcId" not in response["Instance"]  # Optional field not present
        assert "Name" not in response["Instance"]  # Optional field not present
