"""
AI Doc Gen - Web Frontend
Streamlit-based web interface for the AI documentation generator
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st

import config
from handlers.analyze import AnalyzeHandler, AnalyzeHandlerConfig
from handlers.readme import ReadmeHandler, ReadmeHandlerConfig
from handlers.ai_rules import AIRulesHandler, AIRulesHandlerConfig
from utils import Logger


# Initialize Logger
log_dir = Path.cwd() / ".logs" / "streamlit" / datetime.now().strftime("%Y_%m_%d")
log_dir.mkdir(parents=True, exist_ok=True)
Logger.init(
    log_dir=log_dir,
    file_level=logging.INFO,
    console_level=logging.WARNING,
    file_name=f"streamlit_{datetime.now().strftime('%H%M%S')}.log"
)


# Page configuration
st.set_page_config(
    page_title="AI Doc Gen",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_session_state():
    """Initialize session state variables"""
    if "analysis_running" not in st.session_state:
        st.session_state.analysis_running = False
    if "analysis_complete" not in st.session_state:
        st.session_state.analysis_complete = False
    if "generated_files" not in st.session_state:
        st.session_state.generated_files = []


def display_llm_config():
    """Display current LLM configuration"""
    with st.sidebar.expander("🤖 LLM Configuration", expanded=False):
        st.markdown("**Analyzer Agent:**")
        st.code(f"Model: {config.ANALYZER_LLM_MODEL}\nURL: {config.ANALYZER_LLM_BASE_URL}")
        
        st.markdown("**Documenter Agent:**")
        st.code(f"Model: {config.DOCUMENTER_LLM_MODEL}\nURL: {config.DOCUMENTER_LLM_BASE_URL}")
        
        st.markdown("**AI Rules Generator:**")
        st.code(f"Model: {config.AI_RULES_LLM_MODEL}\nURL: {config.AI_RULES_LLM_BASE_URL}")


async def run_analysis(repo_path: Path, config_obj: AnalyzeHandlerConfig):
    """Run repository analysis"""
    handler = AnalyzeHandler(config_obj)
    await handler.handle()


async def run_readme_generation(repo_path: Path, config_obj: ReadmeHandlerConfig):
    """Run README generation"""
    handler = ReadmeHandler(config_obj)
    await handler.handle()


async def run_ai_rules_generation(repo_path: Path, config_obj: AIRulesHandlerConfig):
    """Run AI rules generation"""
    handler = AIRulesHandler(config_obj)
    await handler.handle()


def analyze_page():
    """Repository Analysis Page"""
    st.markdown('<div class="main-header">📊 Repository Analysis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Analyze your codebase structure, dependencies, data flow, and APIs</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        repo_path = st.text_input(
            "Repository Path",
            value=str(Path.cwd()),
            help="Enter the absolute path to the repository you want to analyze",
        )

    with col2:
        max_workers = st.number_input(
            "Max Workers",
            min_value=0,
            max_value=20,
            value=0,
            help="Maximum concurrent workers (0=auto-detect CPU count)",
        )

    st.markdown("### Analysis Options")
    col1, col2, col3 = st.columns(3)

    with col1:
        exclude_structure = st.checkbox("Exclude Code Structure", value=False)
        exclude_dependencies = st.checkbox("Exclude Dependencies", value=False)

    with col2:
        exclude_data_flow = st.checkbox("Exclude Data Flow", value=False)
        exclude_request_flow = st.checkbox("Exclude Request Flow", value=False)

    with col3:
        exclude_api = st.checkbox("Exclude API Analysis", value=False)

    st.markdown("---")

    if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
        if not Path(repo_path).exists():
            st.error(f"❌ Repository path does not exist: {repo_path}")
            return

        st.session_state.analysis_running = True
        st.session_state.analysis_complete = False

        with st.spinner("🔍 Analyzing repository... This may take several minutes with local Ollama models."):
            try:
                config_obj = AnalyzeHandlerConfig(
                    repo_path=Path(repo_path),
                    exclude_code_structure=exclude_structure,
                    exclude_dependencies=exclude_dependencies,
                    exclude_data_flow=exclude_data_flow,
                    exclude_request_flow=exclude_request_flow,
                    exclude_api_analysis=exclude_api,
                    max_workers=max_workers,
                )

                asyncio.run(run_analysis(Path(repo_path), config_obj))

                st.session_state.analysis_running = False
                st.session_state.analysis_complete = True

                # Find generated files
                docs_path = Path(repo_path) / ".ai" / "docs"
                if docs_path.exists():
                    st.session_state.generated_files = list(docs_path.glob("*.md"))

                st.success("✅ Analysis completed successfully!")

            except Exception as e:
                st.session_state.analysis_running = False
                error_msg = f"❌ Analysis failed: {str(e)}"
                st.error(error_msg)
                try:
                    Logger.error(f"Analysis error: {e}", exc_info=True)
                except:
                    pass  # Logger might not be available

    # Display results if analysis is complete
    if st.session_state.analysis_complete and st.session_state.generated_files:
        st.markdown("### 📄 Generated Analysis Files")

        for file_path in st.session_state.generated_files:
            with st.expander(f"📝 {file_path.name}", expanded=False):
                content = file_path.read_text()
                st.markdown(content)

                col1, col2 = st.columns([1, 4])
                with col1:
                    st.download_button(
                        label="⬇️ Download",
                        data=content,
                        file_name=file_path.name,
                        mime="text/markdown",
                    )


def readme_page():
    """README Generation Page"""
    st.markdown('<div class="main-header">📖 README Generator</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Generate comprehensive README.md from your analysis</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        repo_path = st.text_input(
            "Repository Path",
            value=str(Path.cwd()),
            help="Enter the absolute path to the repository",
        )

    with col2:
        use_existing = st.checkbox("Use Existing README", value=False, help="Incorporate existing README content")

    st.markdown("### README Sections to Exclude")
    col1, col2, col3 = st.columns(3)

    with col1:
        exclude_overview = st.checkbox("Exclude Project Overview", value=False)
        exclude_toc = st.checkbox("Exclude Table of Contents", value=False)
        exclude_architecture = st.checkbox("Exclude Architecture", value=False)

    with col2:
        exclude_c4 = st.checkbox("Exclude C4 Model", value=False)
        exclude_structure = st.checkbox("Exclude Repository Structure", value=False)
        exclude_dependencies = st.checkbox("Exclude Dependencies", value=False)

    with col3:
        exclude_api = st.checkbox("Exclude API Documentation", value=False)
        exclude_dev_notes = st.checkbox("Exclude Development Notes", value=False)
        exclude_issues = st.checkbox("Exclude Known Issues", value=False)

    st.markdown("---")

    if st.button("📝 Generate README", type="primary", use_container_width=True):
        if not Path(repo_path).exists():
            st.error(f"❌ Repository path does not exist: {repo_path}")
            return

        with st.spinner("📝 Generating README... This may take a few minutes."):
            try:
                config_obj = ReadmeHandlerConfig(
                    repo_path=Path(repo_path),
                    use_existing_readme=use_existing,
                    exclude_project_overview=exclude_overview,
                    exclude_table_of_contents=exclude_toc,
                    exclude_architecture=exclude_architecture,
                    exclude_c4_model=exclude_c4,
                    exclude_repository_structure=exclude_structure,
                    exclude_dependencies_and_integration=exclude_dependencies,
                    exclude_api_documentation=exclude_api,
                    exclude_development_notes=exclude_dev_notes,
                    exclude_known_issues_and_limitations=exclude_issues,
                    exclude_additional_documentation=False,
                )

                asyncio.run(run_readme_generation(Path(repo_path), config_obj))

                st.success("✅ README generated successfully!")

                # Display generated README
                readme_path = Path(repo_path) / "README.md"
                if readme_path.exists():
                    st.markdown("### 📄 Generated README.md")
                    content = readme_path.read_text()
                    st.markdown(content)

                    st.download_button(
                        label="⬇️ Download README.md",
                        data=content,
                        file_name="README.md",
                        mime="text/markdown",
                        use_container_width=True,
                    )

            except Exception as e:
                error_msg = f"❌ README generation failed: {str(e)}"
                st.error(error_msg)
                try:
                    Logger.error(f"README generation error: {e}", exc_info=True)
                except:
                    pass  # Logger might not be available


def ai_rules_page():
    """AI Rules Generation Page"""
    st.markdown('<div class="main-header">🤖 AI Rules Generator</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Generate CLAUDE.md, AGENTS.md, and Cursor rules for AI assistants</div>',
        unsafe_allow_html=True,
    )

    repo_path = st.text_input(
        "Repository Path",
        value=str(Path.cwd()),
        help="Enter the absolute path to the repository",
    )

    st.markdown("### Generation Options")
    col1, col2 = st.columns(2)

    with col1:
        skip_claude = st.checkbox("Skip Existing CLAUDE.md", value=False)
        skip_agents = st.checkbox("Skip Existing AGENTS.md", value=False)
        skip_cursor = st.checkbox("Skip Existing Cursor Rules", value=False)

    with col2:
        detail_level = st.selectbox(
            "Detail Level",
            options=["minimal", "standard", "comprehensive"],
            index=1,
            help="Level of detail in generated files",
        )
        max_claude_lines = st.number_input("Max CLAUDE.md Lines", value=500, min_value=100, max_value=2000)
        max_agents_lines = st.number_input("Max AGENTS.md Lines", value=150, min_value=50, max_value=500)

    st.markdown("---")

    if st.button("🚀 Generate AI Rules", type="primary", use_container_width=True):
        if not Path(repo_path).exists():
            st.error(f"❌ Repository path does not exist: {repo_path}")
            return

        with st.spinner("🤖 Generating AI rules... This may take a few minutes."):
            try:
                config_obj = AIRulesHandlerConfig(
                    repo_path=Path(repo_path),
                    skip_existing_claude_md=skip_claude,
                    skip_existing_agents_md=skip_agents,
                    skip_existing_cursor_rules=skip_cursor,
                    detail_level=detail_level,
                    max_claude_lines=max_claude_lines,
                    max_agents_lines=max_agents_lines,
                )

                asyncio.run(run_ai_rules_generation(Path(repo_path), config_obj))

                st.success("✅ AI rules generated successfully!")

                # Display generated files
                st.markdown("### 📄 Generated Files")

                files_to_display = [
                    (Path(repo_path) / "CLAUDE.md", "CLAUDE.md"),
                    (Path(repo_path) / "AGENTS.md", "AGENTS.md"),
                    (Path(repo_path) / ".cursor" / "rules", "Cursor Rules"),
                ]

                for file_path, display_name in files_to_display:
                    if file_path.exists():
                        with st.expander(f"📝 {display_name}", expanded=False):
                            content = file_path.read_text() if file_path.is_file() else ""
                            if file_path.is_dir():
                                st.info(f"Directory created: {file_path}")
                                for rule_file in file_path.glob("*.md"):
                                    st.markdown(f"**{rule_file.name}**")
                                    st.code(rule_file.read_text(), language="markdown")
                            else:
                                st.markdown(content)

                                st.download_button(
                                    label=f"⬇️ Download {display_name}",
                                    data=content,
                                    file_name=display_name,
                                    mime="text/markdown",
                                )

            except Exception as e:
                error_msg = f"❌ AI rules generation failed: {str(e)}"
                st.error(error_msg)
                try:
                    Logger.error(f"AI rules generation error: {e}", exc_info=True)
                except:
                    pass  # Logger might not be available


def about_page():
    """About Page"""
    st.markdown('<div class="main-header">ℹ️ About AI Doc Gen</div>', unsafe_allow_html=True)

    st.markdown(
        """
    ### 🎯 What is AI Doc Gen?

    AI Doc Gen is a multi-agent Python tool that automatically analyzes codebases and generates 
    comprehensive documentation using specialized AI agents.

    ### ✨ Features

    - **Multi-Agent Analysis**: 5 concurrent AI agents analyze different aspects of your code
    - **Comprehensive Documentation**: Generates README, architecture diagrams, and API docs
    - **AI Assistant Integration**: Creates configuration files for Claude, Cursor, and other AI tools
    - **Flexible LLM Support**: Works with OpenAI, Anthropic, Ollama, and any OpenAI-compatible API
    - **Automated Workflows**: Batch processing via GitLab integration

    ### 🏗️ Architecture

    **Analysis Agents:**
    - 📦 Structure Analyzer - Maps code organization and components
    - 🔗 Dependency Analyzer - Identifies internal and external dependencies
    - 🔄 Data Flow Analyzer - Tracks data movement through the system
    - 🌐 Request Flow Analyzer - Documents API and request handling
    - 📡 API Analyzer - Catalogs endpoints and interfaces

    **Generation Agents:**
    - 📖 README Generator - Creates comprehensive project documentation
    - 🤖 AI Rules Generator - Produces assistant configuration files

    ### 🛠️ Technology Stack

    - **Python 3.13** - Core language
    - **Pydantic-AI** - Agent framework
    - **Streamlit** - Web interface
    - **GitPython** - Repository analysis
    - **OpenTelemetry** - Observability

    ### 📊 Current Configuration

    """
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Analyzer Agent**")
        st.code(
            f"""Model: {config.ANALYZER_LLM_MODEL}
