"""
Unit tests for EC2Handler class.

Tests cover all functionality with mocked AWS clients to ensure
reliable testing without actual AWS API calls.
"""

from datetime import datetime
from unittest.mock import Mock

import pytest
from botocore.exceptions import ClientError

from aws_mcp.handlers.ec2 import (
    EC2Handler,
)


class TestEC2Handler:
    """Test cases for EC2Handler class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_client = Mock()
        self.handler = EC2Handler(region="us-east-1", client=self.mock_client)

    def test_initialization_default_region(self):
        """Test EC2Handler initialization with default region."""
        handler = EC2Handler()
        assert handler.region == "us-east-1"
        # Client should be created with default region
        assert handler.client is not None

    def test_initialization_custom_region(self):
        """Test EC2Handler initialization with custom region."""
        handler = EC2Handler(region="eu-west-1")
        assert handler.region == "eu-west-1"

    def test_initialization_with_injected_client(self):
        """Test EC2Handler initialization with dependency injection."""
        mock_client = Mock()
        handler = EC2Handler(region="us-west-2", client=mock_client)
        assert handler.region == "us-west-2"
        assert handler.client is mock_client

    def test_list_instances_empty_response(self):
        """Test listing instances when no instances exist."""
        # Mock empty response
        self.mock_client.describe_instances.return_value = {"Reservations": []}

        result = self.handler.list_instances()

        assert isinstance(result, dict)
        assert result["Instances"] == []
        assert result["Count"] == 0
        self.mock_client.describe_instances.assert_called_once_with(Filters=[])

    def test_list_instances_with_state_filter(self):
        """Test listing instances with state filter."""
        self.mock_client.describe_instances.return_value = {"Reservations": []}

        self.handler.list_instances(state="running")

        expected_filters = [{"Name": "instance-state-name", "Values": ["running"]}]
        self.mock_client.describe_instances.assert_called_once_with(Filters=expected_filters)

    def test_list_instances_single_instance(self):
        """Test listing instances with a single instance response."""
        # Mock response with one instance
        mock_datetime = datetime(2024, 1, 1, 12, 0, 0)
        mock_response = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-1234567890abcdef0",
                            "InstanceType": "t2.micro",
                            "State": {"Name": "running"},
                            "LaunchTime": mock_datetime,
                            "Placement": {"AvailabilityZone": "us-east-1a"},
                            "Tags": [{"Key": "Name", "Value": "test-instance"}],
                            "PublicIpAddress": "203.0.113.12",
                            "PrivateIpAddress": "10.0.0.123",
                        }
                    ]
                }
            ]
        }
        self.mock_client.describe_instances.return_value = mock_response

        result = self.handler.list_instances()

        assert result["Count"] == 1
        assert len(result["Instances"]) == 1

        instance = result["Instances"][0]
        assert instance["InstanceId"] == "i-1234567890abcdef0"
        assert instance["InstanceType"] == "t2.micro"
        assert instance["State"] == "running"
        assert instance["Name"] == "test-instance"
        assert instance["PublicIP"] == "203.0.113.12"
        assert instance["PrivateIP"] == "10.0.0.123"
        assert instance["AvailabilityZone"] == "us-east-1a"

    def test_list_instances_multiple_instances(self):
        """Test listing multiple instances across multiple reservations."""
        mock_datetime = datetime(2024, 1, 1, 12, 0, 0)
        mock_response = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-1111111111111111",
                            "InstanceType": "t2.micro",
                            "State": {"Name": "running"},
                            "LaunchTime": mock_datetime,
                            "Placement": {"AvailabilityZone": "us-east-1a"},
                            "Tags": [{"Key": "Name", "Value": "instance-1"}],
                        }
                    ]
                },
                {
                    "Instances": [
                        {
                            "InstanceId": "i-2222222222222222",
                            "InstanceType": "t3.small",
                            "State": {"Name": "stopped"},
                            "LaunchTime": mock_datetime,
                            "Placement": {"AvailabilityZone": "us-east-1b"},
                            "Tags": [],
                        }
                    ]
                },
            ]
        }
        self.mock_client.describe_instances.return_value = mock_response

        result = self.handler.list_instances()

        assert result["Count"] == 2
        assert len(result["Instances"]) == 2

        # Check first instance
        instance1 = result["Instances"][0]
        assert instance1["InstanceId"] == "i-1111111111111111"
        assert instance1["Name"] == "instance-1"

        # Check second instance (no name tag)
        instance2 = result["Instances"][1]
        assert instance2["InstanceId"] == "i-2222222222222222"
        assert instance2["Name"] == "N/A"

    def test_list_instances_no_ip_addresses(self):
        """Test listing instances without IP addresses."""
        mock_datetime = datetime(2024, 1, 1, 12, 0, 0)
        mock_response = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-1234567890abcdef0",
                            "InstanceType": "t2.micro",
                            "State": {"Name": "pending"},
                            "LaunchTime": mock_datetime,
                            "Placement": {"AvailabilityZone": "us-east-1a"},
                            "Tags": [],
                        }
                    ]
                }
            ]
        }
        self.mock_client.describe_instances.return_value = mock_response

        result = self.handler.list_instances()

        instance = result["Instances"][0]
        assert "PublicIP" not in instance
        assert "PrivateIP" not in instance

    def test_list_instances_client_error(self):
        """Test list_instances raises ClientError when AWS API fails."""
        error_response = {"Error": {"Code": "UnauthorizedOperation", "Message": "Access denied"}}
        self.mock_client.describe_instances.side_effect = ClientError(
            error_response, "DescribeInstances"
        )

        with pytest.raises(ClientError):
            self.handler.list_instances()

    def test_describe_instance_success(self):
        """Test successful instance description."""
        mock_datetime = datetime(2024, 1, 1, 12, 0, 0)
        mock_response = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-1234567890abcdef0",
                            "InstanceType": "t2.micro",
                            "State": {"Name": "running"},
                            "StateReason": {"Message": "running"},
                            "LaunchTime": mock_datetime,
                            "Platform": "Linux/Unix",
                            "Architecture": "x86_64",
                            "Placement": {"AvailabilityZone": "us-east-1a"},
                            "SecurityGroups": [{"GroupName": "default"}, {"GroupName": "web-sg"}],
                            "VpcId": "vpc-12345678",
                            "SubnetId": "subnet-12345678",
                            "KeyName": "my-key-pair",
                            "Tags": [{"Key": "Name", "Value": "test-instance"}],
                            "PublicIpAddress": "203.0.113.12",
                            "PrivateIpAddress": "10.0.0.123",
                        }
                    ]
                }
            ]
        }
        self.mock_client.describe_instances.return_value = mock_response

        result = self.handler.describe_instance("i-1234567890abcdef0")

        assert result["InstanceId"] == "i-1234567890abcdef0"
        assert result["InstanceType"] == "t2.micro"
        assert result["State"] == "running"
        assert result["StateReason"] == "running"
        assert result["Platform"] == "Linux/Unix"
        assert result["Architecture"] == "x86_64"
        assert result["AvailabilityZone"] == "us-east-1a"
        assert result["SecurityGroups"] == ["default", "web-sg"]
        assert result["VpcId"] == "vpc-12345678"
        assert result["SubnetId"] == "subnet-12345678"
        assert result["KeyName"] == "my-key-pair"
        assert result["Name"] == "test-instance"
        assert result["PublicIP"] == "203.0.113.12"
        assert result["PrivateIP"] == "10.0.0.123"

        self.mock_client.describe_instances.assert_called_once_with(
            InstanceIds=["i-1234567890abcdef0"]
        )

    def test_describe_instance_minimal_data(self):
        """Test instance description with minimal required data."""
        mock_datetime = datetime(2024, 1, 1, 12, 0, 0)
        mock_response = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-1234567890abcdef0",
                            "InstanceType": "t2.micro",
                            "State": {"Name": "stopped"},
                            "StateReason": {},  # Empty state reason
                            "LaunchTime": mock_datetime,
                            "Architecture": "x86_64",
                            "Placement": {"AvailabilityZone": "us-east-1a"},
                            "SecurityGroups": [],
                            "Tags": [],
                        }
                    ]
                }
            ]
        }
        self.mock_client.describe_instances.return_value = mock_response

        result = self.handler.describe_instance("i-1234567890abcdef0")

        assert result["InstanceId"] == "i-1234567890abcdef0"
        assert result["StateReason"] == "N/A"  # Default when no message
        assert result["Platform"] == "Linux/Unix"  # Default platform
        assert result["SecurityGroups"] == []
        assert "VpcId" not in result  # Optional field not present
        assert "SubnetId" not in result  # Optional field not present
        assert "KeyName" not in result  # Optional field not present
        assert "Name" not in result  # No name tag
        assert "PublicIP" not in result  # No public IP
        assert "PrivateIP" not in result  # No private IP

    def test_describe_instance_not_found(self):
        """Test describe_instance raises ValueError when instance not found."""
        mock_response = {"Reservations": []}
        self.mock_client.describe_instances.return_value = mock_response

        with pytest.raises(ValueError, match="Instance i-nonexistent not found"):
            self.handler.describe_instance("i-nonexistent")

    def test_describe_instance_client_error(self):
        """Test describe_instance raises ClientError when AWS API fails."""
        error_response = {
            "Error": {"Code": "InvalidInstanceID.NotFound", "Message": "Instance not found"}
        }
        self.mock_client.describe_instances.side_effect = ClientError(
            error_response, "DescribeInstances"
        )

        with pytest.raises(ClientError):
            self.handler.describe_instance("i-1234567890abcdef0")

    def test_describe_instance_with_windows_platform(self):
        """Test instance description with Windows platform."""
        mock_datetime = datetime(2024, 1, 1, 12, 0, 0)
        mock_response = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-1234567890abcdef0",
                            "InstanceType": "t2.micro",
                            "State": {"Name": "running"},
                            "StateReason": {"Message": "running"},
                            "LaunchTime": mock_datetime,
                            "Platform": "windows",
                            "Architecture": "x86_64",
                            "Placement": {"AvailabilityZone": "us-east-1a"},
                            "SecurityGroups": [],
                            "Tags": [],
                        }
                    ]
                }
            ]
        }
        self.mock_client.describe_instances.return_value = mock_response

        result = self.handler.describe_instance("i-1234567890abcdef0")

        assert result["Platform"] == "windows"


class TestEC2HandlerIntegration:
    """Integration-style tests that test the full flow without mocking internal methods."""

    def test_full_workflow_with_mock_client(self):
        """Test a complete workflow using a mock client."""
        mock_client = Mock()
        handler = EC2Handler(region="us-west-2", client=mock_client)

        # Setup mock responses
        list_response = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-1234567890abcdef0",
                            "InstanceType": "t2.micro",
                            "State": {"Name": "running"},
                            "LaunchTime": datetime(2024, 1, 1, 12, 0, 0),
                            "Placement": {"AvailabilityZone": "us-west-2a"},
                            "Tags": [{"Key": "Name", "Value": "test-instance"}],
                        }
                    ]
                }
            ]
        }

        detail_response = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-1234567890abcdef0",
                            "InstanceType": "t2.micro",
                            "State": {"Name": "running"},
                            "StateReason": {"Message": "running"},
                            "LaunchTime": datetime(2024, 1, 1, 12, 0, 0),
                            "Platform": "Linux/Unix",
                            "Architecture": "x86_64",
                            "Placement": {"AvailabilityZone": "us-west-2a"},
                            "SecurityGroups": [{"GroupName": "default"}],
                            "Tags": [{"Key": "Name", "Value": "test-instance"}],
                        }
                    ]
                }
            ]
        }

        mock_client.describe_instances.side_effect = [list_response, detail_response]

        # Test list instances
        list_result = handler.list_instances("running")
        assert list_result["Count"] == 1
        assert list_result["Instances"][0]["InstanceId"] == "i-1234567890abcdef0"

        # Test describe instance
        detail_result = handler.describe_instance("i-1234567890abcdef0")
        assert detail_result["InstanceId"] == "i-1234567890abcdef0"
        assert detail_result["SecurityGroups"] == ["default"]

        # Verify mock was called correctly
        assert mock_client.describe_instances.call_count == 2


"""
Additional test fixtures and utilities for EC2Handler testing.
"""


class TestEC2HandlerEdgeCases:
    """Test edge cases and error conditions for EC2Handler."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_client = Mock()
        self.handler = EC2Handler(region="us-east-1", client=self.mock_client)

    def test_list_instances_malformed_response(self):
        """Test handling of malformed AWS API response."""
        # Response missing required fields
        malformed_response = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-1234567890abcdef0",
                            # Missing required fields like InstanceType, State, etc.
                        }
                    ]
                }
            ]
        }
        self.mock_client.describe_instances.return_value = malformed_response

        # Should raise KeyError for missing required fields
        with pytest.raises(KeyError):
            self.handler.list_instances()

    def test_describe_instance_malformed_security_groups(self):
        """Test handling of malformed security groups in response."""
        mock_datetime = datetime(2024, 1, 1, 12, 0, 0)
        mock_response = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-1234567890abcdef0",
                            "InstanceType": "t2.micro",
                            "State": {"Name": "running"},
                            "LaunchTime": mock_datetime,
                            "Architecture": "x86_64",
                            "Placement": {"AvailabilityZone": "us-east-1a"},
                            "SecurityGroups": [
                                {"GroupName": "valid-sg"},
                                {},  # Malformed security group without GroupName
                            ],
                            "Tags": [],
                        }
                    ]
                }
            ]
        }
        self.mock_client.describe_instances.return_value = mock_response

        # Should raise KeyError for missing GroupName
        with pytest.raises(KeyError):
            self.handler.describe_instance("i-1234567890abcdef0")

    def test_describe_instance_empty_tags_list(self):
        """Test instance description with empty tags list."""
        mock_datetime = datetime(2024, 1, 1, 12, 0, 0)
        mock_response = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-1234567890abcdef0",
                            "InstanceType": "t2.micro",
                            "State": {"Name": "running"},
                            "LaunchTime": mock_datetime,
                            "Architecture": "x86_64",
                            "Placement": {"AvailabilityZone": "us-east-1a"},
                            "SecurityGroups": [],
                            "Tags": [],
                        }
                    ]
                }
            ]
        }
        self.mock_client.describe_instances.return_value = mock_response

        result = self.handler.describe_instance("i-1234567890abcdef0")

        # Should not include Name field when no name tag exists
        assert "Name" not in result

    @pytest.mark.parametrize("state_filter", ["running", "stopped", "pending", "terminated"])
    def test_list_instances_various_state_filters(self, state_filter):
        """Test list_instances with various state filters."""
        self.mock_client.describe_instances.return_value = {"Reservations": []}

        self.handler.list_instances(state=state_filter)

        expected_filters = [{"Name": "instance-state-name", "Values": [state_filter]}]
        self.mock_client.describe_instances.assert_called_once_with(Filters=expected_filters)

    def test_list_instances_all_state_no_filter(self):
        """Test list_instances with 'all' state applies no filters."""
        self.mock_client.describe_instances.return_value = {"Reservations": []}

        self.handler.list_instances(state="all")

        self.mock_client.describe_instances.assert_called_once_with(Filters=[])


