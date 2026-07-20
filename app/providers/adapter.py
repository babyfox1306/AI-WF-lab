"""Provider adapter abstraction with OpenAI-compatible, Ollama, and mock implementations."""

import json
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ProviderResponse:
    """Normalized response from a provider adapter."""

    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    duration_ms: int = 0
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class ProviderError:
    """Normalized error from a provider adapter."""

    category: str  # authentication_error, rate_limit, timeout, connection_error, model_not_found, invalid_request, malformed_response, context_limit, unknown
    message: str
    retryable: bool = False


class BaseProviderAdapter(ABC):
    """Abstract base class for provider adapters."""

    def __init__(self, base_url: str, api_key: Optional[str] = None, model: Optional[str] = None, timeout: int = 120):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    @abstractmethod
    def test_connection(self) -> Tuple[bool, str, List[str]]:
        """Test the connection. Returns (success, message, models_list)."""
        ...

    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], **kwargs) -> ProviderResponse:
        """Generate a response from the provider."""
        ...

    def normalize_error(self, error: Exception) -> ProviderError:
        """Normalize an exception to a ProviderError."""
        import httpx
        if isinstance(error, httpx.TimeoutException):
            return ProviderError(category="timeout", message=f"Request timed out after {self.timeout}s", retryable=True)
        if isinstance(error, httpx.ConnectError):
            return ProviderError(category="connection_error", message=f"Cannot connect to {self.base_url}", retryable=True)
        if isinstance(error, httpx.HTTPStatusError):
            status = error.response.status_code
            if status == 401:
                return ProviderError(category="authentication_error", message="Invalid API key", retryable=False)
            if status == 429:
                return ProviderError(category="rate_limit", message="Rate limited", retryable=True)
            if status == 404:
                return ProviderError(category="model_not_found", message=f"Model not found at provider", retryable=False)
            if status >= 500:
                return ProviderError(category="unknown", message=f"Server error: {status}", retryable=True)
            return ProviderError(category="invalid_request", message=str(error), retryable=False)
        return ProviderError(category="unknown", message=str(error), retryable=False)

    def normalize_usage(self, usage: Optional[Dict[str, Any]]) -> Dict[str, int]:
        """Extract token usage from a provider response."""
        if not usage:
            return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        return {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }


class OpenAICompatibleAdapter(BaseProviderAdapter):
    """Adapter for OpenAI-compatible API providers."""

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def test_connection(self) -> Tuple[bool, str, List[str]]:
        import httpx
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(f"{self.base_url}/models", headers=self._headers())
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m.get("id", "") for m in data.get("data", [])][:50]
                    return True, "Connected", models
                return False, f"HTTP {resp.status_code}", []
        except Exception as e:
            err = self.normalize_error(e)
            return False, err.message, []

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> ProviderResponse:
        import httpx
        start = time.time()
        model = kwargs.get("model", self.model)
        body = {
            "model": model or "gpt-4o-mini",
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 4096),
        }
        if kwargs.get("response_format"):
            body["response_format"] = kwargs["response_format"]

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=body,
            )
            resp.raise_for_status()
            data = resp.json()
            duration = int((time.time() - start) * 1000)

        choice = data.get("choices", [{}])[0]
        content = choice.get("message", {}).get("content", "")
        usage = self.normalize_usage(data.get("usage"))
        return ProviderResponse(
            content=content,
            model=data.get("model", model or ""),
            duration_ms=duration,
            raw_response=data,
            **usage,
        )


class OllamaAdapter(BaseProviderAdapter):
    """Adapter for Ollama local API."""

    def test_connection(self) -> Tuple[bool, str, List[str]]:
        import httpx
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(f"{self.base_url}/api/tags")
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m.get("name", "") for m in data.get("models", [])][:50]
                    return True, "Ollama connected", models
                return False, f"HTTP {resp.status_code}", []
        except Exception as e:
            err = self.normalize_error(e)
            return False, err.message, []

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> ProviderResponse:
        import httpx
        start = time.time()
        model = kwargs.get("model", self.model) or "llama3.2"

        # Convert chat messages to Ollama format
        prompt = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt = f"System: {content}\n{prompt}"
            elif role == "user":
                prompt += f"User: {content}\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n"

        body = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "num_predict": kwargs.get("max_tokens", 4096),
            },
        }

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(f"{self.base_url}/api/generate", json=body)
            resp.raise_for_status()
            data = resp.json()
            duration = int((time.time() - start) * 1000)

        content = data.get("response", "")
        return ProviderResponse(
            content=content,
            model=model,
            duration_ms=duration,
            raw_response=data,
            prompt_tokens=data.get("prompt_eval_count", 0),
            completion_tokens=data.get("eval_count", 0),
            total_tokens=(data.get("prompt_eval_count", 0) + data.get("eval_count", 0)),
        )


class MockProviderAdapter(BaseProviderAdapter):
    """Mock provider for testing without real API calls."""

    def __init__(self, **kwargs):
        super().__init__(base_url="http://mock.local", api_key=None, timeout=5)
        self._mock_responses = kwargs.get("mock_responses", {})

    def test_connection(self) -> Tuple[bool, str, List[str]]:
        return True, "Mock provider ready", ["mock-model-v1", "mock-model-v2"]

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> ProviderResponse:
        import hashlib
        start = time.time()

        # Generate deterministic mock response based on input
        system_prompt = ""
        user_input = ""
        for msg in messages:
            if msg.get("role") == "system":
                system_prompt = msg.get("content", "")
            elif msg.get("role") == "user":
                user_input = msg.get("content", "")

        # Check for specific mock responses
        input_hash = hashlib.md5(user_input.encode()).hexdigest()[:8]
        if user_input in self._mock_responses:
            content = self._mock_responses[user_input]
        else:
            content = json.dumps({
                "mock_output": True,
                "input_hash": input_hash,
                "analysis": {
                    "summary": "This is a mock provider response for testing.",
                    "confidence": 0.85,
                    "processing_result": "simulated",
                },
                "extracted_entities": [],
                "recommendations": ["Review the mock output"],
            })

        import time as _time
        _time.sleep(0.05)  # Simulate minimal processing
        duration = int((time.time() - start) * 1000)

        return ProviderResponse(
            content=content,
            model="mock-provider-v1",
            prompt_tokens=len(system_prompt + user_input) // 4,
            completion_tokens=len(content) // 4,
            total_tokens=(len(system_prompt + user_input) + len(content)) // 4,
            duration_ms=duration,
        )


def get_adapter(provider_type: str, base_url: str, api_key: Optional[str] = None,
                model: Optional[str] = None, timeout: int = 120) -> BaseProviderAdapter:
    """Factory function to get the appropriate provider adapter."""
    if provider_type == "openai_compatible":
        return OpenAICompatibleAdapter(base_url=base_url, api_key=api_key, model=model, timeout=timeout)
    elif provider_type == "ollama":
        return OllamaAdapter(base_url=base_url, api_key=api_key, model=model, timeout=timeout)
    else:
        raise ValueError(f"Unsupported provider type: {provider_type}")
