"""
SafePlate Telemetry Module: Sentry Agent Tracing & AI Observability.

Provides high-resolution tracing for multi-step AI agent workflows, capturing
hierarchical spans for pipelines, tool calls, and LLM completions with token,
latency, and cost accounting.
"""

import os
import time
from contextlib import contextmanager
from typing import Any, Dict, Optional
import sentry_sdk
from sentry_sdk.tracing import Span

# Initialize Sentry if DSN is set
SENTRY_DSN = os.getenv("SENTRY_DSN", "")

IS_SENTRY_ENABLED = bool(SENTRY_DSN and not SENTRY_DSN.startswith("mock://"))

if IS_SENTRY_ENABLED:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=1.0,
        send_default_pii=True,
        _experiments={
            "ai_monitoring": True,
        },
        release="safeplate@0.1.0",
        environment=os.getenv("ENVIRONMENT", "development"),
    )

# Local in-memory trace metrics collector for reporting & benchmarks
class LocalTraceMetrics:
    def __init__(self):
        self.spans = []
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_latency_ms = 0.0
        self.tool_calls_count = 0

    def reset(self):
        self.spans.clear()
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_latency_ms = 0.0
        self.tool_calls_count = 0

    def record_span(self, op: str, description: str, duration_ms: float, data: Dict[str, Any]):
        self.spans.append({
            "op": op,
            "description": description,
            "duration_ms": duration_ms,
            "data": data,
        })
        self.total_latency_ms += duration_ms

    def record_llm(self, prompt_tokens: int, completion_tokens: int):
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens

metrics = LocalTraceMetrics()


@contextmanager
def trace_agent_pipeline(pipeline_name: str, input_prompt: str, user_id: str = "elena"):
    """
    Root span representing the end-to-end agent task (ai.pipeline).
    """
    start_time = time.perf_counter()
    span_data = {
        "pipeline.name": pipeline_name,
        "pipeline.input": input_prompt,
        "user.id": user_id,
        "ai.framework": "safeplate-agent-engine",
    }
    
    if IS_SENTRY_ENABLED:
        with sentry_sdk.start_transaction(op="ai.pipeline", name=pipeline_name) as transaction:
            transaction.set_data("pipeline.name", pipeline_name)
            transaction.set_data("pipeline.input", input_prompt)
            transaction.set_tag("user.id", user_id)
            try:
                yield transaction
            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                metrics.record_span("ai.pipeline", pipeline_name, duration_ms, span_data)
    else:
        try:
            yield None
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.record_span("ai.pipeline", pipeline_name, duration_ms, span_data)


@contextmanager
def trace_tool_call(tool_name: str, arguments: Dict[str, Any]):
    """
    Span tracking individual agent tool execution (ai.tool_call).
    """
    start_time = time.perf_counter()
    span_data = {
        "tool.name": tool_name,
        "tool.arguments": arguments,
    }
    metrics.tool_calls_count += 1

    if IS_SENTRY_ENABLED:
        with sentry_sdk.start_span(op="ai.tool_call", description=f"tool:{tool_name}") as span:
            span.set_data("tool.name", tool_name)
            span.set_data("tool.arguments", arguments)
            try:
                yield span
            except Exception as e:
                span.set_data("tool.error", str(e))
                sentry_sdk.capture_exception(e)
                raise
            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                metrics.record_span("ai.tool_call", tool_name, duration_ms, span_data)
    else:
        try:
            yield None
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.record_span("ai.tool_call", tool_name, duration_ms, span_data)


@contextmanager
def trace_llm_inference(
    model: str,
    prompt: str,
    temperature: float = 0.2,
    estimated_prompt_tokens: int = 0,
    estimated_completion_tokens: int = 0,
    cost_usd: float = 0.0,
):
    """
    Span tracking LLM generation / reasoning inference (ai.chat_completions.create).
    """
    start_time = time.perf_counter()
    metrics.record_llm(estimated_prompt_tokens, estimated_completion_tokens)

    span_data = {
        "gen_ai.system": "open-weights",
        "gen_ai.request.model": model,
        "gen_ai.request.temperature": temperature,
        "gen_ai.usage.prompt_tokens": estimated_prompt_tokens,
        "gen_ai.usage.completion_tokens": estimated_completion_tokens,
        "gen_ai.usage.total_tokens": estimated_prompt_tokens + estimated_completion_tokens,
        "gen_ai.cost": cost_usd,
    }

    if IS_SENTRY_ENABLED:
        with sentry_sdk.start_span(op="ai.chat_completions.create", description=f"inference:{model}") as span:
            for k, v in span_data.items():
                span.set_data(k, v)
            try:
                yield span
            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                metrics.record_span("ai.chat_completions.create", model, duration_ms, span_data)
    else:
        try:
            yield None
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.record_span("ai.chat_completions.create", model, duration_ms, span_data)
