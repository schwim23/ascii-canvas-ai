# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Commands

### Setup & Installation
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env to add OPENAI_API_KEY (required) and ANTHROPIC_API_KEY (optional)
```

### Running the Application
```bash
# Interactive mode (primary usage)
python src/main.py

# Interactive mode will prompt you to choose:
# 1. Describe manually - Enter text description of your system
# 2. Scan AWS account - Automatically discover AWS infrastructure

# Batch mode with input file
python src/main.py examples/ecommerce.txt

# Batch mode with output file
python src/main.py examples/ecommerce.txt output.txt
```

### AWS CLI Setup (for AWS Scanning)
```bash
# Install AWS CLI (if not already installed)
# macOS:
brew install awscli
# Linux/Windows: https://aws.amazon.com/cli/

# Configure AWS credentials (Option 1: IAM credentials)
aws configure
# You'll need: Access Key ID, Secret Access Key, Region

# Configure AWS credentials (Option 2: SSO)
aws configure sso
aws sso login

# Verify authentication
aws sts get-caller-identity
```

### Testing & Code Quality
```bash
# Run tests
pytest tests/

# Format code (PEP 8)
black src/

# Note: Currently no tests exist in tests/ directory
```

## Architecture Overview

ASCII Canvas AI is a **multi-agent system** that generates system architecture diagrams from either natural language descriptions or by automatically scanning AWS infrastructure. The architecture follows a sequential pipeline pattern where each agent has a specialized role.

### Core Architecture Patterns

**Pattern 1: Manual Description**
```
User Description → Design Agent → System Design (Pydantic) → ASCII Agent → ASCII Diagram
                        ↑                                         ↑
                        └─────── Refinement Loop ─────────────────┘
```

**Pattern 2: AWS Infrastructure Scanning**
```
AWS Account → AWS Scanner Agent → System Design (Pydantic) → ASCII Agent → ASCII Diagram
              (AWS CLI)                                        ↑
```

### Agent System

The application uses three specialized agents:

1. **Design Recommender Agent** (`src/agents/design_recommender.py`)
   - **Model**: OpenAI GPT-4 (configurable via `DESIGN_MODEL` env var)
   - **Role**: Analyzes natural language system descriptions and creates structured architectural designs
   - **Output**: Pydantic `SystemDesign` object containing:
     - Components (name, type, description)
     - Connections (from/to, connection type, description)
     - Architectural notes
   - **Key Method**: `recommend_design(user_description)` → `SystemDesign`
   - **Refinement**: `refine_design(current_design, feedback)` → `SystemDesign`

2. **AWS Scanner Agent** (`src/agents/aws_scanner.py`) ⭐ NEW
   - **Model**: None (uses AWS CLI commands, not AI-based)
   - **Role**: Discovers AWS infrastructure by executing AWS CLI commands and maps resources to SystemDesign
   - **Scanned Resources**:
     - EC2 instances → `service` components
     - RDS databases → `database` components
     - Lambda functions → `function` components
     - S3 buckets → `storage` components
     - Load Balancers (ALB/NLB) → `load_balancer` components
     - SQS queues → `queue` components
     - ElastiCache clusters → `cache` components
     - API Gateway → `api` components
     - ECS services → `service` components
   - **Connection Inference**: Automatically infers connections based on common AWS patterns
   - **Authentication**: Checks AWS CLI installation and guides users through authentication
   - **Key Methods**: 
     - `scan_aws_infrastructure()` → executes AWS CLI commands
     - `convert_to_system_design()` → `SystemDesign`

3. **ASCII Artist Agent** (`src/agents/ascii_artist.py`)
   - **Model**: Anthropic Claude Sonnet (configurable via `ASCII_MODEL` env var)
   - **Role**: Converts structured system designs into visual ASCII art diagrams
   - **Styles**: Supports "detailed", "compact", and "flowchart" styles
   - **Fallback**: Automatically falls back to OpenAI GPT-4o if Anthropic API unavailable
   - **Key Method**: `create_ascii_diagram(system_design_dict, style)` → `str`

### Data Models (Pydantic)

The system uses strongly-typed Pydantic models for validation and structure:

- **`SystemComponent`**: Represents individual architecture components (services, databases, APIs, etc.)
- **`Connection`**: Represents connections between components with types (http, grpc, async, etc.)
- **`SystemDesign`**: Complete design containing title, description, components, connections, and notes

These models serve as the contract between the two agents and ensure data consistency.

### Main Application Flow (`src/main.py`)

**Interactive Mode** (default):
1. Display banner and ask user to choose input method (describe manually or scan AWS)
2. **If Manual Description**:
   - Get multiline system description from user
   - Call Design Agent to generate `SystemDesign`
   - Display design to user with option to refine
   - If refinement requested, loop back to Design Agent
3. **If AWS Scan**:
   - Initialize AWS Scanner Agent
   - Check AWS CLI installation and authentication status
   - Guide user through authentication if needed
   - Scan AWS resources across multiple services
   - Convert discovered resources to `SystemDesign`
4. Call ASCII Agent with user's chosen style
5. Display diagram with option to save to `outputs/` directory

**Batch Mode** (with file argument):
- Reads system description from file
- Skips interactive prompts
- Outputs diagram to file or stdout

### Error Handling Strategy

- **API Key Validation**: Checks for `OPENAI_API_KEY` before initialization
- **Anthropic Fallback**: If Anthropic API fails, automatically retries with OpenAI
- **Model Configuration**: Both models are configurable via environment variables for flexibility
- **AWS CLI Validation**: Checks if AWS CLI is installed before scanning
- **AWS Authentication**: Verifies AWS authentication and guides users through setup if needed
- **Graceful Degradation**: AWS scanner handles missing permissions and empty accounts gracefully

### File Organization

```
src/
├── main.py                      # CLI application, user interaction, orchestration
└── agents/
    ├── design_recommender.py    # OpenAI-based design generation
    ├── aws_scanner.py           # AWS CLI-based infrastructure discovery
    └── ascii_artist.py          # Claude/OpenAI-based ASCII diagram generation
