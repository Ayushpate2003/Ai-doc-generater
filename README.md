# AI Documentation Generator

An AI-powered code documentation generator that automatically analyzes repositories and creates comprehensive documentation using advanced language models. The system employs a multi-agent architecture to perform specialized code analysis and generate structured documentation.



## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Web Interface](#web-interface)
  - [CLI Commands](#cli-commands)
  - [Advanced Options](#advanced-options)
- [Configuration](#configuration)
- [Web Interface Guide](#web-interface-guide)
- [Troubleshooting](#troubleshooting)
- [Architecture](#architecture)
- [License](#license)

## Features

- **Web Interface**: Modern Streamlit-based GUI for easy interaction (CLI also available)
- **Multi-Agent Analysis**: Specialized AI agents for code structure, data flow, dependency, request flow, and API analysis
- **Automated Documentation**: Generates comprehensive README files with configurable sections
- **AI Assistant Configuration**: Automatically generates CLAUDE.md, AGENTS.md, and .cursor/rules/ files for AI coding assistants
- **GitLab Integration**: Automated analysis for GitLab projects with merge request creation
- **Concurrent Processing**: Parallel execution of analysis agents for improved performance
- **Flexible Configuration**: YAML-based configuration with environment variable overrides
- **Multiple LLM Support**: Works with any OpenAI-compatible API (OpenAI, OpenRouter, Ollama, etc.)
- **Local LLM Support**: Full Ollama integration for privacy-focused, offline operation
- **Observability**: Built-in monitoring with OpenTelemetry tracing and Langfuse integration

## Installation

### Prerequisites

- Python 3.11+ (recommended: 3.13)
- Git
- **One of the following**:
  - API access to an OpenAI-compatible LLM provider (OpenAI, OpenRouter, etc.)
  - Local Ollama installation for offline operation (recommended: mistral model)

1. Clone the repository:
```bash
git clone https://github.com/divar-ir/ai-doc-gen.git
cd ai-doc-gen
```

2. Install using uv (recommended):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

3. Or install with pip:
```bash
pip install -e .
```

### Option 1: Web Interface (Recommended)

1. Set up your environment:
```bash
# Copy and edit environment variables
cp .env.sample .env

# Copy and edit configuration (optional)
mkdir -p .ai
cp config_example.yaml .ai/config.yaml
```

2. Start the web interface:
```bash
streamlit run app.py
```

3. Open your browser at `http://localhost:8501` and use the intuitive GUI to:
   - Analyze repositories
   - Generate README files
   - Create AI assistant configurations
   - View system configuration

### Option 2: Command Line

```bash
# Analyze your repository
uv run src/main.py analyze --repo-path .

# Generate README documentation
uv run src/main.py generate readme --repo-path .

# Generate AI assistant configuration files (CLAUDE.md, AGENTS.md, .cursor/rules/)
uv run src/main.py generate ai-rules --repo-path .
```

Generated documentation will be saved to `.ai/docs/` directory, and AI configuration files will be placed in your repository root.

### Using Ollama (Local LLM)

For privacy-focused, offline operation:

1. Install Ollama:
```bash
# macOS
brew install ollama

# Start Ollama service
ollama serve
```

2. Download a model (mistral recommended for function calling support):
```bash
ollama pull mistral
```

3. Configure `.env` for Ollama:
```bash
# Analyzer Agent LLM
ANALYZER_LLM_MODEL=mistral
ANALYZER_LLM_BASE_URL=http://localhost:11434/v1
ANALYZER_LLM_MAX_TOKENS=4096
ANALYZER_LLM_TEMPERATURE=0.0

# Documenter Agent LLM  
DOCUMENTER_LLM_MODEL=mistral
DOCUMENTER_LLM_BASE_URL=http://localhost:11434/v1
DOCUMENTER_LLM_MAX_TOKENS=4096

# AI Rules Generator Agent LLM
AI_RULES_LLM_MODEL=mistral
AI_RULES_LLM_BASE_URL=http://localhost:11434/v1
AI_RULES_LLM_MAX_TOKENS_MARKDOWN=4096
```

**Note**: Only mistral model supports function calling required by agents. Other models like gemma2:2b and neural-chat don't support this feature.

## Usage

### Web Interface

Access the Streamlit frontend at `http://localhost:8501` after running:
```bash
streamlit run app.py
```

**Available Pages**:

#### 📊 Repository Analysis
- Interactive form for configuring repository analysis
- Select which analyses to run (Structure, Dependencies, Data Flow, Request Flow, API)
- Real-time progress feedback
- View and download generated analysis files

#### 📄 README Generator
- Generate comprehensive README.md files
- Customize which sections to include
- Option to incorporate existing README content
- Preview and download generated README

#### 🤖 AI Rules Generator
- Create configuration files for AI assistants (Claude, Cursor)
- Configurable detail levels (minimal, standard, comprehensive)
- Control file generation with skip options
- Download individual configuration files

#### ℹ️ About & Configuration
- View current LLM configuration
- Check model endpoints and settings
- Access project information and links

### CLI Commands

```bash
# Analyze codebase
uv run src/main.py analyze --repo-path <path>

# Generate README documentation
uv run src/main.py generate readme --repo-path <path>

# Generate AI assistant configuration files
uv run src/main.py generate ai-rules --repo-path <path>

# Run cronjob (GitLab integration)
uv run src/main.py cronjob analyze
```

### Advanced Options

**Analysis Options:**
```bash
# Analyze with specific exclusions
uv run src/main.py analyze --repo-path . --exclude-code-structure --exclude-data-flow

# Use custom configuration file
uv run src/main.py analyze --repo-path . --config /path/to/config.yaml
```

**README Generation Options:**
```bash
# Generate with specific section exclusions
uv run src/main.py generate readme --repo-path . --exclude-architecture --exclude-c4-model

# Use existing README as context
uv run src/main.py generate readme --repo-path . --use-existing-readme
```

**AI Rules Generation Options:**
```bash
# Skip overwriting existing files
uv run src/main.py generate ai-rules --repo-path . \
    --skip-existing-claude-md \
    --skip-existing-agents-md \
    --skip-existing-cursor-rules

# Customize detail level and line limits
uv run src/main.py generate ai-rules --repo-path . \
    --detail-level comprehensive \
    --max-claude-lines 600 \
    --max-agents-lines 150
```

## Configuration

The tool automatically looks for configuration in `.ai/config.yaml` or `.ai/config.yml` in your repository.

### Configuration Options

- **Exclude specific analyses**: Skip code structure, data flow, dependencies, request flow, or API analysis
- **Customize README sections**: Control which sections appear in generated documentation  
- **Configure cronjob settings**: Set working paths and commit recency filters

You can use CLI flags for quick configuration overrides. See [`config_example.yaml`](config_example.yaml) for all available options and [`.env.sample`](.env.sample) for environment variables.

## Web Interface Guide

### Visual Features
- ✅ Success messages for completed operations
- ❌ Error messages with detailed information
- 🔄 Loading spinners during long operations
- 📊 Progress indicators
- 📥 Download buttons for all generated files
- 📝 In-browser preview of Markdown content
- 📂 Organized file display with expanders

### Performance Tips
- Local Ollama models are slower than cloud APIs (10-30 minutes for full analysis)
- Use max_workers=0 for auto-detection of optimal parallelism
- Consider excluding unnecessary analyses for faster results
- Recommended token limit: 4096 for balanced speed/quality

### Best Practices
- Run analysis before generating README
- Check the `.ai/docs/` directory for analysis outputs
- Use "Use Existing README" to preserve manual content
- Skip existing AI rules files to avoid overwriting customizations

## Troubleshooting

### Port Already in Use
If port 8501 is already in use:
```bash
streamlit run app.py --server.port 8502
```

### Import Errors
Ensure all dependencies are installed:
```bash
uv sync
# or
pip install streamlit
```

### Ollama Connection Issues
- Verify Ollama is running: `curl http://localhost:11434/api/tags`
- Check `.env` has correct Ollama configuration
- Ensure models are downloaded: `ollama list`
- Verify mistral model is available (required for function calling)

### Slow Performance
- Reduce `MAX_TOKENS` from 8192 to 4096 in `.env`
- Consider using cloud APIs (OpenRouter, OpenAI) instead of Ollama
- Exclude unnecessary analyses to reduce processing time

## Architecture

The system uses a **multi-agent architecture** with specialized AI agents for different types of code analysis and generation:

- **CLI Layer**: Entry point with command parsing and subcommand routing
- **Handler Layer**: Command-specific business logic (analyze, generate, cronjob)
- **Agent Layer**: AI-powered analysis and documentation generation
  - Analyzer agents: Structure, data flow, dependencies, request flow, API analysis
  - Documentation agent: README generation
  - AI Rules generator: CLAUDE.md, AGENTS.md, and Cursor rules generation
- **Tool Layer**: File system operations and utilities

### Technology Stack

- **Python 3.13** with pydantic-ai for AI agent orchestration
- **Streamlit 1.40+** for modern web interface
- **OpenAI-compatible APIs** for LLM access (OpenAI, OpenRouter, Ollama, etc.)
- **Ollama** for local, privacy-focused LLM inference
- **GitPython & python-gitlab** for repository operations
- **OpenTelemetry & Langfuse** for observability
- **YAML + Pydantic** for configuration management

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [pydantic-ai](https://ai.pydantic.dev/) for AI agent orchestration
- Supports multiple LLM providers through OpenAI-compatible APIs (including OpenRouter)
- Uses [Langfuse](https://langfuse.com/) for LLM observability
