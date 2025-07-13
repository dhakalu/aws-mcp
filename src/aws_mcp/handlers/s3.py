"""
S3 handlers for AWS Model Context Protocol (MCP) Server.

This module bridges the MCP server with AWS S3 service functionalities, providing error
handling and response formatting for various S3 operations.
"""

import json
import logging

from aws_mcp.service.s3 import S3Service

logger = logging.getLogger(__name__)


async def list_s3_buckets(region: str = "us-east-1") -> str:
    """List S3 buckets"""
    try:
        service = S3Service(region)
        result = service.list_buckets()

        buckets = result["Buckets"]
        if not buckets:
            return json.dumps(
                {
                    "Error": False,
                    "Message": f"No S3 buckets found in {region}",
                    "Buckets": [],
                    "Count": 0,
                    "Region": region,
                }
            )

        return json.dumps(
            {
                "Error": False,
                "Buckets": buckets,
                "Count": result["Count"],
                "Region": region,
            }
        )

    except Exception as e:
        logger.error(f"Error in list_s3_buckets: {e}")
        return json.dumps(
            {
                "Error": True,
                "Message": f"Error listing S3 buckets: {str(e)}",
                "Buckets": [],
                "Count": 0,
                "Region": region,
            }
        )
