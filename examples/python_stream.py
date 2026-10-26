#!/usr/bin/env python3
"""Streaming call with token accounting.

    pip install openai
    export ADZUKI_API_KEY="sk-..."
    python examples/python_stream.py "Write a haiku about caches"

Streaming matters for two reasons beyond latency: the first token arrives while
the model is still thinking, and `stream_options={"include_usage": True}` gets
you the billed token counts in the final chunk.
"""
import os

from openai import OpenAI

client = OpenAI(
    base_url=os.environ.get("ADZUKI_BASE_URL", "https://adzukiai.com/v1"),
    api_key=os.environ["ADZUKI_API_KEY"],
)

stream = client.chat.completions.create(
    model=os.environ.get("ADZUKI_MODEL", "deepseek-v4.1-flash"),
    messages=[{"role": "user", "content": "Write a haiku about prompt caching."}],
    stream=True,
    stream_options={"include_usage": True},
)

usage = None
for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
    if chunk.usage:                      # only present on the final chunk
        usage = chunk.usage

print()
if usage:
    print(f"billed: {usage.prompt_tokens:,} prompt / {usage.completion_tokens:,} output")