@pytest.fixture
def sample_instance_data():
    """Fixture providing sample instance data for tests."""
    return {
        "InstanceId": "i-1234567890abcdef0",
        "InstanceType": "t2.micro",
        "State": {"Name": "running"},
        "LaunchTime": datetime(2024, 1, 1, 12, 0, 0),
        "Placement": {"AvailabilityZone": "us-east-1a"},
        "Tags": [
            {"Key": "Name", "Value": "test-instance"},
            {"Key": "Environment", "Value": "testing"},
        ],
        "PublicIpAddress": "203.0.113.12",
        "PrivateIpAddress": "10.0.0.123",
    }


@pytest.fixture
def sample_reservation(sample_instance_data):
    """Fixture providing sample reservation data."""
    return {"Reservations": [{"Instances": [sample_instance_data]}]}


class TestEC2HandlerWithFixtures:
    """Tests using pytest fixtures for cleaner test data."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_client = Mock()
        self.handler = EC2Handler(region="us-east-1", client=self.mock_client)

    def test_list_instances_with_fixture(self, sample_reservation):
        """Test list_instances using sample data fixture."""
        self.mock_client.describe_instances.return_value = sample_reservation

        result = self.handler.list_instances()

        assert result["Count"] == 1
        instance = result["Instances"][0]
        assert instance["InstanceId"] == "i-1234567890abcdef0"
        assert instance["Name"] == "test-instance"
