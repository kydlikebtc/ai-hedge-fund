"""
Model configuration management for AI providers.
Handles loading and validation of model configurations from YAML files.
"""

from typing import Dict, Any, Optional
import os
import yaml
from ..providers import (
    BaseProvider,
    OpenAIProvider,
    AnthropicProvider
)

class ConfigurationError(Exception):
    """Raised when configuration loading or validation fails."""
    pass

class ModelConfig:
    """Manages model configurations for different AI providers."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize model configuration from YAML file.

        Args:
            config_path: Path to YAML configuration file (optional)

        Raises:
            ConfigurationError: If configuration loading or validation fails
        """
        self.config_path = config_path or os.path.join("config", "crypto_models.yaml")
        self.config = self._load_config()
        self._validate_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.

        Returns:
            Dict containing provider configurations

        Raises:
            ConfigurationError: If file loading fails
        """
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise ConfigurationError(f"Failed to load config from {self.config_path}: {str(e)}")

    def _validate_config(self) -> None:
        """
        Validate configuration structure.

        Raises:
            ConfigurationError: If configuration is invalid
        """
        if not isinstance(self.config, dict):
            raise ConfigurationError("Configuration must be a dictionary")

        if 'providers' not in self.config:
            raise ConfigurationError("Configuration must have 'providers' section")

        for provider, settings in self.config['providers'].items():
            if 'default_model' not in settings:
                raise ConfigurationError(f"Provider {provider} missing 'default_model'")
            if 'models' not in settings:
                raise ConfigurationError(f"Provider {provider} missing 'models' list")
            if not isinstance(settings['models'], list):
                raise ConfigurationError(f"Provider {provider} 'models' must be a list")

            # Validate token limits for Claude-3.5 models
            if provider == 'anthropic' and 'settings' in settings:
                max_tokens = settings['settings'].get('max_tokens', 4096)
                if any('-3-5-' in model for model in settings['models']) and max_tokens < 8192:
                    raise ConfigurationError(f"Claude-3.5 models require max_tokens >= 8192")

    def _validate_model_name(self, provider: str, model_name: str) -> str:
        """
        Validate and potentially transform model name.

        Args:
            provider: Provider name
            model_name: Model identifier

        Returns:
            Validated model name

        Raises:
            ConfigurationError: If model name is invalid
        """
        provider_config = self.get_provider_config(provider)

        if provider == 'anthropic':
            # Handle latest aliases
            if model_name.endswith('-latest'):
                base_model = model_name.replace('-latest', '')
                if any(m.startswith(base_model) for m in provider_config['models']):
                    return model_name
            # Validate specific model version
            if model_name not in provider_config['models']:
                raise ConfigurationError(f"Invalid model name for {provider}: {model_name}")
        return model_name

    def get_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """
        Get configuration for specific provider.

        Args:
            provider_name: Name of the provider

        Returns:
            Provider configuration dictionary

        Raises:
            ConfigurationError: If provider not found
        """
        if provider_name not in self.config['providers']:
            raise ConfigurationError(f"Provider {provider_name} not found in configuration")
        return self.config['providers'][provider_name]

    def get_default_model(self, provider_name: str) -> str:
        """
        Get default model for provider.

        Args:
            provider_name: Name of the provider

        Returns:
            Default model identifier

        Raises:
            ConfigurationError: If provider not found
        """
        return self.get_provider_config(provider_name)['default_model']

def get_model_provider(
    provider_name: str = "openai",
    model: Optional[str] = None,
    config_path: Optional[str] = None
) -> BaseProvider:
    """
    Factory function to create model provider instance.

    Args:
        provider_name: Name of the provider (default: "openai")
        model: Model identifier (optional)
        config_path: Path to configuration file (optional)

    Returns:
        BaseProvider instance

    Raises:
        ConfigurationError: If provider creation fails
    """
    try:
        config = ModelConfig(config_path)
        provider_config = config.get_provider_config(provider_name)
        model_name = model or provider_config['default_model']

        # Validate model name
        model_name = config._validate_model_name(provider_name, model_name)

        if provider_name == "openai":
            return OpenAIProvider(
                model_name=model_name,
                settings=provider_config.get('settings', {})
            )
        elif provider_name == "anthropic":
            return AnthropicProvider(
                model_name=model_name,
                settings=provider_config.get('settings', {})
            )
        else:
            raise ConfigurationError(f"Unsupported provider: {provider_name}")
    except Exception as e:
        raise ConfigurationError(f"Failed to create provider {provider_name}: {str(e)}")
