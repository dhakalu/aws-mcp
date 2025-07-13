"""
S3 service facade for AWS MCP Server.

This module provides a simplified facade over boto3 S3 client interactions,
offering type-safe methods for common S3 operations with structured responses.
The facade pattern abstracts away boto3 complexity and provides consistent
error handling and data transformation.
"""

import logging
from typing import Any, Protocol, TypedDict

import boto3


class S3ClientProtocol(Protocol):
    """Protocol for S3 client to enable dependency injection and testing."""

    def list_buckets(self, **kwargs: Any) -> dict:
        """List S3 buckets."""
        ...


class BucketInfo(TypedDict):
    """TypedDict for S3 bucket information."""

    Name: str
    CreationDate: str


class BucketListResponse(TypedDict):
    """TypedDict for list buckets response."""

    Buckets: list[BucketInfo]
    Count: int


logger = logging.getLogger(__name__)


class S3Service:
    """Service for Amazon S3 operations that manages S3 buckets using boto3."""

    def __init__(self, region: str = "us-east-1", client: S3ClientProtocol | None = None):
        """
        Initialize the S3 service.

        Args:
            region: AWS region to operate in
            client: Optional S3 client for dependency injection (useful for testing)
        """
        self.region = region
        self.client = client or boto3.client("s3", region_name=region)
        logger.info(f"S3 service initialized for region: {region}")

    def list_buckets(self) -> BucketListResponse:
        """
        List S3 buckets.

        Returns:
            BucketListResponse containing:
            - Buckets: List of bucket dictionaries
            - Count: Number of buckets

        Raises:
            ClientError: If AWS API call fails
            Exception: For other unexpected errors
        """
        response = self.client.list_buckets()

        buckets: list[BucketInfo] = []
        for bucket in response.get("Buckets", []):
            bucket_info: BucketInfo = {
                "Name": bucket["Name"],
                "CreationDate": bucket["CreationDate"].isoformat(),
            }
            buckets.append(bucket_info)

        logger.info(f"Listed {len(buckets)} S3 buckets")
        result: BucketListResponse = {"Buckets": buckets, "Count": len(buckets)}
        return result
