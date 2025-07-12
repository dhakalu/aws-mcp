"""
Tests for the AWS MCP Server core functionality.
"""

from unittest.mock import Mock

import pytest

from aws_mcp.server import AWSSMCPServer, create_server


class TestAWSSMCPServer:
    """Test cases for AWSSMCPServer class."""

    def test_server_initialization(self):
        """Test server initialization with default region."""
        server = AWSSMCPServer()
        assert server.region == "us-east-1"
        assert server.handlers == {}

    def test_server_initialization_with_region(self):
        """Test server initialization with custom region."""
        server = AWSSMCPServer(region="eu-west-1")
        assert server.region == "eu-west-1"

    def test_register_handler(self):
        """Test registering a service handler."""
        server = AWSSMCPServer()
        mock_handler = Mock()

        server.register_handler("ec2", mock_handler)
        assert "ec2" in server.handlers
        assert server.handlers["ec2"] == mock_handler

    @pytest.mark.asyncio
    async def test_handle_request(self):
        """Test handling an MCP request."""
        server = AWSSMCPServer()
        request = {"action": "test", "service": "ec2"}

        response = await server.handle_request(request)
        assert response["status"] == "success"

    def test_create_server_factory(self):
        """Test the create_server factory function."""
        server = create_server()
        assert isinstance(server, AWSSMCPServer)
        assert server.region == "us-east-1"

        server_with_region = create_server(region="ap-southeast-1")
        assert server_with_region.region == "ap-southeast-1"
