"""Guardrail system for input/output validation."""

import re
from typing import Tuple

from config import settings  # ← Import from config


class GuardSystem:
    """Unified guardrail system."""

    def __init__(self):
        """Initialize guardrail system using settings."""
        # Get guardrail config (you can add GuardrailConfig to config/app.py if needed)
        self._control_token_patterns = [
            r"<\|im_start\|>",
            r"<\|im_end\|>",
            r"<\|endoftext\|>",
            r"<\|assistant\|>",
            r"<\|user\|>",
            r"<\|system\|>",
        ]

        self.hallucination_phrases = [
            "please create",
            "please ensure",
            "please provide",
            "please add",
            "please write",
            "please generate",
            "i cannot",
            "i don't have access",
            "here's the list of available tools",
        ]

        self.allowed_write_dirs = ["Output", "output", ".", "src", "code"]
        self.max_input_length = 10000

    def check_input(self, user_input: str) -> Tuple[bool, str]:
        """Validate user input."""
        if not user_input or not user_input.strip():
            return False, "Input cannot be empty."

        if len(user_input) > self.max_input_length:
            return False, f"Input is too long (max {self.max_input_length} chars)."

        return True, ""

    def strip_control_tokens(self, text: str) -> str:
        """Strip control tokens from text."""
        cleaned = text
        for token in self._control_token_patterns:
            if re.search(token, cleaned):
                cleaned = re.sub(token, "", cleaned)

        # Remove extra whitespace
        cleaned = re.sub(r"\n\s*\n", "\n", cleaned).strip()

        if cleaned != text:
            print(f"[STRIP] Removed control tokens")

        return cleaned

    def check_output(self, output: str) -> Tuple[bool, str, str]:
        """Check LLM output for token leakage and hallucinations."""
        if not output:
            return False, "Empty output", ""

        # Strip tokens first
        cleaned = self.strip_control_tokens(output)

        # Detect hallucinations
        output_lower = cleaned.lower()
        for phrase in self.hallucination_phrases:
            if phrase in output_lower:
                return False, f"Hallucination detected: '{phrase}'", cleaned

        return True, "OK", cleaned

    def check_file_path(self, file_path: str) -> Tuple[bool, str]:
        """Validate file path for security."""
        # Prevent path traversal
        if ".." in file_path:
            return False, "Path traversal not allowed"

        # Check if path starts with allowed directory
        allowed = any(file_path.startswith(d) for d in self.allowed_write_dirs)
        if not allowed:
            dirs = ", ".join(self.allowed_write_dirs)
            return False, f"Only allowed in: {dirs}"

        return True, ""


# Singleton instance
guard_system = GuardSystem()


# Backward compatibility functions
def check_input(user_input: str) -> Tuple[bool, str]:
    """Check input using guard system."""
    return guard_system.check_input(user_input)


def strip_control_tokens(text: str) -> str:
    """Strip control tokens using guard system."""
    return guard_system.strip_control_tokens(text)


def check_output(output: str) -> Tuple[bool, str, str]:
    """Check output using guard system."""
    return guard_system.check_output(output)


def check_file_path(file_path: str) -> Tuple[bool, str]:
    """Check file path using guard system."""
    return guard_system.check_file_path(file_path)
