# MCP client forOpenAI

This repository implements an OpenAI LLM application for Model Context Protocol (MCP), demonstrating how to build AI applications that leverage OpenAI's capabilities through the MCP standard.

The Model Context Protocol (MCP) is an open protocol that enables seamless integration between LLM applications and external data sources and tools. Whether you're building an AI-powered IDE, enhancing a chat interface, or creating custom AI workflows, MCP provides a standardized way to connect LLMs with the context they need.

## Project Structure

```
src/test_mcp_openai/
├── __init__.py
├── mcp_client.py     # MCP client implementation for OpenAI integration
├── openai_agent.py   # OpenAI LLM agent implementation
├── openai_tools.py   # Tool definitions and handlers for the OpenAI agent
└── run.py           # Example implementation and usage
```

## Features

- OpenAI LLM integration with MCP standard
- Tool and context management for OpenAI models
- Structured messaging system for LLM interactions
- Environment-based configuration
- Extensible design for custom tools and contexts

## Prerequisites

- Python 3.8+
- OpenAI API key
- uv package manager

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/test-mcp-openai.git
cd test-mcp-openai
```

2. Create and activate a virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies using uv:
```bash
uv pip install -r pyproject.toml
```

4. Set up environment variables:
Create a `.env` file in the root directory with:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

1. Configure your OpenAI API key in the `.env` file

2. Run the application:
```bash
python -m src.test_mcp_openai.run
```

## Configuration

The application uses environment variables for configuration:
- `OPENAI_API_KEY`: Your OpenAI API key
