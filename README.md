# MCP Development Agent

A development agent based on the Model Context Protocol (MCP) that provides memory management, documentation search, and Git/GitHub integration features, available both as a CLI tool and as an SSE server.

## Features

- 🧠 **Memory System**: Store and retrieve information using embeddings via ChromaDB
- 📚 **Documentation Search**: Search through documentation files
- 🔄 **Git Integration**: Query commit history and issues
- 🔍 **Code Analysis**: Static code analysis using tree-sitter
- 🌐 **GitHub Integration**: Search repositories, issues, pull requests, projects, and code
- 💡 **AI Assistant**: Automatic issue summarization using GPT
- 💻 **CLI Interface**: Interactive command-line interface
- 🌐 **Server Mode**: Server-Sent Events (SSE) support

## Requirements

- Python 3.x
- ChromaDB
- GitPython
- FastMCP
- PyGithub
- tree-sitter
- openai

## Installation

1. Clone the repository:

```bash
git clone [repository-url]
cd mcp-dev-agent
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables (copy .env.example to .env):

```bash
cp .env.example .env
# Edit .env with your API keys:
# - GITHUB_TOKEN
# - OPENAI_API_KEY
# - ANTHROPIC_API_KEY
```

4. Set up code parsers:

```bash
python setup_parsers.py
```

## Usage

The agent can be run in two modes:

### CLI Mode

```bash
python main.py --mode cli
```

Available commands:

#### Memory

- `/memory add <content>` - Add a new general memory
- `/memory get <query>` - Search existing memories
- `/memory repo add <content>` - Add a repository-specific memory
- `/memory repo get <query>` - Search repository-specific memories

#### Git and GitHub

- `/git commits [number]` - Show commit history (default: last 5)
- `/git issues` - List local repository issues
- `/git info` - Show detailed repository information
- `/git diff` - Show pending changes (staged and unstaged)
- `/github repo <owner/repo>` - Show repository details
- `/github issues <owner/repo> [state]` - List issues (state: open/closed)
- `/github prs <owner/repo> [state]` - List pull requests (state: open/closed)
- `/github project <org> <number>` - Show project information
- `/github summarize <owner/repo> <issue_number>` - Generate issue summary using GPT
- `/github search <query> [language]` - Search code on GitHub

#### Code Analysis

- `/code analyze <file> [language]` - Analyze code structure (functions, classes, imports)

#### Documentation

- `/docs <query>` - Search documentation
- `exit` - Exit CLI mode

### Advanced Features

#### Code Analysis

The system uses tree-sitter to analyze code in:

- Python
- JavaScript
- TypeScript

Analysis includes:

- Function and method extraction
- Class identification
- Import mapping
- Memory integration for context

#### GitHub Integration

- Detailed repository information
- Issue search and listing
- Pull request management
- GitHub Projects integration
- Code search with language filtering
- Enriched metadata
- Automatic issue summarization with GPT

#### Enhanced Memory System

- Support for different context types
- Enriched metadata
- Contextual search
- Temporal history
- Code analysis integration
- Automatic summary storage
- Git state contextualization

### Server Mode (SSE)

```bash
python main.py
# or
python main.py --mode server
```

The SSE server enables integration with other applications through the MCP protocol.

## Project Structure

```
.
├── main.py              # Application entry point
├── setup_parsers.py     # Code parser configuration
├── tools/
│   ├── memory_tool.py   # Memory management via ChromaDB
│   ├── doc_tool.py      # Documentation search
│   ├── git_tool.py      # Git integration
│   └── github_tool.py   # GitHub integration and code analysis
└── docs/
    └── api_reference.md # API reference documentation
```

## AI Model Configuration

The agent supports integration with Anthropic (Claude) and OpenAI (GPT-4 and GPT-3.5) AI models. To use these models, you need to:

1. Set up environment variables:

```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export OPENAI_API_KEY="your-openai-api-key"
```

2. The `.agent.json` file is already configured with:

- Claude-3 Opus as default model
- GPT-4 Turbo and GPT-3.5 Turbo support
- Response caching (24 hours)
- Interaction logging

### Model Parameters

You can adjust model parameters by editing the `.agent.json` file:

- `temperature`: Controls response creativity (0.0 to 1.0)
- `max_tokens`: Maximum tokens per response
- `top_p`: Controls response diversity
