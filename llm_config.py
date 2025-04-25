from dataclasses import dataclass
from typing import Optional
import os
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic  # Add Anthropic client
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

@dataclass
class LLMConfig:
    search_provider: str
    reasoning_model_provider: str
    reasoning_model: str
    main_model_provider: str
    main_model: str
    fast_model_provider: str
    fast_model: str

    def __post_init__(self):
        supported_providers = ["xai", "gemini", "openrouter", "openai", "deepseek", "mistral", "anthropic"]  # Add anthropic
        for provider in [self.reasoning_model_provider, self.main_model_provider, self.fast_model_provider]:
            if provider not in supported_providers:
                raise ValueError(f"Provider {provider} not supported. Choose from {supported_providers}")

        provider_mapping = {
            "xai": {
                "client": AsyncOpenAI,
                "model": OpenAIChatCompletionsModel,
                "base_url": "https://api.x.ai/v1",
                "api_key": os.getenv("XAI_API_KEY"),
            },
            "gemini": {
                "client": AsyncOpenAI,
                "model": OpenAIChatCompletionsModel,
                "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
                "api_key": os.getenv("GEMINI_API_KEY"),
            },
            "openrouter": {
                "client": AsyncOpenAI,
                "model": OpenAIChatCompletionsModel,
                "base_url": "https://openrouter.ai/api/v1",
                "api_key": os.getenv("OPENROUTER_API_KEY"),
            },
            "openai": {
                "client": AsyncOpenAI,
                "model": OpenAIChatCompletionsModel,
                "base_url": "https://api.openai.com/v1",
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
            "deepseek": {
                "client": AsyncOpenAI,
                "model": OpenAIChatCompletionsModel,
                "base_url": "https://api.deepseek.com",
                "api_key": os.getenv("DEEPSEEK_API_KEY"),
            },
            "mistral": {
                "client": AsyncOpenAI,
                "model": OpenAIChatCompletionsModel,
                "base_url": "https://api.mistral.ai/v1",
                "api_key": os.getenv("MISTRAL_API_KEY"),
            },
            "anthropic": {  # Add Claude provider
                "client": AsyncAnthropic,
                "model": OpenAIChatCompletionsModel,
                "base_url": None,  # Anthropic client doesn't use base_url
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
            },
        }

        def _init_model(provider: str, model_name: str) -> OpenAIChatCompletionsModel:
            config = provider_mapping[provider]
            if provider == "anthropic":
                client = config["client"](api_key=config["api_key"])
            else:
                client = config["client"](base_url=config["base_url"], api_key=config["api_key"])
            return config["model"](model=model_name, openai_client=client)

        self.reasoning_model = _init_model(self.reasoning_model_provider, self.reasoning_model)
        self.main_model = _init_model(self.main_model_provider, self.main_model)
        self.fast_model = _init_model(self.fast_model_provider, self.fast_model)

def create_default_config(provider: str = os.getenv("MAIN_MODEL_PROVIDER", "xai"), model_name: str = os.getenv("GROK_MODEL_NORMAL", "grok-3-mini-beta")) -> LLMConfig:
    return LLMConfig(
        search_provider=os.getenv("SEARCH_PROVIDER", "duckduckgo"),
        reasoning_model_provider=provider,
        reasoning_model=model_name,
        main_model_provider=provider,
        main_model=model_name,
        fast_model_provider=provider,
        fast_model=model_name
    )

def get_base_url(model: OpenAIChatCompletionsModel) -> str:
    if hasattr(model.client, "base_url") and model.client.base_url:
        return model.client.base_url
    return "N/A"  # For Anthropic, which doesn't use base_url

def model_supports_structured_output(model: OpenAIChatCompletionsModel) -> bool:
    return "x.ai" in get_base_url(model) or "openrouter.ai" in get_base_url(model)