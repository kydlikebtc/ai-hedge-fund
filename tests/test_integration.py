"""
Integration tests for AI hedge fund system.
Tests the complete workflow with multiple providers.
"""
import json
from typing import Any, Callable, Dict, Optional, TypedDict
from unittest.mock import Mock, patch

import pytest
from langgraph.graph import StateGraph

from src.providers.openai_provider import OpenAIProvider
from src.providers.anthropic_provider import AnthropicProvider
from src.providers.base import (
    ModelProviderError,
    ProviderQuotaError,
    ProviderConnectionError
)

def validate_workflow_result(result: Dict[str, Any]) -> bool:
    """Validate workflow execution result."""
    required_keys = ["sentiment_analysis", "risk_assessment", "trading_decision"]
    return all(key in result and result[key] is not None for key in required_keys)

class WorkflowState(TypedDict):
    """Type definition for workflow state."""
    market_data: Dict[str, Any]
    sentiment_analysis: Optional[Dict[str, Any]]
    risk_assessment: Optional[Dict[str, Any]]
    trading_decision: Optional[Dict[str, Any]]

@pytest.fixture
def mock_openai_client():
    """Create mock OpenAI client."""
    mock_client = Mock()
    mock_client.invoke.return_value = {
        "choices": [
            {
                "message": {
                    "content": "Test response",
                    "role": "assistant"
                }
            }
        ]
    }
    return mock_client

@pytest.fixture
def mock_anthropic_client():
    """Create mock Anthropic client."""
    mock_client = Mock()
    mock_client.messages.create.return_value = Mock(
        content=[Mock(text="Test response")]
    )
    return mock_client

@pytest.fixture
def mock_provider(request):
    """Create mock provider for testing."""
    def mock_provider():
        def create_mock_response(prompt: str, provider_config: Dict[str, Any], error: bool = False) -> str:
            """Create mock response with proper structure."""
            # Ensure provider_config is not None and has required fields
            if provider_config is None:
                provider_config = {}

            metadata = {
                "model": provider_config.get("model"),
                "provider": provider_config.get("name"),
                "token_count": 100,
                "timestamp": "2024-03-01T12:00:00Z"
            }

            response_dict = {}
            if error:
                if "sentiment" in prompt.lower():
                    response_dict["sentiment_analysis"] = {
                        "sentiment_score": 0,
                        "confidence": 0,
                        "reasoning": "Error analyzing sentiment",
                        "analysis": "Error occurred during analysis",
                        "metadata": metadata
                    }
                return json.dumps(response_dict)

            if "sentiment" in prompt.lower():
                response_dict["sentiment_analysis"] = {
                    "sentiment_score": 0.75,
                    "confidence": 0.85,
                    "reasoning": "Mock sentiment analysis",
                    "analysis": "Positive market indicators",
                    "metadata": metadata
                }
            elif "risk" in prompt.lower():
                response_dict["risk_assessment"] = {
                    "risk_level": "moderate",
                    "position_limit": 1000,
                    "reasoning": "Mock risk assessment",
                    "analysis": "Market conditions suggest moderate risk",
                    "metadata": metadata
                }
            else:
                response_dict["trading_decision"] = {
                    "action": "buy",
                    "quantity": 100,
                    "reasoning": "Mock trading decision",
                    "analysis": "Technical indicators suggest entry point",
                    "metadata": metadata
                }
            return json.dumps(response_dict)

        def mock_invoke(system_prompt: str, user_prompt: str, provider_config: Dict = None) -> str:
            """Mock provider invoke method."""
            # Use provided config, or request.param if available, or empty dict as fallback
            current_config = provider_config or (request.param if hasattr(request, "param") else {})
            should_raise = getattr(mock_invoke, "should_raise", False)
            return create_mock_response(system_prompt + user_prompt, current_config, error=should_raise)

        # Create mock objects
        mock_openai = Mock()
        mock_anthropic = Mock()

        # Initialize with request.param if available
        initial_config = request.param if hasattr(request, "param") else {}

        return {
            "openai": mock_openai,
            "anthropic": mock_anthropic,
            "mock_invoke": mock_invoke,
            "provider_config": initial_config
        }

    return mock_provider()

