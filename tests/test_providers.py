"""
Tests for AI model providers.
"""

import pytest
from unittest.mock import Mock, patch
import json

from src.providers.base import (
    BaseProvider,
    ModelProviderError,
    ResponseValidationError,
    ProviderConnectionError,
    ProviderAuthenticationError,
    ProviderQuotaError
)
from src.providers.openai_provider import OpenAIProvider
from src.providers.anthropic_provider import AnthropicProvider

@patch('src.providers.openai_provider.ChatOpenAI')
def test_openai_provider_initialization(mock_chat_openai):
    """Test OpenAI provider initialization."""
    mock_client = Mock()
    mock_chat_openai.return_value = mock_client

    provider = OpenAIProvider(model_name="gpt-4")
    assert provider is not None
    assert provider.model_name == "gpt-4"
    assert isinstance(provider.settings, dict)
    assert provider.client == mock_client

@patch('src.providers.openai_provider.ChatOpenAI')
def test_openai_provider_response_generation(mock_chat_openai):
    """Test OpenAI provider response generation."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = json.dumps({
        "sentiment_analysis": {
            "sentiment_score": 0.8,
            "confidence": 0.9,
            "reasoning": "Test response"
        }
    })
    mock_client.invoke.return_value = mock_response
    mock_chat_openai.return_value = mock_client

    provider = OpenAIProvider(model_name="gpt-4")
    response = provider.generate_response(
        system_prompt="You are a test assistant.",
        user_prompt="Test prompt"
    )

    parsed = json.loads(response)
    assert "sentiment_analysis" in parsed
    assert parsed["sentiment_analysis"]["sentiment_score"] == 0.8
    assert parsed["sentiment_analysis"]["confidence"] == 0.9
    mock_client.invoke.assert_called_once()

@patch('src.providers.openai_provider.ChatOpenAI')
def test_openai_provider_response_validation(mock_chat_openai):
    """Test OpenAI provider response validation."""
    mock_client = Mock()
    mock_chat_openai.return_value = mock_client

    provider = OpenAIProvider(model_name="gpt-4")

    # Test valid JSON response
    valid_response = '{"key": "value"}'
    result = provider.validate_response(valid_response)
    assert isinstance(result, dict)
    assert result["key"] == "value"

    # Test invalid responses
    with pytest.raises(ResponseValidationError):
        provider.validate_response("")

    with pytest.raises(ResponseValidationError):
        provider.validate_response("Invalid JSON")

@patch('src.providers.openai_provider.ChatOpenAI')
def test_provider_error_handling(mock_chat_openai):
    """Test provider error handling."""
    mock_client = Mock()
    mock_chat_openai.return_value = mock_client

    provider = OpenAIProvider(model_name="gpt-4")

    # Test authentication error
    mock_client.invoke.side_effect = Exception("authentication failed")
    with pytest.raises(ProviderAuthenticationError):
        provider.generate_response(
            system_prompt="Test system prompt",
            user_prompt="Test user prompt"
        )

    # Test rate limit error
    mock_client.invoke.side_effect = Exception("rate limit exceeded")
    with pytest.raises(ProviderQuotaError):
        provider.generate_response(
            system_prompt="Test system prompt",
            user_prompt="Test user prompt"
        )

    # Test connection error
    mock_client.invoke.side_effect = Exception("connection failed")
    with pytest.raises(ProviderConnectionError):
        provider.generate_response(
            system_prompt="Test system prompt",
            user_prompt="Test user prompt"
        )

    # Test generic error
    mock_client.invoke.side_effect = Exception("unknown error")
    with pytest.raises(ModelProviderError):
        provider.generate_response(
            system_prompt="Test system prompt",
            user_prompt="Test user prompt"
        )

@patch('src.providers.anthropic_provider.ChatAnthropicMessages')
def test_anthropic_provider_initialization(mock_chat_anthropic):
    """Test Anthropic provider initialization."""
    mock_client = Mock()
    mock_chat_anthropic.return_value = mock_client

    # Test with claude-3.5-sonnet
    provider = AnthropicProvider(
        model_name="claude-3-5-sonnet-20241022",
        settings={
            'temperature': 0.7,
            'max_tokens': 8192
        }
    )
    assert provider is not None
    assert provider.model_name == "claude-3-5-sonnet-20241022"
    assert isinstance(provider.settings, dict)
    assert provider.client == mock_client

    # Test with claude-3.5-haiku
    provider = AnthropicProvider(
        model_name="claude-3-5-haiku-20241022",
        settings={
            'temperature': 0.7,
            'max_tokens': 8192
        }
    )
    assert provider is not None
    assert provider.model_name == "claude-3-5-haiku-20241022"
    assert isinstance(provider.settings, dict)
    assert provider.client == mock_client

    # Test with claude-3-opus
    provider = AnthropicProvider(
        model_name="claude-3-opus-20240229",
        settings={
            'temperature': 0.7,
            'max_tokens': 4096
        }
    )
    assert provider is not None
    assert provider.model_name == "claude-3-opus-20240229"

    # Test with claude-3-sonnet
    provider = AnthropicProvider(
        model_name="claude-3-sonnet-20240229",
        settings={
            'temperature': 0.7,
            'max_tokens': 4096
        }
    )
    assert provider is not None
    assert provider.model_name == "claude-3-sonnet-20240229"

@patch('src.providers.anthropic_provider.ChatAnthropicMessages')
def test_anthropic_provider_response_generation(mock_chat_anthropic):
    """Test Anthropic provider response generation."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = json.dumps({
        "response": "Test response",
        "analysis": "Sample analysis",
        "confidence": 0.8
    })
    mock_client.invoke.return_value = mock_response
    mock_chat_anthropic.return_value = mock_client

    provider = AnthropicProvider(
        model_name="claude-3-opus-20240229",
        settings={'temperature': 0.7}
    )
    response = provider.generate_response("System prompt", "Test prompt")

    parsed = json.loads(response)
    assert "response" in parsed
    assert parsed["response"] == "Test response"
    assert parsed["analysis"] == "Sample analysis"
    assert parsed["confidence"] == 0.8
    mock_client.invoke.assert_called_once()

