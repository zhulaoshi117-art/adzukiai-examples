# Adzuki AI in one-api / new-api

[one-api](https://github.com/songquanpeng/one-api) and its fork
[new-api](https://github.com/QuantumNous/new-api) let you run your own
multi-vendor gateway and meter every key yourself. Adzuki AI plugs in as one
upstream "channel" so your gateway can route to Chinese frontier models through
a single OpenAI-compatible endpoint.

## Add a channel

In the admin panel: **Channels → Add channel**, then:

| Field | Value |
|---|---|
| Type | `OpenAI` |
| Name | anything, e.g. `adzuki` |
| Base URL | `https://adzukiai.com/v1` |
| Model | see the list below |
| Key | your Adzuki API key (`sk-...`) |

Leave everything else at its default. The endpoint speaks the OpenAI wire
format, so no rewrite of the request or response is needed.

## Models to list

Paste the model ids you want to expose (the full catalogue is at
`https://adzukiai.com/models`). The live list is also machine-readable at
`https://adzukiai.com/pricing.json`.

```
deepseek-v4.1-flash
deepseek-v4-pro
glm-5.3-flash
glm-5.3
doubao-seed-2.0-lite
doubao-seed-2.1-lite
doubao-seed-2.1-pro
mimo-v2.5
mimo-v2.5-pro
minimax-m3
qwen3.8-max
kimi-k3.1-pro
kimi-k3
```

## Verify it works

After you save the channel, hit your own gateway's endpoint with one of those
model ids. The response should be identical to calling `adzukiai.com/v1`
directly — one-api/new-api only forwards and meters.