URL: {config.ANALYZER_LLM_BASE_URL}
Max Tokens: {config.ANALYZER_LLM_MAX_TOKENS}
Temperature: {config.ANALYZER_LLM_TEMPERATURE}
Timeout: {config.ANALYZER_LLM_TIMEOUT}s"""
        )

    with col2:
        st.markdown("**Documenter Agent**")
        st.code(
            f"""Model: {config.DOCUMENTER_LLM_MODEL}
URL: {config.DOCUMENTER_LLM_BASE_URL}
Max Tokens: {config.DOCUMENTER_LLM_MAX_TOKENS}
Temperature: {config.DOCUMENTER_LLM_TEMPERATURE}
Timeout: {config.DOCUMENTER_LLM_TIMEOUT}s"""
        )

    st.markdown("---")
    st.markdown(
        """
    ### 🔗 Links

    - [GitHub Repository](https://github.com/yourusername/ai-doc-gen)
    - [Documentation](https://docs.ai-doc-gen.dev)
    - [Report Issues](https://github.com/yourusername/ai-doc-gen/issues)

    ### 📄 License

    This project is licensed under the MIT License.
    """
    )


def main():
    """Main application entry point"""
    init_session_state()

    # Sidebar navigation
    with st.sidebar:
        st.markdown("## 📚 AI Doc Gen")
        st.markdown("---")

        page = st.radio(
            "Navigation",
            ["📊 Analysis", "📖 README", "🤖 AI Rules", "ℹ️ About"],
            label_visibility="collapsed",
        )

        st.markdown("---")
        display_llm_config()

        st.markdown("---")
        st.caption(f"Version: {config.VERSION}")
        st.caption("Made with ❤️ using Streamlit")

    # Route to selected page
    if page == "📊 Analysis":
        analyze_page()
    elif page == "📖 README":
        readme_page()
    elif page == "🤖 AI Rules":
        ai_rules_page()
    elif page == "ℹ️ About":
        about_page()


if __name__ == "__main__":
    main()
