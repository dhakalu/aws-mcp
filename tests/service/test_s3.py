"""
Unit tests for S3Service class.

Tests cover all functionality with mocked AWS clients to ensure
reliable testing without actual AWS API calls.
"""

from datetime import datetime
from unittest.mock import Mock

import pytest
from botocore.exceptions import ClientError

from aws_mcp.service.s3 import (
    S3Service,
)


class TestS3Service:
    """Test cases for S3Service class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_client = Mock()
        self.handler = S3Service(region="us-east-1", client=self.mock_client)

    def test_initialization_default_region(self):
        """Test S3Service initialization with default region."""
        handler = S3Service()
        assert handler.region == "us-east-1"
        # Client should be created with default region
        assert handler.client is not None

    def test_initialization_custom_region(self):
        """Test S3Service initialization with custom region."""
        handler = S3Service(region="eu-west-1")
        assert handler.region == "eu-west-1"

    def test_initialization_with_injected_client(self):
        """Test S3Service initialization with dependency injection."""
        mock_client = Mock()
        handler = S3Service(region="us-west-2", client=mock_client)
        assert handler.region == "us-west-2"
        assert handler.client is mock_client

    def test_list_buckets_empty_response(self):
        """Test listing buckets when no buckets exist."""
        # Mock empty response
        self.mock_client.list_buckets.return_value = {"Buckets": []}

        result = self.handler.list_buckets()

        assert isinstance(result, dict)
        assert result["Buckets"] == []
        assert result["Count"] == 0
        self.mock_client.list_buckets.assert_called_once_with()

    def test_list_buckets_missing_buckets_key(self):
        """Test listing buckets when response doesn't have Buckets key."""
        # Mock response without Buckets key
        self.mock_client.list_buckets.return_value = {}

        result = self.handler.list_buckets()

        assert isinstance(result, dict)
        assert result["Buckets"] == []
        assert result["Count"] == 0
        self.mock_client.list_buckets.assert_called_once_with()

    def test_list_buckets_single_bucket(self):
        """Test listing buckets with a single bucket response."""
        # Mock response with one bucket
        mock_datetime = datetime(2024, 1, 1, 12, 0, 0)
        mock_response = {
            "Buckets": [
                {
                    "Name": "my-test-bucket",
                    "CreationDate": mock_datetime,
                }
            ]
        }
        self.mock_client.list_buckets.return_value = mock_response

        result = self.handler.list_buckets()

        assert result["Count"] == 1
        assert len(result["Buckets"]) == 1

        bucket = result["Buckets"][0]
        assert bucket["Name"] == "my-test-bucket"
        assert bucket["CreationDate"] == mock_datetime.isoformat()

    def test_list_buckets_multiple_buckets(self):
        """Test listing multiple buckets."""
        mock_datetime1 = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime2 = datetime(2024, 2, 1, 10, 30, 0)
        mock_datetime3 = datetime(2024, 3, 15, 8, 15, 30)
        
        mock_response = {
            "Buckets": [
                {
                    "Name": "bucket-one",
                    "CreationDate": mock_datetime1,
                },
                {
                    "Name": "bucket-two",
                    "CreationDate": mock_datetime2,
                },
                {
                    "Name": "bucket-three",
                    "CreationDate": mock_datetime3,
                },
            ]
        }
        self.mock_client.list_buckets.return_value = mock_response

        result = self.handler.list_buckets()

        assert result["Count"] == 3
        assert len(result["Buckets"]) == 3

        # Check first bucket
        bucket1 = result["Buckets"][0]
        assert bucket1["Name"] == "bucket-one"
        assert bucket1["CreationDate"] == mock_datetime1.isoformat()

        # Check second bucket
        bucket2 = result["Buckets"][1]
        assert bucket2["Name"] == "bucket-two"
        assert bucket2["CreationDate"] == mock_datetime2.isoformat()

        # Check third bucket
        bucket3 = result["Buckets"][2]
        assert bucket3["Name"] == "bucket-three"
        assert bucket3["CreationDate"] == mock_datetime3.isoformat()

    def test_list_buckets_client_error(self):
        """Test list_buckets raises ClientError when AWS API fails."""
        error_response = {"Error": {"Code": "AccessDenied", "Message": "Access denied"}}
        self.mock_client.list_buckets.side_effect = ClientError(
            error_response, "ListBuckets"
        )

        with pytest.raises(ClientError):
            self.handler.list_buckets()

    def test_list_buckets_handles_different_datetime_formats(self):
        """Test listing buckets with different datetime formats."""
        # Test with timezone-aware datetime
        from datetime import timezone
        mock_datetime = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        mock_response = {
            "Buckets": [
                {
                    "Name": "tz-aware-bucket",
                    "CreationDate": mock_datetime,
                }
            ]
        }
        self.mock_client.list_buckets.return_value = mock_response

        result = self.handler.list_buckets()

        assert result["Count"] == 1
        bucket = result["Buckets"][0]
        assert bucket["Name"] == "tz-aware-bucket"
        assert bucket["CreationDate"] == mock_datetime.isoformat()

    def test_list_buckets_with_special_bucket_names(self):
        """Test listing buckets with special characters in names."""
        mock_datetime = datetime(2024, 1, 1, 12, 0, 0)
        
        mock_response = {
            "Buckets": [
                {
                    "Name": "bucket-with-dashes",
                    "CreationDate": mock_datetime,
                },
                {
                    "Name": "bucket.with.dots",
                    "CreationDate": mock_datetime,
                },
                {
                    "Name": "bucketwith123numbers",
                    "CreationDate": mock_datetime,
                },
            ]
        }
        self.mock_client.list_buckets.return_value = mock_response

        result = self.handler.list_buckets()

        assert result["Count"] == 3
        bucket_names = [bucket["Name"] for bucket in result["Buckets"]]
        assert "bucket-with-dashes" in bucket_names
        assert "bucket.with.dots" in bucket_names
        assert "bucketwith123numbers" in bucket_names

    def test_list_buckets_response_structure(self):
        """Test that list_buckets returns the correct response structure."""
        mock_datetime = datetime(2024, 1, 1, 12, 0, 0)
        mock_response = {
            "Buckets": [
                {
                    "Name": "test-bucket",
                    "CreationDate": mock_datetime,
                }
            ]
        }
        self.mock_client.list_buckets.return_value = mock_response

        result = self.handler.list_buckets()

        # Verify response structure matches BucketListResponse TypedDict
        assert isinstance(result, dict)
        assert "Buckets" in result
        assert "Count" in result
        assert isinstance(result["Buckets"], list)
        assert isinstance(result["Count"], int)
        
        # Verify bucket structure matches BucketInfo TypedDict
        if result["Buckets"]:
            bucket = result["Buckets"][0]
            assert isinstance(bucket, dict)
            assert "Name" in bucket
            assert "CreationDate" in bucket
            assert isinstance(bucket["Name"], str)
            assert isinstance(bucket["CreationDate"], str)
