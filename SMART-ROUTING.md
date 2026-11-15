# adzukiai-smart — automatic model routing

**adzukiai-smart** routes each `/v1/chat/completions` request to the cheapest model that can handle it, so simple traffic never pays flagship pricing.

This document describes the routing behavior. It is enabled **per account** — contact us through [adzukiai.com](https://adzukiai.com/) to turn it on.

## Model pool

| Role | Model |
|---|---|
| Flagship (complex requests) | `deepseek-v4-pro` |
| Flash (simple requests) | `deepseek-v4.1-flash` |

The split may be tuned per account based on your traffic.

## Routing decision

Every request passes through three gates, cheapest first:

### Gate 1 — length

If the estimated request size is at or above the context threshold, the request goes to the flagship model **and is forwarded unchanged**. The gateway does not pre-empt a model's advertised context window.

### Gate 2 — rules

Deterministic regex patterns look **only at the latest user message** (not the full history, so a long conversation can't pollute the signal).

- **Complex** → flagship: coding, debugging, algorithms, math/logic, professional analysis, long-form writing, multi-step tasks, questions about the model itself.
- **Simple** → flash: greetings, translation, rephrasing, short summarization.

If a rule matches, the decision is free — no model call.

### Gate 3 — semantics

If no rule matches, a flash model reads the request (last user turn, truncated) and labels it **simple** or **complex**. This is one cheap call, and it only runs on the ambiguous remainder.

The classifier is the *flash* model, never the flagship — so the routing layer cannot consume the savings it creates.

## Fallback

If the chosen model returns an error (HTTP ≥ 400 or an exception), the request is retried once on the other model. Only if both fail does the gateway return an error (`502`, `router_error`).

## Observing the decision

The response carries a header naming the model that actually served the request:

```
X-Routed-Model: deepseek-v4.1-flash
```

This lets you verify which model answered without changing your client.

## Wire compatibility

adzukiai-smart is drop-in compatible with the rest of the gateway. No client changes:

```
POST /v1/chat/completions
Authorization: Bearer $ADZUKI_API_KEY

{ "model": "deepseek-v4-pro", "messages": [...] }
```

The `model` field in the request is the *requested* model; the router may substitute the flash model when it judges the request simple. Streaming (`"stream": true`) works as normal.

## Production numbers

As of 2026-11-15:

| Metric | Value |
|---|---|
| Requests handled | 415 |
| Routed to flash (simple) | 40% |
| Routed to flagship (complex) | 60% |
| Fallback saves | 6 |

The headline saving comes from output pricing: `deepseek-v4-pro` outputs at **$1.36/M tokens** vs `deepseek-v4.1-flash` at **$0.28/M tokens** (~5×). Output dominates the bill on every model in the catalogue.

## Caveats

- Inference runs in mainland China; account and billing data stay in the US/EU.
- DeepSeek models are restricted for U.S. federal use (does not cover GLM, Kimi, Doubao).
- Routing is a cost/quality trade-off, not magic — measure it on your own traffic.
