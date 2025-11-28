# ASCII Canvas AI

An intelligent system design diagram generator powered by multiple AI agents. Transform natural language descriptions OR automatically scan your AWS infrastructure to generate beautiful ASCII art architecture diagrams.

## Overview

ASCII Canvas AI uses three specialized agents working together:

1. **Design Recommender Agent** - Analyzes your system description and creates a comprehensive architectural design with components, connections, and best practices
2. **AWS Scanner Agent** ⭐ NEW - Automatically discovers and maps your AWS infrastructure using AWS CLI
3. **ASCII Artist Agent** - Transforms the system design into a beautiful, professional ASCII art diagram

## Features

- 🤖 **Multi-Agent System** - Specialized agents for design, AWS scanning, and visualization
- 📝 **Natural Language Input** - Describe your system in plain English
- ☁️ **AWS Infrastructure Scanning** ⭐ NEW - Automatically discover and diagram your AWS architecture
- 🎨 **Multiple Diagram Styles** - Choose from detailed, compact, or flowchart styles
- 🔄 **Iterative Refinement** - Refine designs based on feedback
- 💾 **Export Diagrams** - Save diagrams as text files
- 🎯 **Interactive & Batch Modes** - Use interactively or process files in batch
- ⚡ **Fallback Support** - Automatic fallback between AI providers
- 🔐 **Smart AWS Authentication** - Guided setup for AWS CLI and SSO

## Installation

### Prerequisites

- Python 3.10 or higher
- OpenAI API key (required)
- Anthropic API key (optional, for best ASCII art quality)
- AWS CLI (optional, required only for AWS scanning feature)

### Setup

1. Clone or navigate to the project directory:
```bash
cd ascii-canvas-ai
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

## Usage

### Interactive Mode

Run the application without arguments to enter interactive mode:

```bash
python src/main.py
```

You'll be prompted to choose:
- **Option 1: Describe Manually** - Enter a text description of your system
- **Option 2: Scan AWS Account** - Automatically discover your AWS infrastructure

#### Manual Description Flow:
1. Enter your system description
2. Review the generated design
3. Optionally refine the design
4. Choose a diagram style
5. View and save the ASCII diagram

#### AWS Scanning Flow:
1. System checks AWS CLI installation and authentication
2. Guided authentication setup if needed
3. Select AWS region to scan
4. Automatic discovery of AWS resources:
   - EC2 instances
   - RDS databases
   - Lambda functions
   - S3 buckets
   - Load Balancers (ALB/NLB)
   - SQS queues
   - ElastiCache clusters
   - API Gateway
   - ECS services
5. Automatic connection inference based on AWS patterns
6. Choose a diagram style
7. View and save the ASCII diagram

### Batch Mode

Process a description file and generate a diagram:

```bash
python src/main.py examples/ecommerce.txt output.txt
```

Or print to stdout:

```bash
python src/main.py examples/ecommerce.txt
```

### AWS CLI Setup (for AWS Scanning)

If you want to use the AWS scanning feature, you need AWS CLI installed and configured:

```bash
# Install AWS CLI
# macOS:
brew install awscli

# Configure with IAM credentials:
aws configure

# OR configure with SSO:
aws configure sso
aws sso login