@patch('src.providers.anthropic_provider.ChatAnthropicMessages')
def test_anthropic_provider_error_handling(mock_chat_anthropic):
    """Test Anthropic provider error handling."""
    mock_client = Mock()
    mock_chat_anthropic.return_value = mock_client

    provider = AnthropicProvider(
        model_name="claude-3-opus-20240229",
        settings={'temperature': 0.7}
    )

    # Test authentication error
    mock_client.invoke.side_effect = Exception("authentication failed")
    with pytest.raises(ProviderAuthenticationError):
        provider.generate_response("System prompt", "Test prompt")

    # Test rate limit error
    mock_client.invoke.side_effect = Exception("rate limit exceeded")
    with pytest.raises(ProviderQuotaError):
        provider.generate_response("System prompt", "Test prompt")

    # Test connection error
    mock_client.invoke.side_effect = Exception("connection failed")
    with pytest.raises(ProviderConnectionError):
        provider.generate_response("System prompt", "Test prompt")

    # Test generic error
    mock_client.invoke.side_effect = Exception("unknown error")
    with pytest.raises(ModelProviderError):
        provider.generate_response("System prompt", "Test prompt")

@patch('src.providers.anthropic_provider.ChatAnthropicMessages')
def test_anthropic_provider_token_limits(mock_chat_anthropic):
    """Test Anthropic provider token limit handling."""
    mock_client = Mock()
    mock_response = Mock()
    # Create a more realistic response length
    long_text = "Test response " * 200  # Approximately 2400 chars
    mock_response.content = long_text
    mock_client.invoke.return_value = mock_response
    mock_chat_anthropic.return_value = mock_client

    # Test Claude 3.5 token limit
    provider = AnthropicProvider(
        model_name="claude-3-5-sonnet-20241022",
        settings={
            'temperature': 0.7,
            'max_tokens': 8192
        }
    )
    response = provider.generate_response("System prompt", "Test prompt")
    parsed = json.loads(response)

    # Verify response format and length
    assert "response" in parsed
    assert len(parsed["response"]) <= 8192
    assert "format" in parsed
    assert parsed["format"] == "text"
    assert "metadata" in parsed
    assert parsed["metadata"]["model"] == "claude-3-5-sonnet-20241022"

    # Test Claude 3 token limit
    provider = AnthropicProvider(
        model_name="claude-3-opus-20240229",
        settings={
            'temperature': 0.7,
            'max_tokens': 4096
        }
    )
    response = provider.generate_response("System prompt", "Test prompt")
    parsed = json.loads(response)
    assert len(parsed["response"]) <= 4096
    assert "format" in parsed
    assert parsed["format"] == "text"
    assert "metadata" in parsed
    assert parsed["metadata"]["model"] == "claude-3-opus-20240229"
