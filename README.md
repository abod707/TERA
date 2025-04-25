# TERA: Terminal-Enhanced Research Assistant

TERA (v0.3) is a powerful, AI-driven command-line research tool designed to deliver quick answers or in-depth analytical reports. Powered by multiple ai providers , TERA offers a sleek, user-friendly interface for exploring knowledge with elegance and depth.

Whether you're a student, researcher, or curious mind, TERA makes research accessible and engaging.

Created by: Abdallah Naish Alghamdi  
Instagram: @i_gixnu

## Features

### Two Research Modes:
- **Normal Research**: Quick, concise answers for straightforward queries.
- **Deep Research**: Comprehensive reports with:  
  - Subtopic analysis  
  - Gap identification  
  - Synthesized insights  
  - Up to 60 results (5 searchs per query, 3 queries per iteration, 4 iterations)  
  - Dynamic query generation (1–5 queries based on complexity)  
  - Estimated runtime: ~14 minutes for deep mode

### Multiple AI Providers:
- **Gemini**
- **Grok**
- **OpenRouter**
- **Openai**
- **Mistral**
- **Deepseek**
- **Anthropic**

### Additional Capabilities:
- **Web Search Integration** via:  
  - Serper API  
  - Brave API  
  - DuckDuckGo
  - (All for authoritative sources)

- **Rich CLI Interface** using rich:  
  - Colorful tables  
  - Progress bars  
  - Markdown-formatted reports  
  - Improved output messages (e.g., iteration tracking, result summaries)

- **Cross-Platform Support**:
  - Windows  
  - macOS  
  - Linux  
  - Android (via Termux; clipboard support requires termux-api)

- **Clipboard Support**:
  - Copy results to clipboard (requires termux-api on Android)  

## Prerequisites

Before using TERA, make sure you have the following:  

- Python 3.8+  
- A terminal or command-line interface:  
  - Windows: Command Prompt or PowerShell  
  - macOS/Linux: Terminal  
  - Android: Termux (install termux-api for clipboard support)

- (Optional) GitHub account (for cloning repo)

- API Keys for:
  - Gemini API  
  - Grok API (via xAI)  
  - Openai API
  - Mistral API
  - Deepseek API
  - OpenRouter API
  - Anthropic API
  - Serper API (for web searches)  
  - Brave API (for web searches)

(**you can use what ever you want**,but if you want tracing use Openai)
## Installation

### Step 1: Clone the Repository

Open your terminal (or Termux on Android).  

Install Git if you haven't already:
```bash
# Termux:  
pkg install git

# Windows/macOS/Linux:
# Install Git from https://git-scm.com/downloads
```

Clone the TERA repo:  
```bash
git clone https://github.com/abod707/TERA.git
cd TERA
```

### Step 2: Install Dependencies

(Recommended) Create a virtual environment:  
```bash
python -m venv venv
source venv/bin/activate

# On Windows, use:  
venv\Scripts\activate
```

Install required libraries:  
```bash
pip install -r requirements.txt
```

Note: Ensure requests, duckduckgo_search, rich, and other dependencies are installed (see requirements.txt for the full list).

### Step 3: Set Up Environment Variables

Rename .env.example to .env and add your API keys:  
```
# API Keys
GEMINI_API_KEY=
XAI_API_KEY=
OPENROUTER_API_KEY=
OPENAI_API_KEY=
DEEPSEEK_API_KEY=
MISTRAL_API_KEY=
ANTHROPIC_API_KEY=
SERPER_API_KEY=
BRAVE_API_KEY=

# Model Configurations
GEMINI_MODEL_NORMAL=
GEMINI_MODEL_DEEP=
GROK_MODEL_NORMAL=
GROK_MODEL_DEEP=
OPENROUTER_MODEL_NORMAL=
OPENROUTER_MODEL_DEEP=
OPENAI_MODEL_NORMAL=
OPENAI_MODEL_DEEP=
DEEPSEEK_MODEL_NORMAL=
DEEPSEEK_MODEL_DEEP=
MISTRAL_MODEL_NORMAL=
MISTRAL_MODEL_DEEP=
ANTHROPIC_MODEL_NORMAL=
ANTHROPIC_MODEL_DEEP=

# Default Settings
DEFAULT_QUERY=What is the capital of France?
DEFAULT_PROVIDER=1
DEFAULT_MODE=1
DEFAULT_SEARCH_PROVIDER=1
```


## disabling openai tracing

if you don't using openai api key
you will encounter this error
```bash
OPENAI_API_KEY is not set, skipping trace export
```

you can skip this error by export this environment variable:
```bash
export OPENAI_AGENTS_DISABLE_TRACING=1
```
or in windows 
```cmd
set OPENAI_AGENTS_DISABLE_TRACING=1
```

## Usage

Run the main script:  
```bash
python tera.py
```

You'll be prompted to select:  
  
- AI Provider  
- Search Provider
- Research Mode: Normal / Deep


Results will be displayed with colorful formatting, Markdown structure, and optionally copied to your clipboard.  

## Contributing

1. Fork the repository  
2. Create a new branch:  
   ```bash
   git checkout -b feature-name
   ```
3. Make your changes  
4. Commit:  
   ```bash
   git commit -m "Add new feature"
   ```
5. Push:  
   ```bash
   git push origin feature-name
   ```
6. Create a pull request

## License

This project is licensed under the MIT License.  

## Support

For help or feedback, reach out on Instagram: @i_gixnu  

Ready to explore knowledge from your terminal? Let TERA be your guide.
