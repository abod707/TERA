import asyncio
import platform
import subprocess
from dotenv import load_dotenv
from rich.console import Console, Theme
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
import time
import os
from coordinator import ResearchCoordinator
from research_agents.query_agent import create_query_agent
from research_agents.search_agent import create_search_agent
from research_agents.follow_up_agent import create_follow_up_agent
from research_agents.synthesis_agent import create_synthesis_agent
from llm_config import LLMConfig, create_default_config

load_dotenv()

# Custom Rich theme
custom_theme = Theme({
    "header": "bold cyan",
    "success": "bold green",
    "error": "bold red",
    "prompt": "bold magenta",
    "info": "dim cyan",
    "result": "bold blue",
    "progress": "cyan",
    "highlight": "bold yellow",
    "model": "italic blue",
})

console = Console(theme=custom_theme)

# Configuration
config = {
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    "XAI_API_KEY": os.getenv("XAI_API_KEY"),
    "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY"),
    "MISTRAL_API_KEY": os.getenv("MISTRAL_API_KEY"),
    "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),  # Add Anthropic API key
    "SERPER_API_KEY": os.getenv("SERPER_API_KEY"),
    "BRAVE_API_KEY": os.getenv("BRAVE_API_KEY"),
    "GEMINI_MODEL_NORMAL": os.getenv("GEMINI_MODEL_NORMAL", "gemini-1.5-flash"),
    "GEMINI_MODEL_DEEP": os.getenv("GEMINI_MODEL_DEEP", "gemini-1.5-pro"),
    "GROK_MODEL_NORMAL": os.getenv("GROK_MODEL_NORMAL", "grok-3-mini-beta"),
    "GROK_MODEL_DEEP": os.getenv("GROK_MODEL_DEEP", "grok-3-medium-beta"),
    "OPENROUTER_MODEL_NORMAL": os.getenv("OPENROUTER_MODEL_NORMAL", "mixtral-8x7b-32768"),
    "OPENROUTER_MODEL_DEEP": os.getenv("OPENROUTER_MODEL_DEEP", "mixtral-8x22b-32768"),
    "OPENAI_MODEL_NORMAL": os.getenv("OPENAI_MODEL_NORMAL", "gpt-3.5-turbo"),
    "OPENAI_MODEL_DEEP": os.getenv("OPENAI_MODEL_DEEP", "gpt-4"),
    "DEEPSEEK_MODEL_NORMAL": os.getenv("DEEPSEEK_MODEL_NORMAL", "deepseek-v3"),
    "DEEPSEEK_MODEL_DEEP": os.getenv("DEEPSEEK_MODEL_DEEP", "deepseek-r1"),
    "MISTRAL_MODEL_NORMAL": os.getenv("MISTRAL_MODEL_NORMAL", "mixtral-8x7b"),
    "MISTRAL_MODEL_DEEP": os.getenv("MISTRAL_MODEL_DEEP", "mixtral-8x22b"),
    "ANTHROPIC_MODEL_NORMAL": os.getenv("ANTHROPIC_MODEL_NORMAL", "claude-3-haiku-20240307"),  # Add Claude models
    "ANTHROPIC_MODEL_DEEP": os.getenv("ANTHROPIC_MODEL_DEEP", "claude-3-opus-20240229"),
    "DEFAULT_QUERY": os.getenv("DEFAULT_QUERY", "What is the capital of France?"),
    "DEFAULT_PROVIDER": os.getenv("DEFAULT_PROVIDER", "2"),
    "DEFAULT_MODE": os.getenv("DEFAULT_MODE", "1"),
    "DEFAULT_SEARCH_PROVIDER": os.getenv("DEFAULT_SEARCH_PROVIDER", "1"),
}

# Validate required API keys for search providers
required_keys = ["SERPER_API_KEY", "BRAVE_API_KEY"]
for key in required_keys:
    if not config[key]:
        raise ValueError(f"Missing {key} in .env file!")

def copy_to_clipboard(text: str) -> bool:
    os_type = platform.system()
    try:
        if os_type == "Linux":
            if os.environ.get("TERMUX_VERSION"):
                subprocess.run(['termux-clipboard-set'], input=text, text=True, check=True)
            else:
                subprocess.run(['xclip', '-selection', 'clipboard'], input=text, text=True, check=True)
        elif os_type == "Windows":
            subprocess.run(['clip'], input=text, text=True, check=True)
        elif os_type == "Darwin":
            subprocess.run(['pbcopy'], input=text, text=True, check=True)
        else:
            return False
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

