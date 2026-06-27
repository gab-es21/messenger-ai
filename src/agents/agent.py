from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AgentProfile:
    id: str
    name: str
    color: str
    active: bool = False
    source: str = "claude"          # "claude" | "ollama"
    model: str = "claude-sonnet-4-6"
    api_key: str = ""
    ollama_endpoint: str = "http://localhost:11434"
    persona: str = ""
    rules: list[str] = field(default_factory=list)
    response_length: str = "medium"  # "short" | "medium" | "long"
    temperature: float = 0.7
    tone: str = "casual"             # "casual" | "formal" | "technical" | "socratic"
