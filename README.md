# Adzuki AI — API examples

**Adzuki AI is an OpenAI-compatible API gateway that serves DeepSeek, GLM, Kimi and Doubao
models to developers outside mainland China, billed per token in US dollars.** One endpoint,
one API key, one invoice — no Chinese phone number, no real-name verification, card payment.

This repository is the official set of runnable examples and a cost estimator for that API.
Everything here talks to a real endpoint; nothing is pseudocode.

| | |
|---|---|
| Base URL | `https://adzukiai.com/v1` |
| Wire format | OpenAI Chat Completions (`POST /chat/completions`) |
| Authentication | `Authorization: Bearer $ADZUKI_API_KEY` |
| Models & pricing | https://adzukiai.com/models |
| Machine-readable prices | https://adzukiai.com/pricing.json |
| API reference | https://adzukiai.com/docs |
| Per-model detail | https://adzukiai.com/deepseek-v4-pro |

## Quick start

```bash
pip install openai
export ADZUKI_API_KEY="sk-..."        # https://adzukiai.com -> API keys
python examples/python_openai_sdk.py "Explain B-tree splits"
```

The only two lines that differ from any other OpenAI-compatible provider:

```python
client = OpenAI(
    base_url="https://adzukiai.com/v1",
    api_key=os.environ["ADZUKI_API_KEY"],
)
```

## Models and prices

All prices in USD per 1,000,000 tokens. `pricing.json` in this repository is refreshed daily
by a GitHub Action, so the table below and the endpoint cannot disagree.

| Model (API id) | Vendor | Input | Cached input | Output | Context |
|---|---|---|---|---|---|
| `doubao-seed-2.0-lite` | ByteDance Doubao | $0.17 | $0.0343 | $1.03 | &mdash; |
| `glm-5.3-flash` | Zhipu AI | $0.23 | $0.0657 | $0.80 | &mdash; |
| `deepseek-v4.1-flash` | DeepSeek | $0.57 | $0.0114 | $2.29 | &mdash; |
| `doubao-seed-2.1-pro` | ByteDance Doubao | $1.71 | $0.34 | $8.57 | &mdash; |
| `glm-5.3` | Zhipu AI | $2.29 | $0.57 | $8.00 | &mdash; |
| [`deepseek-v4-pro`](https://adzukiai.com/deepseek-v4-pro) | DeepSeek | $2.57 | $0.0857 | $7.71 | 1M |
| `kimi-k3` | Moonshot AI | $5.71 | $0.57 | $28.57 | &mdash; |

7 models from 4 vendors. Output costs several times more than input on
every model, so the cost of a request is dominated by what it generates, not by what you send.

## Examples

| File | Shows |
|---|---|
| [`examples/curl.sh`](examples/curl.sh) | raw HTTP, no SDK — useful when you need to see the wire format |
| [`examples/python_openai_sdk.py`](examples/python_openai_sdk.py) | the official `openai` Python SDK, plus how to read `usage` |
| [`examples/python_stream.py`](examples/python_stream.py) | streaming with `stream_options={"include_usage": True}` |
| [`examples/node_openai_sdk.mjs`](examples/node_openai_sdk.mjs) | the `openai` npm package |

## Cost estimator

```bash
$ python tools/estimate_cost.py deepseek-v4-pro --in 2000 --cached 8000 --out 2000
deepseek-v4-pro  (DeepSeek)

component           tokens   rate / 1M      cost USD
------------------------------------------------------
fresh input          2,000      2.5714      0.005143
cached input         8,000      0.0857      0.000686
output               2,000      7.7143      0.015429
------------------------------------------------------
total               12,000                  0.021257

same request without cache hits: 0.041143 USD  (caching saves 0.019886 USD, 48%)
```

`--in` is fresh (uncached) input and `--cached` is the part the vendor served from its prompt
cache. They are separate flags on purpose: cached input is priced far below fresh input, and a
single "input tokens" number would overstate the bill. Use `--list` for every model, `--json`
for machine-readable output, `--url` to pull the live price list instead of the local copy.

## Things worth knowing before you build on this

- **Requests are processed in mainland China.** Every model here is operated by a provider whose
  inference runs there; your prompt leaves the US or EU when you call it. Account and billing data
  stay in the US and EU. If your workload cannot cross that boundary, do not use this.
- **DeepSeek models are restricted for U.S. federal use.** Federal civilian agencies, the
  Department of Defense, the Intelligence Community and their contractors may not procure or use
  DeepSeek technology, including through a third-party gateway. The restriction does not apply to
  ordinary commercial use, and it does not cover the GLM, Kimi or Doubao models.
- **Pricing is flat around the clock.** There is no peak/off-peak tier and no surcharge at busy
  hours. The upstream vendors do discount their own list prices overnight (22:00–08:00 China
  time); that discount is not passed through here, so schedulable batch work is the one case where
  going direct is cheaper.
- **Billing is a prepaid balance.** No subscription, no monthly minimum. When the balance reaches
  zero, requests stop. A request that fails through the gateway's own error is not charged.
- **Adzuki AI is a gateway, not a model provider.** Model names and logos are trademarks of their
  respective owners.

## Keeping this repository honest

`pricing.json` is generated from the same source as https://adzukiai.com/models and refreshed by
`.github/workflows/refresh-pricing.yml` every day. If a number in this README ever looks stale,
the `pricing.json` file is the one to trust — or fetch https://adzukiai.com/pricing.json directly.

## License

MIT — see [LICENSE](LICENSE).
