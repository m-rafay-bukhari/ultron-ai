import os
from typing import Dict, Any

class PromptLoader:
    """Helper class to load, format, and manage modular prompt templates from files."""

    def __init__(self, base_dir: str = None) -> None:
        if base_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = base_dir

    def load_prompt(self, category: str, name: str, version: str = "v1") -> str:
        """Load a raw prompt template string from a file.
        
        File format expectation: prompts/{category}/{name}_{version}.txt
        """
        filename = f"{name}_{version}.txt"
        filepath = os.path.join(self.base_dir, category, filename)
        
        if not os.path.exists(filepath):
            # Fallback to name.txt if versioned file doesn't exist
            filepath = os.path.join(self.base_dir, category, f"{name}.txt")

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Prompt template not found at {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            return f.read().strip()

    def format_prompt(self, category: str, name: str, variables: Dict[str, Any], version: str = "v1") -> str:
        """Load and format a prompt template with provided template variables."""
        template = self.load_prompt(category, name, version)
        return template.format(**variables)