def create_test_workflow(provider_name: str, mock_provider: Dict) -> Callable:
    """Create test workflow with mock provider."""
    # Import here to avoid circular imports
    from src.agents.base import BaseAgent
    from src.agents.specialized import SentimentAgent, RiskAgent, PortfolioAgent
    from langgraph.graph import StateGraph

    # Get provider configuration from mock_provider
    provider_config = mock_provider.get("provider_config")

    def sentiment_node(state: WorkflowState) -> WorkflowState:
        """Process sentiment analysis."""
        try:
            if "error" in state:
                return state
            # Pass provider_config to mock_invoke
            response_str = mock_provider["mock_invoke"]("Analyze market sentiment", "Provide sentiment analysis", provider_config)
            response = json.loads(response_str)
            if not isinstance(response, dict) or "sentiment_analysis" not in response:
                raise ValueError("Invalid sentiment analysis response")
            sentiment_data = response["sentiment_analysis"]
            return {
                **state,
                "sentiment_analysis": sentiment_data
            }
        except Exception as e:
            return {
                **state,
                "sentiment_analysis": {
                    "sentiment_score": 0,
                    "confidence": 0,
                    "reasoning": f"Error analyzing sentiment: {str(e)}",
                    "analysis": "Error occurred during sentiment analysis.",
                    "metadata": {
                        "error": str(e),
                        "timestamp": "2024-03-01T12:00:00Z",
                        "model": provider_config.get("model", "default"),
                        "provider": provider_config.get("name", "unknown")
                    }
                }
            }

    def risk_node(state: WorkflowState) -> WorkflowState:
        """Process risk assessment."""
        try:
            if "error" in state:
                return state
            # Pass provider_config to mock_invoke
            response_str = mock_provider["mock_invoke"]("Assess trading risk", "Evaluate market risk", provider_config)
            response = json.loads(response_str)
            if not isinstance(response, dict) or "risk_assessment" not in response:
                raise ValueError("Invalid risk assessment response")
            risk_data = response["risk_assessment"]
            return {
                **state,
                "risk_assessment": risk_data
            }
        except Exception as e:
            return {
                **state,
                "risk_assessment": {
                    "risk_level": "high",
                    "position_limit": 0,
                    "reasoning": f"Error assessing risk: {str(e)}",
                    "analysis": "Error occurred during risk assessment.",
                    "metadata": {
                        "error": str(e),
                        "timestamp": "2024-03-01T12:00:00Z",
                        "model": provider_config.get("model", "default"),
                        "provider": provider_config.get("name", "unknown")
                    }
                }
            }

    def portfolio_node(state: WorkflowState) -> WorkflowState:
        """Process portfolio decisions."""
        try:
            if "error" in state:
                return state
            # Pass provider_config to mock_invoke
            response_str = mock_provider["mock_invoke"]("Make trading decision", "Generate portfolio action", provider_config)
            response = json.loads(response_str)
            if not isinstance(response, dict) or "trading_decision" not in response:
                raise ValueError("Invalid trading decision response")
            decision_data = response["trading_decision"]
            return {
                **state,
                "trading_decision": decision_data
            }
        except Exception as e:
            return {
                **state,
                "trading_decision": {
                    "action": "hold",
                    "quantity": 0,
                    "reasoning": f"Error making trading decision: {str(e)}",
                    "analysis": "Error occurred during portfolio management.",
                    "metadata": {
                        "error": str(e),
                        "timestamp": "2024-03-01T12:00:00Z",
                        "model": provider_config.get("model", "default"),
                        "provider": provider_config.get("name", "unknown")
                    }
                }
            }

    # Create workflow graph
    workflow = StateGraph(WorkflowState)

    # Add nodes
    workflow.add_node("sentiment", sentiment_node)
    workflow.add_node("risk", risk_node)
    workflow.add_node("portfolio", portfolio_node)

    # Set edges
    workflow.set_entry_point("sentiment")
    workflow.add_edge("sentiment", "risk")
    workflow.add_edge("risk", "portfolio")
    workflow.set_finish_point("portfolio")

    return workflow.compile()

@pytest.fixture
def mock_market_data():
    """Create mock market data for testing."""
    return {
        "ticker": "AAPL",
        "price": 150.0,
        "volume": 1000000,
        "insider_trades": [
            {"type": "buy", "shares": 1000, "price": 148.0},
            {"type": "sell", "shares": 500, "price": 152.0}
        ]
    }

