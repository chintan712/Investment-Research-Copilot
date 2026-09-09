from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class Usage:
    model: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None

    @property
    def total_tokens(self) -> int | None:
        if self.input_tokens is None or self.output_tokens is None:
            return None
        return self.input_tokens + self.output_tokens


@dataclass
class LLMResponse:
    text: str
    usage: Usage = field(default_factory=Usage)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)


class LLMProvider(Protocol):
    model_name: str

    def embed(self, text: str) -> list[float]: ...

    def generate(self, system: str, user: str) -> LLMResponse: ...

    def generate_with_tools(self, system: str, user: str, tools: list[dict[str, Any]]) -> LLMResponse: ...
