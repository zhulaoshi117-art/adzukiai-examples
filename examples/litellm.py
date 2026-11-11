#!/usr/bin/env python3
"""Call Adzuki AI through LiteLLM, the open-source gateway/SDK.

    pip install litellm
    export ADZUKI_API_KEY="sk-..."          # https://adzukiai.com -> API keys
    python examples/litellm.py "Explain B-tree splits"

LiteLLM speaks the OpenAI wire format, so Adzuki AI works as a drop-in
"openai/" provider: point api_base at the gateway and pass an api_key.
You get LiteLLM's cost tracking, retries and fallbacks for free on top.
"""
import os
import sys

from litellm import completion

prompt = " ".join(sys.argv[1:]).strip() or "Explain B-tree splits in two sentences."

resp = completion(
    model="openai/" + os.environ.get("ADZUKI_MODEL", "deepseek-v4.1-flash"),
    messages=[{"role": "user", "content": prompt}],
    api_base=os.environ.get("ADZUKI_BASE_URL", "https://adzukiai.com/v1"),
    api_key=os.environ["ADZUKI_API_KEY"],
)

print(resp.choices[0].message.content)

# LiteLLM returns usage in the OpenAI shape; cached tokens are billed separately
# and are far cheaper than fresh input.
u = resp.usage
cached = getattr(getattr(u, "prompt_tokens_details", None), "cached_tokens", 0) or 0
print()
print(f"prompt   {u.prompt_tokens:>8,} tokens ({cached:,} cached)")
print(f"output   {u.completion_tokens:>8,} tokens")
