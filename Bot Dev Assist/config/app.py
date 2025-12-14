"""Application configuration."""

import os
from dataclasses import dataclass, field
from typing import Dict, Literal, Optional


@dataclass
class AppConfig:
    """Application configuration."""

    # Execution mode
    mode: Literal["inprocess", "remote_model"] = "inprocess"
    remote_model_url: Optional[str] = None

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_dir: str = os.getenv("LOG_DIR", "logs")
    log_path: Optional[str] = os.getenv(
        "LOG_PATH", os.path.join(os.getcwd(), "logs", "app.log")
    )

    # Sessions
    session_store: str = os.getenv("SESSION_STORE", "data/sessions")

    # Security
    guardrail_policy: str = os.getenv("GUARDRAIL_POLICY", "allow_all")

    # Tracing
    tracing_enabled: bool = os.getenv("TRACING_ENABLED", "false").lower() == "true"

    # UI Configuration
    ui_config: Dict[str, object] = field(
        default_factory=lambda: {
            "show_model": True,
            "allow_param_edit": ["temperature", "max_output_tokens", "max_context"],
            "theme": "dark",
        }
    )

    def __post_init__(self):
        """Validate and setup directories."""
        # Create log directory if needed
        if self.log_path:
            log_dir = os.path.dirname(self.log_path)
            os.makedirs(log_dir, exist_ok=True)

        # Create session store directory
        os.makedirs(self.session_store, exist_ok=True)

    def ui_view(self) -> Dict[str, object]:
        """Get UI-safe view of configuration."""
        return {
            "mode": self.mode,
            "remote_model_url": self.remote_model_url,
            "log_level": self.log_level,
            "log_dir": self.log_dir,
            "session_store": self.session_store,
            "guardrail_policy": self.guardrail_policy,
            "tracing_enabled": self.tracing_enabled,
            "ui_config": self.ui_config,
        }

    def validate(self) -> tuple[bool, str]:
        """Validate app configuration.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if self.mode not in ["inprocess", "remote_model"]:
            return False, f"Invalid mode: {self.mode}"

        if self.mode == "remote_model" and not self.remote_model_url:
            return False, "remote_model_url required when mode is remote_model"

        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            return False, f"Invalid log level: {self.log_level}"

        return True, ""