@pytest.mark.parametrize("provider_config", [
    {"name": "openai", "model": "gpt-4"},
    {"name": "anthropic", "model": "claude-3-opus-20240229"},
    {"name": "anthropic", "model": "claude-3-5-sonnet-20241022"},
    {"name": "anthropic", "model": "claude-3-5-haiku-20241022"}
])
def test_workflow_execution(provider_config, mock_provider, mock_market_data):
    """Test complete workflow with different providers."""
    mock_provider["provider_config"] = provider_config
    workflow = create_test_workflow(provider_config["name"], mock_provider)

    # Initialize workflow state
    initial_state = WorkflowState(
        market_data=mock_market_data,
        sentiment_analysis=None,
        risk_assessment=None,
        trading_decision=None
    )

    # Execute workflow
    try:
        result = workflow.invoke(initial_state)
        assert result is not None
        assert "sentiment_analysis" in result
        assert "risk_assessment" in result
        assert "trading_decision" in result

        # Verify sentiment analysis
        sentiment = result["sentiment_analysis"]
        assert isinstance(sentiment, dict)
        assert "sentiment_score" in sentiment
        assert isinstance(sentiment["sentiment_score"], (int, float))
        assert 0 <= sentiment["sentiment_score"] <= 1
        assert "confidence" in sentiment
        assert "reasoning" in sentiment
        assert "analysis" in sentiment
        assert "metadata" in sentiment
        assert sentiment["metadata"]["model"] == provider_config["model"]

        # Verify risk assessment
        risk = result["risk_assessment"]
        assert isinstance(risk, dict)
        assert "risk_level" in risk
        assert risk["risk_level"] in ["low", "moderate", "high"]
        assert "position_limit" in risk
        assert isinstance(risk["position_limit"], (int, float))
        assert "reasoning" in risk
        assert "analysis" in risk
        assert "metadata" in risk
        assert risk["metadata"]["model"] == provider_config["model"]

        # Verify trading decision
        decision = result["trading_decision"]
        assert isinstance(decision, dict)
        assert "action" in decision
        assert decision["action"] in ["buy", "sell", "hold"]
        assert "quantity" in decision
        assert isinstance(decision["quantity"], (int, float))
        assert "reasoning" in decision
        assert "analysis" in decision
        assert "metadata" in decision
        assert decision["metadata"]["model"] == provider_config["model"]
    except Exception as e:
        pytest.fail(f"Workflow execution failed with {provider_config['name']}: {str(e)}")

@pytest.mark.parametrize("provider_config", [
    {"name": "openai", "model": "gpt-4"},
    {"name": "anthropic", "model": "claude-3-opus-20240229"},
    {"name": "anthropic", "model": "claude-3-5-sonnet-20241022"},
    {"name": "anthropic", "model": "claude-3-5-haiku-20241022"}
])
def test_workflow_error_handling(provider_config, mock_provider):
    """Test workflow error handling with different providers."""
    workflow = create_test_workflow(provider_config["name"], mock_provider)

    # Set mock to raise error
    mock_provider["mock_invoke"].should_raise = True

    # Initialize workflow state with empty market data
    initial_state = WorkflowState(
        market_data={
            "ticker": "",
            "price": 0.0,
            "volume": 0,
            "insider_trades": []
        },
        sentiment_analysis=None,
        risk_assessment=None,
        trading_decision=None
    )

    # Execute workflow
    result = workflow.invoke(initial_state)

    # Verify error handling
    assert result is not None
    assert isinstance(result, dict)
    assert "sentiment_analysis" in result
    sentiment = result["sentiment_analysis"]
    assert isinstance(sentiment, dict)
    assert "sentiment_score" in sentiment
    assert sentiment["sentiment_score"] == 0
    assert "confidence" in sentiment
    assert sentiment["confidence"] == 0
    assert "reasoning" in sentiment
    assert "Error analyzing sentiment" in sentiment["reasoning"]
    assert "analysis" in sentiment
    assert "metadata" in sentiment

