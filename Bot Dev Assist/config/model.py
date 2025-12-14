"""Model configuration."""

import os
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class ModelConfig:
    """Model configuration for Foundry/LLM."""

    # Model identification
    foundry_model: str = os.getenv(
        "FOUNDRY_MODEL", "qwen2.5-coder-7b-instruct-generic-cpu:4"
    )
    model_name: str = os.getenv("MODEL_NAME", "Dev Assistant")
    model_key: str = os.getenv("MODEL_KEY", "dev-assistant-v1")

    # Runtime parameters
    temperature: float = float(os.getenv("MODEL_TEMPERATURE", "0.2"))
    max_tokens: int = int(os.getenv("MODEL_MAX_TOKENS", "2000"))
    max_context: int = int(os.getenv("MODEL_MAX_CONTEXT", "4096"))
    top_p: float = float(os.getenv("MODEL_TOP_P", "0.9"))
    top_k: int = int(os.getenv("MODEL_TOP_K", "50"))
    repetition_penalty: float = float(os.getenv("MODEL_REPETITION_PENALTY", "1.05"))

    # Features
    streaming: bool = os.getenv("MODEL_STREAMING", "true").lower() == "true"

    # Tools (lazy load to avoid circular imports)
    _tools: Optional[list] = field(default=None, init=False, repr=False)

    @property
    def tools(self):
        """Get tools (lazy loaded)."""
        if self._tools is None:
            from tools import get_all_tools

            self._tools = get_all_tools()
        return self._tools

    def ui_view(self) -> Dict[str, object]:
        """Get UI-safe view of configuration."""
        return {
            "foundry_model": self.foundry_model,
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "max_context": self.max_context,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "repetition_penalty": self.repetition_penalty,
            "streaming": self.streaming,
        }

    def validate(self) -> tuple[bool, str]:
        """Validate model configuration.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.foundry_model:
            return False, "foundry_model not configured"

        if not 0 <= self.temperature <= 2:
            return False, f"temperature must be 0-2, got {self.temperature}"

        if self.max_tokens < 1:
            return False, f"max_tokens must be >= 1, got {self.max_tokens}"

        if self.max_context < self.max_tokens:
            return (
                False,
                f"max_context ({self.max_context}) must be >= max_tokens ({self.max_tokens})",
            )

        return True, ""
