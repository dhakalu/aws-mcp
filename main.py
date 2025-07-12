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

from aws_mcp.server import create_server, setup_logging
from aws_mcp.utils.auth import AWSAuth, get_default_region


async def main():
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
        
        # Create and configure the MCP server
        server = create_server(region=region)
        
        # TODO: Register service handlers when implemented
        # from aws_mcp.handlers.ec2 import EC2Handler
        # from aws_mcp.handlers.s3 import S3Handler
        # from aws_mcp.handlers.lambda_ import LambdaHandler
        # 
        # server.register_handler("ec2", EC2Handler(region))
        # server.register_handler("s3", S3Handler(region))
        # server.register_handler("lambda", LambdaHandler(region))
        
        # Start the server
        logger.info("AWS MCP Server starting...")
        await server.start()
        
        # Keep the server running
        logger.info("AWS MCP Server is running. Press Ctrl+C to stop.")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        
    except Exception as e:
        logger.error(f"Failed to start AWS MCP Server: {e}")
        sys.exit(1)
    
    finally:
        if 'server' in locals():
            await server.stop()
        logger.info("AWS MCP Server stopped")


if __name__ == "__main__":
    asyncio.run(main())
