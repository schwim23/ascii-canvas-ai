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

# Batch mode with input file
python src/main.py examples/ecommerce.txt

# Batch mode with output file
python src/main.py examples/ecommerce.txt output.txt
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

ASCII Canvas AI is a **dual-agent system** that generates system architecture diagrams from natural language descriptions. The architecture follows a sequential pipeline pattern where each agent has a specialized role.

### Core Architecture Pattern

```
User Description → Design Agent → System Design (Pydantic) → ASCII Agent → ASCII Diagram
                        ↑                                         ↑
                        └─────── Refinement Loop ─────────────────┘
```

### Agent System

The application uses two specialized AI agents that work sequentially:

1. **Design Recommender Agent** (`src/agents/design_recommender.py`)
   - **Model**: OpenAI GPT-4 (configurable via `DESIGN_MODEL` env var)
   - **Role**: Analyzes natural language system descriptions and creates structured architectural designs
   - **Output**: Pydantic `SystemDesign` object containing:
     - Components (name, type, description)
     - Connections (from/to, connection type, description)
     - Architectural notes
   - **Key Method**: `recommend_design(user_description)` → `SystemDesign`
   - **Refinement**: `refine_design(current_design, feedback)` → `SystemDesign`

2. **ASCII Artist Agent** (`src/agents/ascii_artist.py`)
   - **Model**: Anthropic Claude Opus (configurable via `ASCII_MODEL` env var)
   - **Role**: Converts structured system designs into visual ASCII art diagrams
   - **Styles**: Supports "detailed", "compact", and "flowchart" styles
   - **Fallback**: Automatically falls back to OpenAI GPT-4 if Anthropic API unavailable
   - **Key Method**: `create_ascii_diagram(system_design_dict, style)` → `str`

### Data Models (Pydantic)

The system uses strongly-typed Pydantic models for validation and structure:

- **`SystemComponent`**: Represents individual architecture components (services, databases, APIs, etc.)
- **`Connection`**: Represents connections between components with types (http, grpc, async, etc.)
- **`SystemDesign`**: Complete design containing title, description, components, connections, and notes

These models serve as the contract between the two agents and ensure data consistency.

### Main Application Flow (`src/main.py`)

**Interactive Mode** (default):
1. Display banner and initialize both agents
2. Get multiline system description from user
3. Call Design Agent to generate `SystemDesign`
4. Display design to user with option to refine
5. If refinement requested, loop back to Design Agent
6. Call ASCII Agent with user's chosen style
7. Display diagram with option to save to `outputs/` directory

**Batch Mode** (with file argument):
- Reads system description from file
- Skips interactive prompts
- Outputs diagram to file or stdout

### Error Handling Strategy

- **API Key Validation**: Checks for `OPENAI_API_KEY` before initialization
- **Anthropic Fallback**: If Anthropic API fails, automatically retries with OpenAI
- **Model Configuration**: Both models are configurable via environment variables for flexibility

### File Organization

```
src/
├── main.py                      # CLI application, user interaction, orchestration
└── agents/
    ├── design_recommender.py    # OpenAI-based design generation
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
- `ASCII_MODEL`: Override default Claude model (default: claude-sonnet-4-5))

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
