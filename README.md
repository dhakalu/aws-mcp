# AWS MCP Server

[![CI](https://github.com/dhakalu/aws-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/dhakalu/aws-mcp/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/dhakalu/aws-mcp/branch/main/graph/badge.svg)](https://codecov.io/gh/dhakalu/aws-mcp)
[![PyPI version](https://badge.fury.io/py/aws-mcp.svg)](https://badge.fury.io/py/aws-mcp)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server that provides AWS SDK functionality through boto3, enabling AI assistants and chatbots to interact with AWS services seamlessly.

## Overview

This project implements the Model Context Protocol for AWS services, allowing AI assistants like Claude, ChatGPT, and other compatible chatbots to perform AWS operations through a standardized interface. By bridging the gap between conversational AI and cloud infrastructure, users can manage their AWS resources using natural language commands.

## What is Model Context Protocol (MCP)?

Model Context Protocol is a standard for connecting AI assistants with external systems and data sources. It provides a secure, structured way for AI models to access and interact with external services while maintaining proper authentication and authorization.

## Features

🚀 **Current Features:**
- **MCP Protocol Support**: Full Model Context Protocol server implementation
- **EC2 Management**: List and describe EC2 instances
- **S3 Operations**: List S3 buckets in your account
- **AWS Authentication**: Secure credential validation and management
- **Tool-based Interface**: Structured tools for AI assistant integration

🔧 **Implemented Tools:**
- `list_ec2_instances`: List EC2 instances with optional state filtering
- `describe_ec2_instance`: Get detailed information about a specific EC2 instance
- `list_s3_buckets`: List S3 buckets in the specified region

🚀 **Planned Features:**
- **S3 Object Operations**: Upload, download, and manage S3 objects
- **Lambda Functions**: Deploy and invoke Lambda functions
- **CloudWatch Monitoring**: Query metrics and logs
- **IAM Management**: Manage users, roles, and policies
- **RDS Operations**: Database management and monitoring
- **CloudFormation**: Stack management and deployment
- **Security Groups**: Network security configuration
- **Route 53**: DNS management
- **Cost and Billing**: Usage monitoring and cost analysis

## Installation

```bash
# Clone the repository
git clone https://github.com/dhakalu/aws-mcp.git
cd aws-mcp

# Install dependencies
uv sync
```

## Configuration

### AWS Credentials

Ensure your AWS credentials are configured using one of the following methods:

1. **AWS CLI Configuration**:
   ```bash
   aws configure
   ```

2. **Environment Variables**:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_DEFAULT_REGION=us-east-1
   ```

3. **IAM Roles** (for EC2 instances)

### MCP Client Configuration

Add this server to your MCP-compatible client configuration:

```json
{
  "servers": {
    "aws-mcp": {
      "command": "python",
      "args": ["/path/to/aws-mcp/main.py"],
      "env": {
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

## Usage Examples

Once configured, you can interact with AWS services through natural language via MCP-compatible clients:

### Available Tools

#### EC2 Operations
- **list_ec2_instances**: "List all my EC2 instances" or "Show running instances"
  - Optional parameter: `state` (running, stopped, pending, terminated, all)
  - Optional parameter: `region` (defaults to us-east-1)
- **describe_ec2_instance**: "Show details for instance i-1234567890abcdef0"
  - Required parameter: `instance_id`
  - Optional parameter: `region` (defaults to us-east-1)

#### S3 Operations  
- **list_s3_buckets**: "List all my S3 buckets" or "Show me my buckets"
  - Optional parameter: `region` (defaults to us-east-1)

### Example Tool Calls

```json
{
  "tool": "list_ec2_instances",
  "arguments": {
    "state": "running",
    "region": "us-east-1"
  }
}
```

```json
{
  "tool": "describe_ec2_instance", 
  "arguments": {
    "instance_id": "i-1234567890abcdef0",
    "region": "us-east-1"
  }
}
```

```json
{
  "tool": "list_s3_buckets",
  "arguments": {
    "region": "us-east-1"
  }
}
```

## Security Considerations

- **Principle of Least Privilege**: Ensure your AWS credentials have only the minimum required permissions
- **Credential Security**: Never commit AWS credentials to version control
- **Network Security**: Use VPC endpoints and security groups appropriately
- **Audit Logging**: Enable CloudTrail for comprehensive audit logging
- **Resource Limits**: Consider implementing resource usage limits to prevent accidental over-provisioning

## Development

### Project Structure

```
aws-mcp/
├── main.py              # MCP server entry point
├── pyproject.toml       # Project configuration
├── README.md           # This file
├── src/
│   ├── aws_mcp/
│   │   ├── __init__.py
│   │   ├── server.py    # MCP server implementation
│   │   ├── handlers/    # AWS service handlers
│   │   │   ├── ec2.py
│   │   │   ├── s3.py
│   │   │   ├── lambda_.py
│   │   │   └── ...
│   │   └── utils/
│   │       └── auth.py  # AWS authentication
└── tests/
    └── ...
```

### Running in Development

```bash
# Install in development mode
uv sync --extra dev

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=aws_mcp

# Run linting and formatting
uv run ruff check src/ tests/
uv run black --check src/ tests/
uv run mypy src/

# Run the MCP server
uv run main.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new functionality
- Update documentation for new features
- Ensure proper error handling and logging
- Use type hints throughout the codebase

### Code Quality

The project uses several tools to maintain code quality:

```bash
# Format imports and code
uv run isort src/ tests/
uv run black src/ tests/

# Lint code
uv run ruff check src/ tests/

# Type checking
uv run mypy src/

# Run all quality checks
uv run ruff check src/ tests/ && \
uv run black --check src/ tests/ && \
uv run isort --check-only src/ tests/ && \
uv run mypy src/
```

All pull requests must pass the CI pipeline which includes:
- ✅ Code formatting (Black, isort)
- ✅ Linting (Ruff)
- ✅ Type checking (MyPy)
- ✅ Tests (pytest with coverage)
- ✅ Security scanning (safety, bandit)
- ✅ Package building and installation tests

## Requirements

- Python 3.13+
- boto3
- Valid AWS credentials
- MCP-compatible client (Claude Desktop, etc.)

## Supported AWS Regions

This MCP server supports all AWS regions where the required services are available. Configure your preferred region through environment variables or AWS credentials.

## Error Handling

The server implements comprehensive error handling for:
- AWS API errors and rate limiting
- Authentication and authorization issues
- Network connectivity problems
- Invalid resource requests
- MCP protocol errors

## Logging

Detailed logging is available for troubleshooting:
- AWS API calls and responses
- MCP protocol messages
- Error conditions and stack traces
- Performance metrics

## Roadmap

- [x] Core MCP server implementation
- [x] EC2 service integration (list, describe)
- [x] S3 service integration (list buckets)
- [x] AWS authentication and credential validation
- [x] Tool-based interface for AI assistants
- [ ] EC2 instance control (start, stop, reboot)
- [ ] S3 object operations (upload, download, delete)
- [ ] Lambda service integration
- [ ] CloudWatch integration
- [ ] IAM management features
- [ ] RDS operations
- [ ] CloudFormation support
- [ ] Advanced security features
- [ ] Performance optimizations
- [ ] Comprehensive documentation
- [ ] Example integrations

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: [dhakal.upenn@gmail.com]
- 🐛 Issues: [GitHub Issues](https://github.com/dhakalu/aws-mcp/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/dhakalu/aws-mcp/discussions)

## Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) for the standardization
- [AWS SDK for Python (Boto3)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- The open-source community for inspiration and contributions

---

**Disclaimer**: This project is not officially affiliated with Amazon Web Services. AWS is a trademark of Amazon.com, Inc. or its affiliates.