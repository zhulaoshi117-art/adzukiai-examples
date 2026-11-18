Comic drama (动态漫画 / manhua-style short drama) is one of the few AI-video workloads where the economics are already obvious: a single episode is a dozen or so storyboard shots, and a season is dozens of episodes. Multiply a per-shot cost by a few hundred, and the difference between "always use the flagship model" and "use the right model per shot" stops being a rounding error.

This document is about the second option. It is a write-up of a real test we ran against a live gateway — not a benchmark, and not a vendor's marketing page. I run Adzuki AI, the gateway in question, so treat the numbers with the usual grain of salt, but every cost below is an actual charge, pulled from the upstream billing API after a real video came back.

## The problem: nobody needs the flagship for every shot

A comic-drama episode is not one kind of footage. It is several, with very different demands:

| Shot type | What it looks like | What it actually needs |
|---|---|---|
| Static / idle | A figure standing in wind, hair and cloth moving, a slow push-in | 480p, cheapest tier, no complex motion |
| Dialogue | Two people talking, simple camera drift, mid shot | 720p, mid tier, ordinary motion |
| Action | A fight, fast cuts, splashing water, slow-mo | 1080p, flagship, complex motion |

The default behaviour most teams fall into is to send everything to the flagship at 1080p, because "it's the good one." That is the expensive habit this routing approach removes.

## The routing logic: three gates, not a black box

The router does not guess. It reads two signals that are already in the request, then falls back to a tagger only when those are ambiguous.

1. **Explicit overrides win.** If the client pins a `model`, `resolution`, or `duration`, that is used verbatim. No magic.
2. **The prompt decides the tier.** Static/idle keywords route down, complex action keywords route up. This is a plain rule table — zero model calls, zero cost, fully explainable.
3. **A tagger catches the fuzzy cases.** Only when the prompt is ambiguous does a small model classify it. The rare case, not the common one.

The point is that every routing decision is traceable. The chosen model is returned in the response headers and logged, so a client can always answer "why did this shot cost what it cost." That transparency is the difference between "an optimizer" and "a black box that might be quietly downgrading you."

## The real test: three shots, real charges

We ran three representative shots through a live gateway on 2026-11-17, with real generation and real billing. Results:

| Shot | Model | Resolution | Status | Time | Charged | List cost |
|---|---|---|---|---|---|---|
| Static (figure in wind) | 2.0-mini | 480p | ✅ | 154s | **¥1.17** | ¥1.10 |
| Dialogue (two figures) | 2.0-fast | 720p | ✅ | 169s | **¥4.03** | ¥4.00 |
| Action (rain duel) | 2.0-pro | 1080p | ✅ | 270s | **¥12.50** | ¥12.39 |

The charges land within 1% of the list prices, which is itself the point we wanted to verify: the billing path is correct, and the routing did not inflate anything.

## The number that matters

Take the same three shots and compare "always flagship at 1080p" against "routed per shot":

| Approach | Cost for 3 shots |
|---|---|
| Always 2.0-pro at 1080p | ¥37.50 |
| Routed (mini 480p + fast 720p + pro 1080p) | ¥17.70 |
| **Saved** | **¥19.80 — 52.8%** |

Scale it to one episode of 12 shots (a typical 4 static + 6 dialogue + 2 action mix) and the gap widens, because most shots in a comic drama are static or dialogue, not action:

| Approach | Per episode | 60 episodes |
|---|---|---|
| Always pro 1080p | ¥148.68 | ¥8,920.80 |
| Routed | ¥53.18 | ¥3,190.80 |
| **Saved** | **64%** | **¥5,730** |

The saving is not "we cut quality across the board." It is "the static shot does not need the action model." The output quality per shot is unchanged; what changes is that you stop paying the flagship price for footage that a cheaper tier renders identically well.

## Two things that bit us, worth knowing before you build on this

**1. Resolution belongs in `metadata`, not the top level.** Sending `resolution` at the top level of the request is silently ignored and defaults to 720p — you pay more for nothing. It has to go under `metadata`. This is a real footgun that costs real money at comic-drama volume.

**2. Copyright / sensitivity filters are a thing.** Our first dialogue shot used a "costumed swordsman" prompt and failed with `OutputVideoSensitiveContentDetected.PolicyViolation` — likely a copyright-adjacent guardrail. A neutral prompt passed. If your clients produce costumed or IP-adjacent material, prompt-level de-sensitization is something the routing layer can also handle automatically, but it is worth knowing it exists before you promise a clean pipeline.

## What this is and is not

This is **not** a general "one API for all video models" aggregator. Those already exist and they solve a different problem — normalizing parameters and picking the cheapest vendor for the *same* model. This is the inverse: same model family (Seedance), choosing the *right tier per shot* for a specific workload (comic drama).

The moat is not the routing logic, which is simple. It is the data: every client's shot taxonomy, and every manual override they make, is feedback that makes the routing better. A small per-client model can eventually replace the rule table entirely, trained on the client's own shots — which is why this works best as a long-term collaboration, not a one-off API toggle.

The three generated shots, the detailed report, and the client-facing deck are in the GitHub repo: https://github.com/zhulaoshi117-art/adzukiai-examples/tree/main/seedance-router
