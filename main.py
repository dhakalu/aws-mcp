#!/usr/bin/env python3
"""
AWS MCP Server - Entry point for the Model Context Protocol server.

This script starts the AWS MCP server that enables AI assistants to interact
with AWS services through natural language commands.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src directory to Python path for development
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from aws_mcp.server import run
from aws_mcp.utils import AWSAuth, get_default_region, setup_logging


async def main() -> None:
    """Main entry point for the AWS MCP Server."""
    setup_logging("INFO")
    logger = logging.getLogger(__name__)
    
    try:
        # Get AWS region
        region = get_default_region()
        logger.info(f"Starting AWS MCP Server for region: {region}")
        
        # Validate AWS credentials
        if not AWSAuth.validate_credentials():
            logger.error("AWS credentials not found or invalid. Please configure your credentials.")
            logger.error("Use 'aws configure' or set environment variables.")
            sys.exit(1)
        
        # Start the MCP server using stdio transport
        logger.info("AWS MCP Server starting...")
        await run()
        
    except Exception as e:
        logger.error(f"Failed to start AWS MCP Server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