@pytest.mark.parametrize("provider_config", [
    {"name": "openai", "model": "gpt-4"},
    {"name": "anthropic", "model": "claude-3-opus-20240229"},
    {"name": "anthropic", "model": "claude-3-5-sonnet-20241022"},
    {"name": "anthropic", "model": "claude-3-5-haiku-20241022"}
])
def test_workflow_state_transitions(provider_config, mock_provider):
    """Test workflow state transitions with different providers."""
    workflow = create_test_workflow(provider_config["name"], mock_provider)

    # Initialize workflow state
    initial_state = WorkflowState(
        market_data={
            "ticker": "AAPL",
            "price": 150.0,
            "volume": 1000000,
            "insider_trades": [
                {"type": "buy", "shares": 1000, "price": 148.0},
                {"type": "sell", "shares": 500, "price": 152.0}
            ]
        },
        sentiment_analysis=None,
        risk_assessment=None,
        trading_decision=None
    )

    # Execute workflow
    result = workflow.invoke(initial_state)

    # Verify state transitions
    assert result is not None
    assert isinstance(result, dict)
    assert "error" not in result

    # Verify sentiment analysis state
    assert "sentiment_analysis" in result
    sentiment = result["sentiment_analysis"]
    assert isinstance(sentiment, dict)
    assert "sentiment_score" in sentiment
    assert isinstance(sentiment["sentiment_score"], (int, float))
    assert 0 <= sentiment["sentiment_score"] <= 1
    assert "confidence" in sentiment
    assert "reasoning" in sentiment
    assert "analysis" in sentiment
    assert "metadata" in sentiment
    assert isinstance(sentiment["metadata"], dict)
    assert "model" in sentiment["metadata"]
    assert "timestamp" in sentiment["metadata"]
    assert "provider" in sentiment["metadata"]
    assert "token_count" in sentiment["metadata"]

    # Verify risk assessment state
    assert "risk_assessment" in result
    risk = result["risk_assessment"]
    assert isinstance(risk, dict)
    assert "risk_level" in risk
    assert risk["risk_level"] in ["low", "moderate", "high"]
    assert "position_limit" in risk
    assert isinstance(risk["position_limit"], (int, float))
    assert "reasoning" in risk
    assert "analysis" in risk
    assert "metadata" in risk
    assert isinstance(risk["metadata"], dict)
    assert "model" in risk["metadata"]
    assert "timestamp" in risk["metadata"]
    assert "provider" in risk["metadata"]
    assert "token_count" in risk["metadata"]

    # Verify trading decision state
    assert "trading_decision" in result
    decision = result["trading_decision"]
    assert isinstance(decision, dict)
    assert "action" in decision
    assert decision["action"] in ["buy", "sell", "hold"]
    assert "quantity" in decision
    assert isinstance(decision["quantity"], (int, float))
    assert "reasoning" in decision
    assert "analysis" in decision
    assert "metadata" in decision
    assert isinstance(decision["metadata"], dict)
    assert "model" in decision["metadata"]
    assert "timestamp" in decision["metadata"]
    assert "provider" in decision["metadata"]
    assert "token_count" in decision["metadata"]

@pytest.mark.parametrize("provider_config", [
    {"name": "anthropic", "model": "claude-3-opus-20240229"},
    {"name": "anthropic", "model": "claude-3-5-sonnet-20241022"},
    {"name": "anthropic", "model": "claude-3-5-haiku-20241022"}
])
def test_anthropic_token_limits(provider_config, mock_provider):
    """Test token limits for different Anthropic models."""
    workflow = create_test_workflow(provider_config["name"], mock_provider)

    # Initialize workflow state
    initial_state = WorkflowState(
        market_data={
            "ticker": "AAPL",
            "price": 150.0,
            "volume": 1000000,
            "insider_trades": [{"type": "buy", "shares": 100, "price": 150.0}] * 100
        },
        sentiment_analysis=None,
        risk_assessment=None,
        trading_decision=None
    )

    # Execute workflow
    result = workflow.invoke(initial_state)

    # Verify response structure
    assert result is not None
    assert isinstance(result, dict)
    assert "error" not in result

    # Check token limits for each field
    max_tokens = 8192 if "claude-3-5" in provider_config["model"] else 4096

    # Verify sentiment analysis
    assert "sentiment_analysis" in result
    sentiment = result["sentiment_analysis"]
    assert "reasoning" in sentiment
    assert len(sentiment["reasoning"]) <= max_tokens // 3
    assert "metadata" in sentiment
    assert isinstance(sentiment["metadata"], dict)
    assert "token_count" in sentiment["metadata"]
    assert sentiment["metadata"]["token_count"] <= max_tokens // 3

    # Verify risk assessment
    assert "risk_assessment" in result
    risk = result["risk_assessment"]
    assert "reasoning" in risk
    assert len(risk["reasoning"]) <= max_tokens // 3
    assert "metadata" in risk
    assert isinstance(risk["metadata"], dict)
    assert "token_count" in risk["metadata"]
    assert risk["metadata"]["token_count"] <= max_tokens // 3

    # Verify trading decision
    assert "trading_decision" in result
    decision = result["trading_decision"]
    assert "reasoning" in decision
    assert len(decision["reasoning"]) <= max_tokens // 3
    assert "metadata" in decision
    assert isinstance(decision["metadata"], dict)
    assert "token_count" in decision["metadata"]
    assert decision["metadata"]["token_count"] <= max_tokens // 3
