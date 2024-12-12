"""
Base classes and error handling for AI model providers.
"""
from typing import Any, Dict, Optional


class ModelProviderError(Exception):
    """Base exception class for model provider errors."""
    def __init__(self, message: str, provider: Optional[str] = None):
        self.provider = provider
        super().__init__(f"[{provider or 'Unknown Provider'}] {message}")


class ResponseValidationError(ModelProviderError):
    """Exception raised when provider response validation fails."""
    def __init__(self, message: str, provider: Optional[str] = None, response: Any = None):
        self.response = response
        super().__init__(message, provider)


class ProviderConnectionError(ModelProviderError):
    """Exception raised when connection to provider fails."""
    def __init__(self, message: str, provider: Optional[str] = None, retry_count: int = 0):
        self.retry_count = retry_count
        super().__init__(message, provider)


class ProviderAuthenticationError(ModelProviderError):
    """Exception raised when provider authentication fails."""
    pass


class ProviderQuotaError(ModelProviderError):
    """Exception raised when provider quota is exceeded."""
    def __init__(self, message: str, provider: Optional[str] = None, quota_reset_time: Optional[str] = None):
        self.quota_reset_time = quota_reset_time
        super().__init__(message, provider)


class BaseProvider:
    """Base class for AI model providers."""

    def __init__(self, model_name: str = None, settings: Dict[str, Any] = None):
        self.model_name = model_name
        self.settings = settings or {}
        self._initialize_provider()

    def _initialize_provider(self) -> None:
        """Initialize the provider client and validate settings."""
        raise NotImplementedError("Provider must implement _initialize_provider")

    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a response from the model."""
        raise NotImplementedError("Provider must implement generate_response")

    def validate_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and parse the model's response."""
        try:
            # Handle both content-wrapped and direct JSON responses
            if isinstance(response, dict) and "content" in response:
                content = response["content"]
                metadata = response.get("metadata", {})
            else:
                content = response
                metadata = {
                    "model": self.model_name,
                    "provider": self.__class__.__name__,
                    "token_count": len(str(response)) // 4,  # Approximate token count
                    "timestamp": "2024-03-01T12:00:00Z"
                }

            # Parse JSON content
            if isinstance(content, str):
                import json
                parsed = json.loads(content)
            else:
                parsed = content

            # Validate response structure
            if not isinstance(parsed, dict):
                raise ResponseValidationError(
                    "Response must be a JSON object",
                    provider=self.__class__.__name__,
                    response=response
                )

            # Add metadata to each response type
            if "sentiment_analysis" in parsed:
                parsed["sentiment_analysis"]["metadata"] = metadata
            elif "risk_assessment" in parsed:
                parsed["risk_assessment"]["metadata"] = metadata
            elif "trading_decision" in parsed:
                parsed["trading_decision"]["metadata"] = metadata

            return parsed
        except json.JSONDecodeError as e:
            raise ResponseValidationError(
                f"Failed to parse response as JSON: {str(e)}",
                provider=self.__class__.__name__,
                response=response
            )

    def _handle_provider_error(self, error: Exception, retry_count: int = 0) -> None:
        """Handle provider-specific errors and implement fallback logic."""
        if isinstance(error, ProviderConnectionError) and retry_count < 3:
            # Implement exponential backoff
            import time
            time.sleep(2 ** retry_count)
            return self.generate_response(
                system_prompt="Retry after connection error",
                user_prompt="Please try again"
            )
        elif isinstance(error, ProviderQuotaError):
            # Try fallback provider if quota exceeded
            from src.config import get_model_provider
            fallback_provider = get_model_provider("openai")  # Default fallback
            return fallback_provider.generate_response(
                system_prompt="Fallback after quota error",
                user_prompt="Please try again"
            )
        else:
            raise error
