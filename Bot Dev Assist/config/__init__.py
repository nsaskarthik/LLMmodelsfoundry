"""
Centralized configuration loader for model, app, and IRIS settings.

All configuration stays in-process but is structured so the model runner
can be moved out-of-process later without changing callers.
"""

import os
from dataclasses import dataclass, field
from typing import Dict

from .app import AppConfig
from .iris import IRISConfig
from .model import ModelConfig


@dataclass
class Settings:
    """Global settings container."""

    app: AppConfig = field(default_factory=AppConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    iris: IRISConfig = field(default_factory=IRISConfig)

    def ui_safe_view(self) -> Dict[str, object]:
        """Expose only UI-safe fields; secrets remain masked/omitted."""
        return {
            "app": self.app.ui_view(),
            "model": self.model.ui_view(),
            "iris": self.iris.ui_view(),
        }

    def validate(self) -> tuple[bool, str]:
        """Validate all configurations.

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate app config
        if not os.path.exists(self.app.log_dir):
            os.makedirs(self.app.log_dir, exist_ok=True)

        if not os.path.exists(self.app.session_store):
            os.makedirs(self.app.session_store, exist_ok=True)

        # Validate model config
        if not self.model.foundry_model:
            return False, "Model name not configured"

        # Validate IRIS if enabled
        is_valid, msg = self.iris.validate()
        if not is_valid:
            return False, f"IRIS validation failed: {msg}"

        return True, ""


# Singleton settings object
settings = Settings()
