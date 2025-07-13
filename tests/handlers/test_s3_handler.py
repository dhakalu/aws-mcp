"""
Unit tests for S3 handlers.

Tests cover all S3 handler functionality with mocked AWS clients to ensure
reliable testing without actual AWS API calls.
"""

import json
from unittest.mock import Mock, patch

import pytest

from aws_mcp.handlers.s3 import list_s3_buckets


class TestS3Handlers:
    """Test cases for S3 handlers."""

    @pytest.mark.asyncio
    @patch("aws_mcp.handlers.s3.S3Service")
    async def test_list_s3_buckets_success(self, mock_s3_service):
        """Test successful S3 bucket listing."""
        # Mock the service response
        mock_service_instance = Mock()
        mock_service_instance.list_buckets.return_value = {
            "Buckets": [
                {"Name": "bucket-1", "CreationDate": "2024-01-01T12:00:00"},
                {"Name": "bucket-2", "CreationDate": "2024-02-01T10:30:00"},
            ],
            "Count": 2,
        }
        mock_s3_service.return_value = mock_service_instance

        result = await list_s3_buckets("us-east-1")

        # Parse the JSON response
        parsed_result = json.loads(result)

        assert parsed_result["Error"] is False
        assert parsed_result["Count"] == 2
        assert parsed_result["Region"] == "us-east-1"
        assert len(parsed_result["Buckets"]) == 2
        assert parsed_result["Buckets"][0]["Name"] == "bucket-1"
        assert parsed_result["Buckets"][1]["Name"] == "bucket-2"

        # Verify service was called correctly
        mock_s3_service.assert_called_once_with("us-east-1")
        mock_service_instance.list_buckets.assert_called_once()

    @pytest.mark.asyncio
    @patch("aws_mcp.handlers.s3.S3Service")
    async def test_list_s3_buckets_empty(self, mock_s3_service):
        """Test S3 bucket listing when no buckets exist."""
        # Mock empty response
        mock_service_instance = Mock()
        mock_service_instance.list_buckets.return_value = {
            "Buckets": [],
            "Count": 0,
        }
        mock_s3_service.return_value = mock_service_instance

        result = await list_s3_buckets("us-west-2")

        # Parse the JSON response
        parsed_result = json.loads(result)

        assert parsed_result["Error"] is False
        assert parsed_result["Message"] == "No S3 buckets found in us-west-2"
        assert parsed_result["Count"] == 0
        assert parsed_result["Region"] == "us-west-2"
        assert parsed_result["Buckets"] == []

    @pytest.mark.asyncio
    @patch("aws_mcp.handlers.s3.S3Service")
    async def test_list_s3_buckets_default_region(self, mock_s3_service):
        """Test S3 bucket listing with default region."""
        # Mock the service response
        mock_service_instance = Mock()
        mock_service_instance.list_buckets.return_value = {
            "Buckets": [{"Name": "test-bucket", "CreationDate": "2024-01-01T12:00:00"}],
            "Count": 1,
        }
        mock_s3_service.return_value = mock_service_instance

        result = await list_s3_buckets()

        # Parse the JSON response
        parsed_result = json.loads(result)

        assert parsed_result["Error"] is False
        assert parsed_result["Region"] == "us-east-1"

        # Verify service was called with default region
        mock_s3_service.assert_called_once_with("us-east-1")

    @pytest.mark.asyncio
    @patch("aws_mcp.handlers.s3.S3Service")
    async def test_list_s3_buckets_exception(self, mock_s3_service):
        """Test S3 bucket listing when an exception occurs."""
        # Mock service to raise an exception
        mock_service_instance = Mock()
        mock_service_instance.list_buckets.side_effect = Exception("AWS API Error")
        mock_s3_service.return_value = mock_service_instance

        result = await list_s3_buckets("eu-west-1")

        # Parse the JSON response
        parsed_result = json.loads(result)

        assert parsed_result["Error"] is True
        assert "Error listing S3 buckets: AWS API Error" in parsed_result["Message"]
        assert parsed_result["Buckets"] == []
        assert parsed_result["Count"] == 0
