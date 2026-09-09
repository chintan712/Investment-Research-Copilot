from app.core.config import Settings
from app.llm.base import LLMProvider
from app.llm.providers import AzureOpenAIProvider, OpenAIProvider


def build_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "azure_openai":
        return AzureOpenAIProvider(settings)
    if settings.llm_provider == "openai":
        return OpenAIProvider(settings)
    raise ValueError(f"Unsupported LLM_PROVIDER: {settings.llm_provider}")
