"""IRIS Database configuration."""

import os
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class IRISConfig:
    """IRIS Database configuration."""

    enabled: bool = os.getenv("IRIS_ENABLED", "false").lower() == "true"
    host: str = os.getenv("IRIS_HOST", "localhost")
    port: int = int(os.getenv("IRIS_PORT", "1972"))
    username: str = os.getenv("IRIS_USERNAME", "superuser")
    password: str = os.getenv("IRIS_PASSWORD", "****")
    namespace: str = os.getenv("IRIS_NAMESPACE", "IRISAPP")
    schema_source: Optional[str] = os.getenv("IRIS_SCHEMA_SOURCE")
    cache_path: str = os.getenv("IRIS_CACHE_PATH", "data/cache/iris_schema.json")
    preload: bool = os.getenv("IRIS_PRELOAD", "false").lower() == "true"

    ui_exposed_fields: Dict[str, bool] = field(
        default_factory=lambda: {
            "host": True,
            "port": True,
            "namespace": True,
            "schema_source": True,
        }
    )

    def ui_view(self) -> Dict[str, object]:
        """Get UI-safe view of configuration (masks secrets)."""
        view = {}
        for key, allowed in self.ui_exposed_fields.items():
            if allowed and hasattr(self, key):
                view[key] = getattr(self, key)
        view["password"] = "****"  # Never expose password
        view["preload"] = self.preload
        view["enabled"] = self.enabled
        return view

    def validate(self) -> tuple[bool, str]:
        """Validate IRIS configuration.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.enabled:
            return True, ""

        if not self.host or not self.port:
            return False, "IRIS host and port are required"

        if not self.username or self.password == "****":
            return False, "IRIS credentials are required"

        if not self.namespace:
            return False, "IRIS namespace is required"

        return True, ""
