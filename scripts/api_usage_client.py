#!/usr/bin/env python3
"""Record OpenAI-compatible response usage in Token Usage Monitor.

This helper extracts only provider/model/request identifiers and token counters.
It never sends prompts, response text, or API keys to the local monitor.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any
from urllib.request import Request, urlopen


DEFAULT_ENDPOINT = "http://127.0.0.1:47821/v1/usage"


def _mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    for method_name in ("model_dump", "dict"):
        method = getattr(value, method_name, None)
        if callable(method):
            rendered = method()
            if isinstance(rendered, Mapping):
                return dict(rendered)
    if value is None:
        return {}
    fields = (
        "input_tokens", "output_tokens", "prompt_tokens", "completion_tokens",
        "total_tokens", "cached_input_tokens", "prompt_cache_hit_tokens",
        "prompt_cache_miss_tokens", "input_tokens_details", "output_tokens_details",
        "completion_tokens_details", "reasoning_tokens",
    )
    return {name: getattr(value, name) for name in fields if getattr(value, name, None) is not None}


def build_usage_payload(
    provider: str,
    response: Any,
    *,
    task_name: str | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """Build the metadata-only payload accepted by the local monitor."""
    rendered = _mapping(response)
    usage = _mapping(rendered.get("usage") or getattr(response, "usage", None))
    if not usage:
        raise ValueError("The API response does not contain a usage object")
    resolved_model = model or rendered.get("model") or getattr(response, "model", None) or "unknown"
    request_id = rendered.get("id") or getattr(response, "id", None)
    payload: dict[str, Any] = {
        "provider": provider,
        "model": str(resolved_model),
        "usage": usage,
        "source": "api_usage_client",
    }
    if task_name:
        payload["task_name"] = task_name
    if request_id:
        payload["request_id"] = str(request_id)
    return payload


def record_response_usage(
    provider: str,
    response: Any,
    *,
    task_name: str | None = None,
    model: str | None = None,
    endpoint: str = DEFAULT_ENDPOINT,
    timeout: float = 3.0,
) -> dict[str, Any]:
    """Send token counters from one completed API response to the local app."""
    payload = build_usage_payload(provider, response, task_name=task_name, model=model)
    request = Request(
        endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=timeout) as result:
        return json.loads(result.read().decode("utf-8"))

