# ULTRON AI - Prompts Directory (.prompts/)

This directory stores instructions, guidelines, templates, and system messages used to guide LLM completions and agent behaviors across ULTRON.

> [!NOTE]
> This folder is non-executable and contains instructions rather than code. The code that loads and routes these prompts resides in the `backend/` and `core/` modules (e.g., `prompts/loader.py`).

## Directory Structure

Organize system and user prompts into structured markdown or text files:
- `system_instruction.md` - The base instructions and persona configuration (e.g., JARVIS/FRIDAY/ULTRON style guidelines).
- `planning_agent.md` - System instructions for translating high-level user requests into concrete plans.
- `coding_agent.md` - Specific context, code style preferences, and syntax requirements for the coding assistant.
- `voice_interaction.md` - Guidelines and system context for speech-to-text and text-to-speech interaction.

## Best Practices for Prompt Templates

1. **Clear Context Boundaries**: Clearly distinguish variables using templates, double brackets `{{var}}`, or specific XML-style tags.
2. **Deterministic Output Formats**: Specify structure (e.g., JSON schemas or exact XML tagging) clearly in the prompts.
3. **Role & Identity**: Reinforce the local-first, privacy-respecting, and helper persona of the agent.