async def main() -> None:
    console.print(Panel(
        Text(
            f"🌟 Welcome to TERA! 🌟\n"
            f"Powered by multiple AI providers\n"
            f"Embark on a journey of knowledge! 🚀",
            style="bold cyan",
            justify="center"
        ),
        title="[bold magenta]🔬 TERA v0.3 🔬[/bold magenta]",
        border_style="bold cyan",
        padding=(2, 4),
        expand=False
    ))

    while True:
        # Provider selection
        provider_table = Table(title="[header]🤖 Select Your AI Provider 🤖[/header]", show_header=False, expand=False)
        provider_table.add_column(style="bold white")
        provider_table.add_column(style="white")
        provider_table.add_row("1. Gemini", "Google's AI models", style="green")
        provider_table.add_row("2. Grok", "xAI's Grok models", style="blue")
        provider_table.add_row("3. OpenRouter", "Access to various open models", style="yellow")
        provider_table.add_row("4. Claude", "Anthropic's Claude models", style="magenta")  # Add Claude
        provider_table.add_row("5. OpenAI", "OpenAI's GPT models", style="cyan")
        provider_table.add_row("6. DeepSeek", "DeepSeek's language models", style="white")
        provider_table.add_row("7. Mistral", "Mistral AI's models", style="purple")
        console.print(provider_table)

        while True:
            provider = Prompt.ask(
                "[prompt]Enter 1-7 (press Enter for 2)[/prompt]",
                default=config["DEFAULT_PROVIDER"],
                console=console
            )
            if provider in ["", "1", "2", "3", "4", "5", "6", "7"]:
                provider = config["DEFAULT_PROVIDER"] if provider == "" else provider
                break
            console.print("[error]Please select 1-7[/error]")

        # Validate API key for selected provider
        api_key_map = {
            "1": "GEMINI_API_KEY",
            "2": "XAI_API_KEY",
            "3": "OPENROUTER_API_KEY",
            "4": "ANTHROPIC_API_KEY",  # Add Anthropic API key validation
            "5": "OPENAI_API_KEY",
            "6": "DEEPSEEK_API_KEY",
            "7": "MISTRAL_API_KEY",
        }
        provider_names = {
            "1": "Gemini",
            "2": "Grok",
            "3": "OpenRouter",
            "4": "Claude",
            "5": "OpenAI",
            "6": "DeepSeek",
            "7": "Mistral",
        }
        if not config[api_key_map[provider]]:
            console.print(f"[error]{provider_names[provider]} provider unavailable. Missing {api_key_map[provider]}.[/error]")
            continue

        # Search Provider selection
        search_provider_table = Table(title="[header]🔍 Select Your Search Provider 🔍[/header]", show_header=False, expand=False)
        search_provider_table.add_column(style="bold white")
        search_provider_table.add_column(style="white")
        search_provider_table.add_row("1. DuckDuckGo", "🔎 Privacy-focused search", style="green")
        search_provider_table.add_row("2. Serper", "🔎 Google search via API", style="blue")
        search_provider_table.add_row("3. Brave", "🔎 Independent search engine", style="yellow")
        console.print(search_provider_table)

        while True:
            search_provider = Prompt.ask(
                "[prompt]Enter 1, 2, or 3 (press Enter for 1)[/prompt]",
                default=config["DEFAULT_SEARCH_PROVIDER"],
                console=console
            )
            if search_provider in ["", "1", "2", "3"]:
                search_provider = config["DEFAULT_SEARCH_PROVIDER"] if search_provider == "" else search_provider
                break
            console.print("[error]Please select 1, 2, or 3[/error]")

        search_provider_map = {
            "1": "duckduckgo",
            "2": "serper",
            "3": "brave"
        }
        selected_search_provider = search_provider_map[search_provider]

        # Mode selection
        mode_table = Table(title="[header]✨ Choose Your Research Mode ✨[/header]", show_header=False, expand=False)
        mode_table.add_column(style="bold white")
        mode_table.add_column(style="white")
        mode_table.add_row("1. Normal Research", "📝 Quick, concise answers", style="green")
        mode_table.add_row("2. Deep Research", "📚 In-depth, analytical reports", style="blue")
        console.print(mode_table)

        while True:
            mode = Prompt.ask(
                "[prompt]Enter 1 or 2 (press Enter for 1)[/prompt]",
                default=config["DEFAULT_MODE"],
                console=console
            )
            if mode in ["", "1", "2"]:
                mode = config["DEFAULT_MODE"] if mode == "" else mode
                break
            console.print("[error]Please select 1 or 2[/error]")

        # Query input
        console.print(Panel(
            "[bold white]Enter your research query:[/bold white]",
            title="[header]🔍 Research Query 🔍[/header]",
            border_style="cyan",
            expand=False
        ))
        query = Prompt.ask(
            "[prompt] > [/prompt]",
            default=config["DEFAULT_QUERY"],
            console=console
        )

        # Set up LLM configuration
        provider_map = {
            "1": ("gemini", config["GEMINI_MODEL_NORMAL"] if mode == "1" else config["GEMINI_MODEL_DEEP"]),
            "2": ("xai", config["GROK_MODEL_NORMAL"] if mode == "1" else config["GROK_MODEL_DEEP"]),
            "3": ("openrouter", config["OPENROUTER_MODEL_NORMAL"] if mode == "1" else config["OPENROUTER_MODEL_DEEP"]),
            "4": ("anthropic", config["ANTHROPIC_MODEL_NORMAL"] if mode == "1" else config["ANTHROPIC_MODEL_DEEP"]),  # Add Claude
            "5": ("openai", config["OPENAI_MODEL_NORMAL"] if mode == "1" else config["OPENAI_MODEL_DEEP"]),
            "6": ("deepseek", config["DEEPSEEK_MODEL_NORMAL"] if mode == "1" else config["DEEPSEEK_MODEL_DEEP"]),
            "7": ("mistral", config["MISTRAL_MODEL_NORMAL"] if mode == "1" else config["MISTRAL_MODEL_DEEP"]),
        }
        provider_key, model_name = provider_map[provider]
        llm_config = LLMConfig(
            search_provider=selected_search_provider,
            reasoning_model_provider=provider_key,
            reasoning_model=model_name,
            main_model_provider=provider_key,
            main_model=model_name,
            fast_model_provider=provider_key,
            fast_model=model_name
        )

        # Create agents
        query_agent = create_query_agent(llm_config.main_model)
        search_agent = create_search_agent(llm_config.main_model, mode)
        follow_up_agent = create_follow_up_agent(llm_config.main_model, mode)
        synthesis_agent = create_synthesis_agent(llm_config.main_model, mode)

        # Run research
        start_time = time.time()
        coordinator = ResearchCoordinator(
            query,
            query_agent,
            search_agent,
            follow_up_agent,
            synthesis_agent,
            mode,
            selected_search_provider,
            config["SERPER_API_KEY"],
            config["BRAVE_API_KEY"]
        )
        console.print("[progress]Processing research...[/progress]")
        report = await coordinator.research()

        # Display results
        console.print("\n[result]══════ Research Result ══════[/result]")
        console.print(Panel(
            report,
            title=f"[success]{'Normal' if mode == '1' else 'Deep'} Research Answer ({model_name})[/success]",
            border_style="blue",
            expand=False,
            padding=(1, 2)
        ))

        # Display time taken
        elapsed_time = time.time() - start_time
        console.print(Panel(f"[success]⏱ Total time taken: {elapsed_time:.2f} seconds[/success]", border_style="green", expand=False))
        console.print(f"[model]Currently using: {model_name}[/model]")

        # Clipboard prompt
        console.print("\n[header]📋 Copy Result to Clipboard? 📋[/header]")
        while True:
            copy_input = Prompt.ask(
                "[prompt]Enter y/n (press Enter for n)[/prompt]",
                default="n",
                console=console
            )
            if copy_input in ["", "y", "n"]:
                copy = copy_input == "y"
                break
            console.print("[error]Please select y or n[/error]")
        if copy:
            if copy_to_clipboard(report):
                console.print(Panel("[success]✅ Result copied to clipboard![/success]", border_style="green", expand=False))
            else:
                console.print(Panel("[error]❌ Failed to copy. Ensure clipboard tools are installed (e.g., xclip on Linux).[/error]", border_style="red", expand=False))

        # Continue or exit
        console.print("\n[header]🔄 Ask Another Question? 🔄[/header]")
        while True:
            continue_input = Prompt.ask(
                "[prompt]Enter y/n (press Enter for y)[/prompt]",
                default="y",
                console=console
            )
            if continue_input in ["", "y", "n"]:
                continue_loop = continue_input != "n"
                break
            console.print("[error]Please select y or n[/error]")
        if not continue_loop:
            console.print(Panel(
                Text(
                    f"🌟 Thank you for using TERA! 🌟\n"
                    f"Come back anytime to explore more knowledge! 👋",
                    style="bold magenta",
                    justify="center"
                ),
                title="[prompt]Farewell[/prompt]",
                border_style="bold magenta",
                padding=(2, 4),
                expand=False
            ))
            break

        console.print("\n[info]════════════════════════════════════════[/info]")

if __name__ == "__main__":
    asyncio.run(main())