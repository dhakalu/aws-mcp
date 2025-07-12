"""
Tests for the AWS MCP Server core functionality.
"""

from aws_mcp.server import AWSSMCPServer


class TestAWSSMCPServer:
    """Test cases for AWSSMCPServer class."""

    def test_server_initialization_default(self):
        """Test server initialization with default region."""
        server = AWSSMCPServer()
        assert server.region == "us-east-1"

    def test_server_initialization_with_region(self, monkeypatch):
        """Test server initialization with custom region."""
        monkeypatch.setenv("AWS_REGION", "eu-west-1")
        server = AWSSMCPServer()
        assert server.region == "eu-west-1"
