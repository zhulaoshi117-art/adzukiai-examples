# Comparing 7 Chinese frontier models through one API — a field guide, not a benchmark

There are now a handful of Chinese labs shipping models that are genuinely
competitive with the Western frontier — DeepSeek, Qwen, GLM, Kimi, Doubao,
MiniMax, MiMo — and for a developer outside mainland China, they used to be a
hassle to even try: a Chinese phone number for real-name verification, a
separate account and invoice per vendor, RMB billing, and docs in Chinese.

Adzuki AI is one of the gateways that removes that friction: one OpenAI-compatible
endpoint, one API key, US-dollar per-token billing. I run it, so take the rest of
this with the appropriate grain of salt. What follows is not a benchmark — there
are no leaderboard scores here — it is a **field guide**: what each family of
models is *for*, how their pricing actually behaves, and how to pick one without
overpaying. Every price below is in USD per 1,000,000 tokens, pulled from the
same machine-readable list the gateway publishes.

## The lineup at a glance

| Family | Vendor | What it's known for | Price range (output) |
|---|---|---|---|
| DeepSeek | DeepSeek | Strong coding + math, extremely cheap cache | $2.29–$7.71 |
| Qwen | Alibaba | Best-in-class long context, tool use | $10.29 |
| GLM | Zhipu AI | General-purpose flagship, balanced | $0.80–$8.00 |
| Kimi | Moonshot AI | Very long context, premium output | $19.43–$28.57 |
| Doubao | ByteDance | Cheap, fast, good default for volume | $0.77–$8.57 |
| MiniMax | MiniMax | Long context at a mid price | $4.80 |
| MiMo | Xiaomi | Cheapest cache on the board | $0.57–$1.71 |

The pattern that jumps out immediately: **output is priced several times higher
than input on every single model.** That is the one fact that should shape your
whole choice, because most of your bill is what the model *generates*, not what
you *send*.

## The three decisions that actually matter

### 1. How much of your prompt is cacheable?

Prompt caching is where these models quietly diverge. MiMo charges **$0.0057**
per 1M cached input tokens — roughly 50x cheaper than fresh input. DeepSeek is
$0.0857, Qwen $0.4286, and Kimi $0.5714. The spread is an order of magnitude.

If your workload is a long system prompt + a big tool schema + a long document
you re-send on every turn (agents, RAG, code assistants), the cache price — not
the headline input price — is what you will actually pay. MiMo and DeepSeek are
built for that pattern. If your prompts are short and never repeat, ignore cache
pricing entirely; you will never hit it.

### 2. How long is your context really?

"Long context" is the most over-bought feature in this catalogue. DeepSeek-V4-Pro
advertises a 1M-token window; Qwen and Kimi are known for very long contexts too.
But a 1M-token window does not mean you should *use* it — attention gets
expensive fast, and the model is not equally reliable at token 900,000 as it is
at token 9,000.

For most production RAG, 32k–128k is plenty, and paying the premium-tier price of
Kimi to hold a context you will never fill is money left on the table. Buy the
long-context model only when you have measured that you actually need it.

### 3. Are you batch or latency-sensitive?

There is no peak/off-peak surcharge on the gateway — pricing is flat around the
clock. That is the trade-off: the upstream vendors *do* discount their own list
prices overnight (22:00–08:00 China time), but that discount is not passed through
here. If you have schedulable batch work, going direct to a vendor during their
off-peak window can be cheaper; if you want one invoice and no per-vendor account
to maintain, the flat price is the point.

## A pragmatic starting map

- **Default for most tasks** — Doubao-Seed-2.1-Pro. Cheap enough to leave on,
  fast, and strong enough that most requests never need anything fancier.
- **Coding, math, structured output** — DeepSeek-V4-Pro. The cache economics are
  outstanding and it handles strict JSON and reasoning well.
- **Agents with big tool schemas** — Qwen-3.8-Max. Tool use and long context are
  where Qwen has earned its reputation.
- **Huge-document summarization** — GLM-5.3 or MiniMax-M3. Long context at a
  price that does not punish you for it.
- **Cheapest possible cache** — MiMo-V2.5. If you are re-sending the same prefix
  constantly, this is the floor.
- **Top-shelf quality, money is not the constraint** — Kimi-K3.1-Pro. Premium
  output at a premium price.

This is a starting point, not a verdict. The honest version of "which model" is:
**measure it on your own workload.** A single afternoon of your traffic is worth
more than any leaderboard.

## What it costs, concretely

The gateway ships a cost calculator that answers the question benchmarks ignore:
*what does this request actually bill?* You can also reproduce it yourself —
cached input, fresh input, and output are three different prices, and treating
them as one number overstates the bill. A 2,000-token fresh prompt with 8,000
cached tokens and a 2,000-token reply on DeepSeek-V4-Pro costs about **$0.021**;
the same request without cache hits is roughly **$0.041**, or about twice as much.
That gap is why cache-aware routing is the single highest-leverage optimization
in this catalogue.

The interactive calculator is at **https://adzukiai.com/compare**, and the full
price list is machine-readable at **https://adzukiai.com/pricing.json** — 13
models across these 7 vendors, refreshed from the same source as the site so the
numbers never drift.

## Things worth knowing before you build on any of this

- **Inference runs in mainland China.** Your prompt leaves the US or EU when you
  call these models. Account and billing data stay in the US and EU. If your
  workload cannot cross that boundary, these models are not for you.
- **DeepSeek is restricted for U.S. federal use.** Federal civilian agencies,
  the DoD, the IC, and their contractors may not procure or use DeepSeek
  technology, including through a gateway. This does not apply to ordinary
  commercial use, and does not cover GLM, Kimi, or Doubao.
- **You are buying model access, not a model.** Adzuki AI is a gateway; the model
  names and logos belong to their respective owners.

## Where to go from here

The runnable examples live at **github.com/adzukiai/examples** — curl, the Python
and Node `openai` SDKs, streaming, LiteLLM, and a one-api/new-api wiring guide.
Every snippet talks to the real endpoint; nothing is pseudocode.

---

*Disclosure: I run Adzuki AI. The prices are pulled from the same public list the
gateway serves, so they are reproducible whether or not you take my recommendations.*
