"""
Tests for AWS utility functions.
"""

import os
from unittest.mock import patch

from aws_mcp.utils.auth import AWSAuth, get_default_region
from aws_mcp.utils.helpers import (
    build_error_response,
    build_success_response,
    extract_instance_id,
    format_file_size,
    parse_s3_uri,
    validate_aws_resource_name,
)

# TODO: Import when dependencies are available
# import pytest


class TestHelpers:
    """Test cases for helper utility functions."""

    def test_validate_s3_bucket_name(self):
        """Test S3 bucket name validation."""
        assert validate_aws_resource_name("my-bucket", "s3") == True
        assert validate_aws_resource_name("my.bucket", "s3") == True
        assert validate_aws_resource_name("MyBucket", "s3") == False  # uppercase not allowed
        assert validate_aws_resource_name("my..bucket", "s3") == False  # double dots not allowed
        assert validate_aws_resource_name("", "s3") == False  # empty name

    def test_validate_lambda_function_name(self):
        """Test Lambda function name validation."""
        assert validate_aws_resource_name("my-function", "lambda") == True
        assert validate_aws_resource_name("my_function", "lambda") == True
        assert validate_aws_resource_name("MyFunction123", "lambda") == True
        assert (
            validate_aws_resource_name("my-function!", "lambda") == False
        )  # special chars not allowed

    def test_parse_s3_uri(self):
        """Test S3 URI parsing."""
        result = parse_s3_uri("s3://my-bucket/path/to/file.txt")
        assert result == {"bucket": "my-bucket", "key": "path/to/file.txt"}

        result = parse_s3_uri("invalid-uri")
        assert result is None

    def test_format_file_size(self):
        """Test file size formatting."""
        assert format_file_size(0) == "0 B"
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1536) == "1.5 KB"
        assert format_file_size(1048576) == "1.0 MB"

    def test_extract_instance_id(self):
        """Test instance ID extraction."""
        assert extract_instance_id("i-1234567890abcdef0") == "i-1234567890abcdef0"
        assert extract_instance_id("invalid-id") is None

    def test_build_error_response(self):
        """Test error response building."""
        response = build_error_response("TestError", "Test message")
        assert response["error"]["type"] == "TestError"
        assert response["error"]["message"] == "Test message"
        assert "timestamp" in response["error"]

    def test_build_success_response(self):
        """Test success response building."""
        data = {"result": "success"}
        response = build_success_response(data, "Operation completed")
        assert response["success"] == True
        assert response["data"] == data
        assert response["message"] == "Operation completed"
        assert "timestamp" in response


class TestAuth:
    """Test cases for authentication utilities."""

    def test_aws_auth_initialization(self):
        """Test AWSAuth initialization."""
        auth = AWSAuth()
        assert auth.region == "us-east-1"
        assert auth.profile is None

        auth_with_profile = AWSAuth(region="eu-west-1", profile="test")
        assert auth_with_profile.region == "eu-west-1"
        assert auth_with_profile.profile == "test"

    def test_get_credentials(self):
        """Test credential information retrieval."""
        auth = AWSAuth()
        creds = auth.get_credentials()
        assert "region" in creds
        assert "profile" in creds
        assert "status" in creds

    @patch.dict(os.environ, {"AWS_DEFAULT_REGION": "us-west-2"})
    def test_get_default_region_from_env(self):
        """Test getting default region from environment."""
        assert get_default_region() == "us-west-2"

    @patch.dict(os.environ, {}, clear=True)
    def test_get_default_region_fallback(self):
        """Test getting default region fallback."""
        assert get_default_region() == "us-east-1"