# Verify authentication:
aws sts get-caller-identity
```

The application will guide you through authentication if you're not already logged in.

## Examples

### Example 1: E-commerce Platform

**Input:**
```
I need a scalable e-commerce platform that handles product browsing,
shopping cart, payment processing, and order management. It should
support high traffic and integrate with third-party payment providers.
```

**Output:**
The system generates a comprehensive design with:
- Frontend (web/mobile)
- API Gateway
- Microservices (Product, Cart, Payment, Order)
- Databases (Product DB, Order DB)
- Message Queue for async processing
- Cache layer for performance
- Payment Gateway integration

### Example 2: Social Media Application

**Input:**
```
Design a social media app where users can post content, follow other users,
comment on posts, and receive real-time notifications. It needs to scale
to millions of users.
```

**Output:**
Architecture including:
- User service
- Post service
- Feed generation service
- Notification service
- WebSocket server for real-time updates
- CDN for media storage
- Redis cache
- Database sharding strategy

### Example 3: AWS Infrastructure Scan ⭐ NEW

**Input:**
Choose "Scan AWS Account" and authenticate

**Output:**
Automatic discovery and visualization of:
- All EC2 instances (running)
- RDS databases
- Lambda functions
- S3 buckets
- Load balancers
- Message queues (SQS)
- Cache clusters (ElastiCache)
- API Gateways
- ECS services

Connections are automatically inferred based on common AWS architecture patterns (e.g., Load Balancer → EC2, Service → Database, API Gateway → Lambda).

## Project Structure

```
ascii-canvas-ai/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Main CLI application
│   └── agents/
│       ├── __init__.py
│       ├── design_recommender.py  # Design AI agent
│       ├── aws_scanner.py         # AWS infrastructure scanner ⭐ NEW
│       └── ascii_artist.py        # ASCII art AI agent
├── tests/                      # Test files
├── examples/                   # Example input files
├── outputs/                    # Generated diagrams (auto-created)
├── requirements.txt
├── .env.example
├── .gitignore
├── WARP.md
└── README.md
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY` - Required for design generation
- `ANTHROPIC_API_KEY` - Optional, recommended for best ASCII art quality
- `DESIGN_MODEL` - OpenAI model to use (default: gpt-4o)
- `ASCII_MODEL` - Claude model to use (default: claude-sonnet-4-5-20250929)

### Diagram Styles

- **detailed** - Spacious layout with comprehensive labels and boxes
- **compact** - Space-efficient design fitting in ~80 characters
- **flowchart** - Flow-oriented diagram showing data/request paths

## API Reference

### DesignRecommenderAgent

```python
from agents.design_recommender import DesignRecommenderAgent

agent = DesignRecommenderAgent()
design = agent.recommend_design("Your system description here")
refined = agent.refine_design(design, "Your feedback here")
```

### AwsScannerAgent ⭐ NEW

```python
from agents.aws_scanner import AwsScannerAgent

agent = AwsScannerAgent(region="us-east-1")
if agent.scan_aws_infrastructure():
    design = agent.convert_to_system_design()
```

### AsciiArtistAgent

```python
from agents.ascii_artist import AsciiArtistAgent

agent = AsciiArtistAgent()
diagram = agent.create_ascii_diagram(design.model_dump(), style="detailed")
refined_diagram = agent.refine_diagram(diagram, design.model_dump(), "Your feedback")
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

This project follows PEP 8 guidelines. Format code with:

```bash
black src/
```

## Architecture

The system uses a flexible pipeline architecture with two input methods:

**Manual Description:**
```
User Input → Design Agent → System Design → ASCII Agent → ASCII Diagram
                ↑                              ↑
                └── Refinement Loop ───────────┘
```

**AWS Infrastructure Scanning:** ⭐ NEW
```
AWS Account → AWS Scanner → System Design → ASCII Agent → ASCII Diagram
            (AWS CLI)                          ↑
```

Each agent is independently configurable and optimized for their specific tasks. The AWS Scanner uses AWS CLI commands (not AI) to discover infrastructure, while the Design Agent uses AI for interpretation of descriptions.

## Contributing

Contributions are welcome! Areas for improvement:

- Additional diagram styles
- Support for more AI providers
- Support for more cloud providers (Azure, GCP)
- Enhanced connection inference for AWS resources
- Export to other formats (SVG, PNG)
- Web interface
- Design templates library
- Multi-language support
- Terraform/CloudFormation file parsing

## License

MIT License - see LICENSE file for details

## Troubleshooting

### API Key Errors

Ensure your `.env` file contains valid API keys:
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Import Errors

Make sure you've installed all dependencies:
```bash
pip install -r requirements.txt
```

### ASCII Art Quality

For best results, use the Anthropic API (Claude models). If unavailable, the system will automatically fall back to OpenAI.

### AWS Scanning Issues

**AWS CLI not found:**
```bash
# Install AWS CLI
brew install awscli  # macOS
# or visit https://aws.amazon.com/cli/
```

**Authentication errors:**
```bash
# Configure credentials
aws configure
# or for SSO
aws sso login
```

**No resources found:**
- Ensure you're scanning the correct region
- Verify you have read permissions for AWS services
- Check that resources exist and are in "running" state

## Credits

Built with:
- [OpenAI API](https://openai.com/) - Design generation
- [Anthropic Claude](https://anthropic.com/) - ASCII art generation
- [Rich](https://rich.readthedocs.io/) - Beautiful terminal output
- [Pydantic](https://pydantic.dev/) - Data validation

---

**ASCII Canvas AI** - Transform ideas into visual architecture
