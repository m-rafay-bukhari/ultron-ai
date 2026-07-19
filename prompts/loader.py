import os
from typing import Dict, Any, Optional
from jinja2 import Template


class PromptLoader:
    """Helper class to load, format, and manage modular prompt templates from files using Jinja2."""

    def __init__(self, base_dir: Optional[str] = None) -> None:
        if base_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = base_dir

    def load_prompt(self, category: str, name: str, version: str = "v1") -> str:
        """Load a raw prompt template string from a file.

        Checks standard package prompts/ subdirectories first, then falls back to project root's .prompts/ directory.
        """
        filename = f"{name}_{version}.txt"
        filepath = os.path.join(self.base_dir, category, filename)

        if not os.path.exists(filepath):
            filepath = os.path.join(self.base_dir, category, f"{name}.txt")

        # Fallback to project root .prompts folder if not found in package subdirectories
        if not os.path.exists(filepath):
            project_root = os.path.dirname(self.base_dir)
            dot_prompts_md = os.path.join(project_root, ".prompts", f"{name}.md")
            dot_prompts_txt = os.path.join(project_root, ".prompts", f"{name}.txt")
            if os.path.exists(dot_prompts_md):
                filepath = dot_prompts_md
            elif os.path.exists(dot_prompts_txt):
                filepath = dot_prompts_txt

        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"Prompt template not found for category={category}, name={name}"
            )

        with open(filepath, "r", encoding="utf-8") as f:
            return f.read().strip()

    def format_prompt(
        self, category: str, name: str, variables: Dict[str, Any], version: str = "v1"
    ) -> str:
        """Load and format a prompt template using Jinja2 rendering."""
        template_content = self.load_prompt(category, name, version)
        template = Template(template_content)
        return str(template.render(**variables))
