# ASCII Canvas AI

An intelligent system design diagram generator powered by dual AI agents. Transform natural language descriptions of your application or system into beautiful ASCII art architecture diagrams.

## Overview

ASCII Canvas AI uses two specialized AI agents working in tandem:

1. **Design Recommender Agent** - Analyzes your system description and creates a comprehensive architectural design with components, connections, and best practices
2. **ASCII Artist Agent** - Transforms the system design into a beautiful, professional ASCII art diagram

## Features

- 🤖 **Dual AI Agent System** - Specialized agents for design and visualization
- 📝 **Natural Language Input** - Describe your system in plain English
- 🎨 **Multiple Diagram Styles** - Choose from detailed, compact, or flowchart styles
- 🔄 **Iterative Refinement** - Refine designs based on feedback
- 💾 **Export Diagrams** - Save diagrams as text files
- 🎯 **Interactive & Batch Modes** - Use interactively or process files in batch
- ⚡ **Fallback Support** - Automatic fallback between AI providers

## Installation

### Prerequisites

- Python 3.10 or higher
- OpenAI API key (required)
- Anthropic API key (optional, for best ASCII art quality)

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

You'll be guided through:
1. Describing your system
2. Reviewing the generated design
3. Optionally refining the design
4. Choosing a diagram style
5. Viewing and saving the ASCII diagram

### Batch Mode

Process a description file and generate a diagram:

```bash
python src/main.py examples/ecommerce.txt output.txt
```

Or print to stdout:

```bash
python src/main.py examples/ecommerce.txt
```

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

## Project Structure

```
ascii-canvas-ai/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Main CLI application
│   └── agents/
│       ├── __init__.py
│       ├── design_recommender.py  # Design AI agent
│       └── ascii_artist.py        # ASCII art AI agent
├── tests/                      # Test files
├── examples/                   # Example input files
├── outputs/                    # Generated diagrams (auto-created)
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY` - Required for design generation
- `ANTHROPIC_API_KEY` - Optional, recommended for best ASCII art quality
- `DESIGN_MODEL` - OpenAI model to use (default: gpt-4)
- `ASCII_MODEL` - Claude model to use (default: claude-3-opus-20240229)

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

The system uses a pipeline architecture:

```
User Input → Design Agent → System Design → ASCII Agent → ASCII Diagram
                ↑                              ↑
                └── Refinement Loop ───────────┘
```

Each agent is independently configurable and can use different AI models optimized for their specific tasks.

## Contributing

Contributions are welcome! Areas for improvement:

- Additional diagram styles
- Support for more AI providers
- Export to other formats (SVG, PNG)
- Web interface
- Design templates library
- Multi-language support

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

## Credits

Built with:
- [OpenAI API](https://openai.com/) - Design generation
- [Anthropic Claude](https://anthropic.com/) - ASCII art generation
- [Rich](https://rich.readthedocs.io/) - Beautiful terminal output
- [Pydantic](https://pydantic.dev/) - Data validation

---

**ASCII Canvas AI** - Transform ideas into visual architecture
