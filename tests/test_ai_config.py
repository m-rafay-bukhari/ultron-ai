import json
from typing import Any
import pytest
from pydantic import ValidationError
from services.ai import (
    ModelConfigLoader,
    AIConfig,
)


def test_config_loading_defaults() -> None:
    """Verify that configuration loads standard out-of-the-box defaults."""
    loader = ModelConfigLoader()
    config = loader.get_config()

    assert config.default_model == "ollama-llama3"
    assert config.ollama.api_base == "http://localhost:11434"
    assert config.openai.api_key is None
    assert config.openai.timeout == 30.0


def test_config_loading_file(tmp_path: Any) -> None:
    """Verify that configuration parses valid properties from a JSON file."""
    config_data = {
        "default_model": "custom-model",
        "openai": {"api_key": "file-key", "timeout": 45.0},
        "ollama": {"api_base": "http://10.0.0.1:11434"},
    }
    config_file = tmp_path / "ai_config.json"
    config_file.write_text(json.dumps(config_data))

    loader = ModelConfigLoader(config_path=str(config_file))
    config = loader.get_config()

    assert config.default_model == "custom-model"
    assert config.openai.api_key == "file-key"
    assert config.openai.timeout == 45.0
    assert config.ollama.api_base == "http://10.0.0.1:11434"


def test_config_validation_error(tmp_path: Any) -> None:
    """Verify that invalid value types (e.g. timeout as bad string) trigger ValidationError."""
    config_data = {"openai": {"timeout": "not-a-float"}}
    config_file = tmp_path / "ai_config.json"
    config_file.write_text(json.dumps(config_data))

    with pytest.raises(ValidationError):
        # Invalid configuration schema should propagate type validation error
        ModelConfigLoader(config_path=str(config_file))


def test_config_invalid_file_fallback(tmp_path: Any) -> None:
    """Verify that a malformed JSON file does not crash the loader, falling back to defaults."""
    config_file = tmp_path / "malformed_config.json"
    config_file.write_text("{invalid json: [")

    # Should log warning but proceed using defaults
    loader = ModelConfigLoader(config_path=str(config_file))
    config = loader.get_config()

    assert config.default_model == "ollama-llama3"
    assert config.ollama.api_base == "http://localhost:11434"


def test_config_environment_overrides(monkeypatch: Any) -> None:
    """Verify environmental variables override both defaults and file parameters."""
    monkeypatch.setenv("ULTRON_AI_DEFAULT_MODEL", "env-model")
    monkeypatch.setenv("ULTRON_AI_OPENAI__API_KEY", "env-secret-key")
    monkeypatch.setenv("ULTRON_AI_GEMINI__API_KEY", "gemini-secret-key")
    monkeypatch.setenv("ULTRON_AI_OLLAMA__TIMEOUT", "15.0")

    loader = ModelConfigLoader()
    config = loader.get_config()

    assert config.default_model == "env-model"
    assert config.openai.api_key == "env-secret-key"
    assert config.gemini.api_key == "gemini-secret-key"
    assert config.ollama.timeout == 15.0


def test_config_hot_reload(tmp_path: Any) -> None:
    """Verify configuration registers hot-reload callback correctly and updates values dynamically."""
    config_file = tmp_path / "reload_config.json"
    config_data = {"default_model": "initial-model"}
    config_file.write_text(json.dumps(config_data))

    loader = ModelConfigLoader(config_path=str(config_file))
    assert loader.get_config().default_model == "initial-model"

    reload_triggered = False
    new_model_value = ""

    def on_reload(new_config: AIConfig) -> None:
        nonlocal reload_triggered, new_model_value
        reload_triggered = True
        new_model_value = new_config.default_model

    loader.register_on_reload(on_reload)

    # Modify configuration file content
    updated_data = {"default_model": "updated-model"}
    config_file.write_text(json.dumps(updated_data))

    # Trigger hot-reload
    loader.reload()

    assert reload_triggered is True
    assert new_model_value == "updated-model"
    assert loader.get_config().default_model == "updated-model"
