# AWS MCP Server

A Model Context Protocol (MCP) server that provides AWS SDK functionality through boto3, enabling AI assistants and chatbots to interact with AWS services seamlessly.

## Overview

This project implements the Model Context Protocol for AWS services, allowing AI assistants like Claude, ChatGPT, and other compatible chatbots to perform AWS operations through a standardized interface. By bridging the gap between conversational AI and cloud infrastructure, users can manage their AWS resources using natural language commands.

## What is Model Context Protocol (MCP)?

Model Context Protocol is a standard for connecting AI assistants with external systems and data sources. It provides a secure, structured way for AI models to access and interact with external services while maintaining proper authentication and authorization.

## Features

🚀 **Planned Features:**
- **EC2 Management**: Start, stop, and monitor EC2 instances
- **S3 Operations**: Upload, download, and manage S3 objects and buckets
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
uv install -e .
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

Once configured, you can interact with AWS services through natural language:

### EC2 Operations
- "List all my EC2 instances"
- "Start the instance named 'web-server'"
- "Show me the status of instance i-1234567890abcdef0"

### S3 Operations
- "Upload file.txt to my-bucket"
- "List all files in my-documents bucket"
- "Download report.pdf from analytics-bucket"

### Lambda Functions
- "Invoke the data-processor function with this payload"
- "Show me the logs for the last execution of my-lambda"

### CloudWatch
- "Show CPU utilization for my EC2 instances"
- "Get error logs from the last hour"

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
│   │       ├── auth.py  # AWS authentication
│   │       └── helpers.py
└── tests/
    └── ...
```

### Running in Development

```bash
# Install in development mode
uv pip install -e ".[dev]"

# Run tests
pytest

# Run the MCP server
python main.py
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

- [ ] Core MCP server implementation
- [ ] EC2 service integration
- [ ] S3 service integration
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