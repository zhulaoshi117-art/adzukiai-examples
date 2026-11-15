# Most requests don't need your most expensive model

We route each request to the right model automatically now. I think that matters more than another benchmark score.

---

The awkward part of buying frontier models: the best model is also the most expensive, and it's overkill for most of what you send it.

Translate one sentence with DeepSeek-V4-Pro and you paid flagship pricing for something a flash model does fine. Point the cheap model at a hard debugging session and you get a wrong answer you then pay twice to fix.

Adzuki AI is an OpenAI-compatible gateway for Chinese frontier models (DeepSeek, Qwen, GLM, Kimi, Doubao, MiniMax, MiMo), billed per token in USD. The last few weeks we've been trying to answer one thing: can the gateway pick the model for you, better than you'd pick it yourself, without you having to think about it?

That's **adzukiai-smart**, the routing layer. This is a short note on what it does, what it's actually done in production, and who it's for.

## The problem

Model-selection advice is usually a list of rules you have to remember and re-apply on every call. Nobody actually does that. What happens instead:

1. You default to the flagship for everything because it's the safe choice. Bill ends up several times larger than it needs to be.
2. Or you route by gut feel, send a hard request to a weak model, and ship a bad answer.

Same failure either way: the model and the task don't match.

adzukiai-smart makes that match on every request. You can see what it picked, but you don't have to manage it.

## How it works

A request goes through three gates before it reaches a model. Each one is cheaper than the next, so the common cases cost almost nothing to decide.

**Gate 1, length.** If the request is near the model's context limit, it goes straight to the flagship, forwarded untouched. We don't second-guess a model's advertised context window.

**Gate 2, rules.** A small set of hard patterns looks only at the latest user message. "Write a function that…", "debug this…", "analyze the trade-offs…" go to the flagship. "Translate…", "summarize…", "hi" go to flash. Free and deterministic, no model call.

**Gate 3, semantics.** If the rules can't decide, a flash model reads the request and labels it. One cheap call, and it only runs on whatever the rules couldn't place.

Underneath all three there's a safety net: if the chosen model errors, the request is retried on the other model before it ever fails. Six requests have been saved that way since launch.

One design choice worth noting: the judge is the cheap model, not the expensive one. The classifier never spends flagship tokens, so the routing layer can't eat the savings it's supposed to create.

You can see which model actually served a request through the `X-Routed-Model` response header, without changing your client.

## What it did in production

Since launch, adzukiai-smart has handled **415 requests**. The split:

- **40% to flash** — simple requests that never touched a flagship.
- **60% to flagship** — the ones that actually earned it.

The 40% is the interesting part. A human defaulting to "the best model" sends those to the flagship. They ran on flash instead.

On price: DeepSeek-V4-Pro outputs at **$1.36 per million tokens**, DeepSeek-V4.1-Flash at **$0.28** — about **5× cheaper**. Output dominates the bill because output costs several times input on every model in the catalogue. So a simple request on flash costs roughly a fifth of what it would have on the flagship.

I won't publish a "you saved $X" number, because the honest version depends on your token mix and I'm not going to make one up. The number I can state: 40% of requests went to a model about 5× cheaper on output, with no human in the loop.

## Who it's for

adzukiai-smart is for developers who want model selection without doing the chore. It's a default you set once, not a benchmark to chase.

Routing policy changes cost and quality in ways that depend on your traffic, so we turn it on per account rather than flipping everyone at once. If you want it:

- Talk to us and we'll tune the split to your traffic.
- The homepage at [adzukiai.com](https://adzukiai.com/) is where you reach us.

## Caveats

- **Inference runs in mainland China.** Your prompt leaves the US or EU when you call these models. Account and billing data stay in the US and EU. If your workload can't cross that boundary, none of this applies to you.
- **DeepSeek models are restricted for U.S. federal use.** Federal civilian agencies, the DoD, the IC, and their contractors may not procure or use DeepSeek technology, including through a gateway. This does not cover GLM, Kimi, or Doubao.
- **Routing is a cost/quality trade-off, not magic.** A flash model can still get a "simple" request wrong. The gates minimize that, but the final judge is you, on your own traffic.
- **Adzuki AI is a gateway, not a model provider.** Model names and logos belong to their respective owners.

---

Field note, not a benchmark. Routing numbers are from our production logs; prices come from the machine-readable list the gateway serves at [adzukiai.com/pricing.json](https://adzukiai.com/pricing.json), refreshed from one source so they don't drift.
