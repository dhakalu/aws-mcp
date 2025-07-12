"""
Helper utilities for the AWS MCP Server.

This module contains common utility functions and helpers used throughout
the MCP server implementation.
"""

import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO") -> None:
    """
    Set up logging configuration for the MCP server.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger.info(f"Logging initialized at {level} level")


def validate_aws_resource_name(name: str, resource_type: str) -> bool:
    """
    Validate AWS resource names according to AWS naming conventions.

    Args:
        name: Resource name to validate
        resource_type: Type of AWS resource (e.g., 's3', 'ec2', 'lambda')

    Returns:
        True if name is valid, False otherwise
    """
    if not name:
        return False

    # S3 bucket naming rules
    if resource_type == "s3":
        return (
            3 <= len(name) <= 63
            and bool(re.match(r"^[a-z0-9.-]+$", name))
            and not name.startswith(".")
            and not name.endswith(".")
            and ".." not in name
        )

    # Lambda function naming rules
    elif resource_type == "lambda":
        return 1 <= len(name) <= 64 and bool(re.match(r"^[a-zA-Z0-9-_]+$", name))

    # EC2 instance name (tag value)
    elif resource_type == "ec2":
        return len(name) <= 255  # EC2 tag values can be up to 255 characters

    # Default validation
    return bool(re.match(r"^[a-zA-Z0-9-_]+$", name))


def parse_s3_uri(s3_uri: str) -> Optional[Dict[str, str]]:
    """
    Parse an S3 URI into bucket and key components.

    Args:
        s3_uri: S3 URI in format s3://bucket/key

    Returns:
        Dictionary with 'bucket' and 'key' if valid, None otherwise
    """
    match = re.match(r"^s3://([^/]+)/(.+)$", s3_uri)
    if match:
        return {"bucket": match.group(1), "key": match.group(2)}
    return None


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string (e.g., "1.5 KB", "2.3 MB")
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    size_index = 0
    size = float(size_bytes)

    while size >= 1024.0 and size_index < len(size_names) - 1:
        size_index += 1
        size /= 1024.0

    return f"{size:.1f} {size_names[size_index]}"


def format_datetime(dt: Union[str, datetime]) -> str:
    """
    Format datetime for consistent display.

    Args:
        dt: Datetime string or datetime object

    Returns:
        Formatted datetime string
    """
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except ValueError:
            return dt

    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def sanitize_for_json(obj: Any) -> Any:
    """
    Sanitize object for JSON serialization.

    Args:
        obj: Object to sanitize

    Returns:
        JSON-serializable object
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, "__dict__"):
        return {k: sanitize_for_json(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    else:
        return obj


def extract_instance_id(instance_ref: str) -> Optional[str]:
    """
    Extract instance ID from various reference formats.

    Args:
        instance_ref: Instance reference (ID, name, or description)

    Returns:
        Instance ID if found, None otherwise
    """
    # Direct instance ID
    if re.match(r"^i-[0-9a-f]{8,17}$", instance_ref):
        return instance_ref

    # TODO: Implement name-to-ID lookup when boto3 is available
    return None


def build_error_response(
    error_type: str, message: str, details: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Build standardized error response.

    Args:
        error_type: Type of error (e.g., 'ValidationError', 'AWSError')
        message: Error message
        details: Optional additional error details

    Returns:
        Standardized error response dictionary
    """
    response = {
        "error": {
            "type": error_type,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        }
    }

    if details:
        response["error"]["details"] = details

    return response


def build_success_response(data: Any, message: Optional[str] = None) -> Dict[str, Any]:
    """
    Build standardized success response.

    Args:
        data: Response data
        message: Optional success message

    Returns:
        Standardized success response dictionary
    """
    response = {
        "success": True,
        "data": sanitize_for_json(data),
        "timestamp": datetime.utcnow().isoformat(),
    }

    if message:
        response["message"] = message

    return response
