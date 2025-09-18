"""Configuration management utilities."""

import json
import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from file.

    Args:
        config_path: Path to configuration file (YAML or JSON)

    Returns:
        Configuration dictionary
    """
    config = {}

    # Load environment variables
    load_dotenv()

    # Load default config
    default_config_path = Path(__file__).parent.parent / "config" / "default.yaml"
    if default_config_path.exists():
        with open(default_config_path, "r") as f:
            config = yaml.safe_load(f) or {}

    # Load user config if provided
    if config_path:
        config_path = Path(config_path)
        if config_path.exists():
            if config_path.suffix in [".yaml", ".yml"]:
                with open(config_path, "r") as f:
                    user_config = yaml.safe_load(f) or {}
            elif config_path.suffix == ".json":
                with open(config_path, "r") as f:
                    user_config = json.load(f)
            else:
                raise ValueError(f"Unsupported config format: {config_path.suffix}")

            # Merge configs
            config = merge_configs(config, user_config)

    # Override with environment variables
    config = override_with_env(config)

    return config


def save_config(config: Dict[str, Any], config_path: str) -> None:
    """
    Save configuration to file.

    Args:
        config: Configuration dictionary
        config_path: Path to save configuration
    """
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)

    if config_path.suffix in [".yaml", ".yml"]:
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
    elif config_path.suffix == ".json":
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
    else:
        raise ValueError(f"Unsupported config format: {config_path.suffix}")


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge two configuration dictionaries.

    Args:
        base: Base configuration
        override: Override configuration

    Returns:
        Merged configuration
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value

    return result


def override_with_env(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Override configuration with environment variables.

    Environment variables should be prefixed with VIDSCRIBE_

    Args:
        config: Configuration dictionary

    Returns:
        Configuration with environment overrides
    """
    env_prefix = "VIDSCRIBE_"

    for key, value in os.environ.items():
        if key.startswith(env_prefix):
            # Convert VIDSCRIBE_MODEL_SIZE to model.size
            config_key = key[len(env_prefix):].lower().replace("_", ".")
            keys = config_key.split(".")

            # Navigate to the right place in config
            current = config
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]

            # Set the value
            current[keys[-1]] = value

    return config


def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration.

    Returns:
        Default configuration dictionary
    """
    return {
        "model": {
            "size": "base",
            "device": None,
        },
        "download": {
            "output_dir": None,
            "keep_files": False,
        },
        "output": {
            "format": "text",
            "language": None,
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    }