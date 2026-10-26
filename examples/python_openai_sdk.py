#!/usr/bin/env python3
"""One Chat Completions call through Adzuki AI, using the official OpenAI SDK.

    pip install openai
    export ADZUKI_API_KEY="sk-..."          # https://adzukiai.com -> API keys
    python examples/python_openai_sdk.py "Explain B-tree splits"

Nothing about the SDK changes: only base_url and api_key. That is the whole point
of an OpenAI-compatible gateway.
"""
import os
import sys

from openai import OpenAI

client = OpenAI(
    base_url=os.environ.get("ADZUKI_BASE_URL", "https://adzukiai.com/v1"),
    api_key=os.environ["ADZUKI_API_KEY"],
)

prompt = " ".join(sys.argv[1:]).strip() or "Explain B-tree splits in two sentences."

resp = client.chat.completions.create(
    model=os.environ.get("ADZUKI_MODEL", "deepseek-v4.1-flash"),
    messages=[{"role": "user", "content": prompt}],
)

print(resp.choices[0].message.content)

# Usage is what you get billed on. cached_tokens is the part of the prompt the
# vendor served from its prompt cache, which is priced far below fresh input.
u = resp.usage
cached = getattr(getattr(u, "prompt_tokens_details", None), "cached_tokens", 0) or 0
print()
print(f"prompt   {u.prompt_tokens:>8,} tokens ({cached:,} cached)")
print(f"output   {u.completion_tokens:>8,} tokens")
