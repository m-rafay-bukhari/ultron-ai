# ULTRON AI - Skills Directory (.skills/)

This directory contains instructional documentation, rules, guidelines, and behavioral patterns for specialized assistant capabilities (skills). 

> [!NOTE]
> This folder is non-executable and contains instructions rather than code. Code implementation details for tools and agents reside in the `backend/` and `core/` directories, while the operational instructions, system capabilities, and tool execution boundaries are defined here.

## Directory Structure

Add separate markdown files for each distinct capability or toolset:
- `coding_agent.md` - Instructions on writing, refactoring, and debugging code.
- `browser_automation.md` - Guidelines for safe and efficient web navigation/interaction.
- `macos_integration.md` - Rules for interacting with system APIs and local applications.
- `memory_management.md` - Guidelines for long-term and semantic memory indexing.

## Creating a New Skill Instruction File

When adding instruction sets for new skills, ensure they include:
1. **Description & Boundaries**: The clear scope of what the skill is allowed to do.
2. **Standard Workflows**: Step-by-step reasoning or planning models for the skill.
3. **Safety & Permission Levels**: Guidelines on which actions require explicit user confirmation (e.g., deleting files, modifying system settings).
4. **Error Handling**: Expected recovery patterns if the capability encounters an issue.