```

## Development Notes

### Adding New Agent Capabilities

When extending agent functionality:
- Both agents use structured prompts with clear role definitions
- Design Agent uses `response_format={"type": "json_object"}` for structured output
- ASCII Agent uses higher temperature (0.8) for creative output vs Design Agent (0.7)
- Always maintain backward compatibility with Pydantic models

### Environment Variables

Required:
- `OPENAI_API_KEY`: Used by Design Agent (always) and ASCII Agent (fallback)

Optional:
- `ANTHROPIC_API_KEY`: Used by ASCII Agent for better diagram quality
- `DESIGN_MODEL`: Override default OpenAI model (default: gpt-4o)
- `ASCII_MODEL`: Override default Claude model (default: claude-sonnet-4-5)

### Working with Diagrams

- All saved diagrams go to `outputs/` directory (auto-created)
- Diagrams are plain text files (.txt) for portability
- The three style options affect layout, density, and visual flow
- ASCII Agent uses Unicode box-drawing characters (─ │ ┌ ┐ └ ┘ etc.)

### Dependencies

Core dependencies (from requirements.txt):
- `openai>=1.0.0`: Design Agent and fallback for ASCII Agent
- `anthropic>=0.7.0`: Primary ASCII Agent model
- `pydantic>=2.0.0`: Type validation and data models
- `rich>=13.0.0`: Terminal UI (panels, prompts, colors)
- `python-dotenv>=1.0.0`: Environment configuration
- `boto3>=1.28.0`: AWS SDK (optional, currently using AWS CLI directly)

### AWS Scanning Details

The AWS Scanner Agent executes the following AWS CLI commands:
- `aws ec2 describe-instances` - Discovers EC2 instances
- `aws rds describe-db-instances` - Discovers RDS databases
- `aws lambda list-functions` - Discovers Lambda functions
- `aws s3api list-buckets` - Discovers S3 buckets
- `aws elbv2 describe-load-balancers` - Discovers ALB/NLB
- `aws sqs list-queues` - Discovers SQS queues
- `aws elasticache describe-cache-clusters` - Discovers ElastiCache
- `aws apigateway get-rest-apis` - Discovers API Gateway
- `aws ecs list-clusters` + `describe-services` - Discovers ECS services

**Connection Inference Logic**:
The scanner infers connections between components based on common AWS architecture patterns:
- Load Balancers → EC2/ECS services
- Services → Databases
- Services → Cache clusters
- Services → SQS queues
- API Gateway → Lambda functions
- Services → S3 storage

**Important Notes**:
- Only scans a single AWS region (configurable)
- Only includes running/active resources
- Connections are inferred, not derived from actual network analysis
- Requires appropriate IAM permissions for read-only access to AWS services
