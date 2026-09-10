from typing import Any

from openai import AzureOpenAI, OpenAI

from app.core.config import Settings
from app.llm.base import LLMResponse, Usage


class AzureOpenAIProvider:
    def __init__(self, settings: Settings) -> None:
        if not settings.azure_openai_api_key or not settings.azure_openai_endpoint:
            raise RuntimeError("Azure OpenAI credentials are not configured")
        self.model_name = settings.azure_openai_deployment or "azure-openai"
        self.embedding_model = settings.azure_openai_embedding_deployment
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            azure_endpoint=settings.azure_openai_endpoint,
            api_version="2024-10-21",
            timeout=settings.llm_timeout_seconds,
        )

    def embed(self, text: str) -> list[float]:
        if not self.embedding_model:
            raise RuntimeError("AZURE_OPENAI_EMBEDDING_DEPLOYMENT is not configured")
        return self.client.embeddings.create(input=text, model=self.embedding_model).data[0].embedding

    def generate(self, system: str, user: str) -> LLMResponse:
        result = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        )
        choice = result.choices[0]
        usage = result.usage
        return LLMResponse(choice.message.content or "", Usage(self.model_name, usage.prompt_tokens if usage else None, usage.completion_tokens if usage else None))

    def generate_with_tools(self, system: str, user: str, tools: list[dict[str, Any]]) -> LLMResponse:
        result = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            tools=tools,
            tool_choice="auto",
        )
        choice = result.choices[0]
        usage = result.usage
        calls = [{"tool": call.function.name, "arguments": call.function.arguments} for call in (choice.message.tool_calls or [])]
        return LLMResponse(choice.message.content or "", Usage(self.model_name, usage.prompt_tokens if usage else None, usage.completion_tokens if usage else None), calls)


class OpenAIProvider(AzureOpenAIProvider):
    def __init__(self, settings: Settings) -> None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        self.model_name = settings.openai_model
        self.embedding_model = settings.openai_embedding_model
        self.client = OpenAI(api_key=settings.openai_api_key, timeout=settings.llm_timeout_seconds)
