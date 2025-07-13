"""
Handler package for AWS service integrations.

This package contains handlers that bridge the AWS Model Context Protocol (MCP) server
with various AWS services. Handlers are responsible for handling errors, mapping
and formatting responses for AWS service operations.
"""

from .ec2 import describe_ec2_instance, list_ec2_instances

__all__ = [
    "list_ec2_instances",
    "describe_ec2_instance",
]
