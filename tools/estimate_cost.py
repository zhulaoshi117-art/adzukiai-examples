#!/usr/bin/env python3
"""Estimate what a request costs, from the published price list.

    python tools/estimate_cost.py --list
    python tools/estimate_cost.py deepseek-v4-pro --in 2000 --cached 8000 --out 2000
    python tools/estimate_cost.py deepseek-v4-pro --in 2000 --out 2000 --json
    python tools/estimate_cost.py --url https://adzukiai.com/pricing.json --list

`--in` is fresh (uncached) input tokens and `--cached` is the part of the prompt
the vendor served from its prompt cache. They are priced differently, so they are
separate flags: cached input is usually 10-60x cheaper than fresh input, and
passing one number for "input" would silently overstate the bill.

The numbers come from pricing.json, which is generated from the same source as
https://adzukiai.com/models. Nothing here is hard-coded, so the estimate cannot
drift away from the published prices.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL = os.path.normpath(os.path.join(HERE, "..", "pricing.json"))


def load(url: str | None) -> dict:
    if url:
        with urllib.request.urlopen(url, timeout=20) as r:
            return json.load(r)
    if not os.path.exists(LOCAL):
        sys.exit(f"pricing.json not found at {LOCAL}; run with --url https://adzukiai.com/pricing.json")
    with open(LOCAL, encoding="utf-8") as f:
        return json.load(f)


def find(data: dict, model: str) -> dict:
    for m in data["models"]:
        if m["id"].lower() == model.lower():
            return m
    ids = [m["id"] for m in data["models"]]
    sys.exit("unknown model %r.\nknown ids: %s" % (model, ", ".join(ids)))


def cmd_list(data: dict) -> None:
    unit = data.get("unit", "per 1,000,000 tokens")
    print(f"{data['service']} — USD {unit}  (updated {data.get('updated', '?')})\n")
    print(f"{'model':<24}{'vendor':<18}{'input':>8}{'cached':>9}{'output':>9}{'ctx':>10}")
    print("-" * 78)
    for m in data["models"]:
        ctx = m.get("context_tokens")
        ctx_s = f"{ctx:,}" if ctx else "-"
        print(f"{m['id']:<24}{m['vendor']:<18}{m['input_per_1m']:>8.4f}"
              f"{m['cached_input_per_1m']:>9.4f}{m['output_per_1m']:>9.4f}{ctx_s:>10}")
    print()
    print(f"pricing page: {data['url']}/models")
    print(f"json:         {data['url']}/pricing.json")


def cmd_estimate(data: dict, m: dict, fresh: int, cached: int, out: int, as_json: bool) -> None:
    pin, pcache, pout = m["input_per_1m"], m["cached_input_per_1m"], m["output_per_1m"]
    c_fresh = fresh * pin / 1e6
    c_cached = cached * pcache / 1e6
    c_out = out * pout / 1e6
    total = c_fresh + c_cached + c_out
    no_cache = (fresh + cached) * pin / 1e6 + c_out

    if as_json:
        print(json.dumps({
            "model": m["id"],
            "tokens": {"fresh_input": fresh, "cached_input": cached, "output": out},
            "rates_per_1m": {"input": pin, "cached_input": pcache, "output": pout},
            "cost_usd": {
                "fresh_input": round(c_fresh, 8),
                "cached_input": round(c_cached, 8),
                "output": round(c_out, 8),
                "total": round(total, 8),
            },
            "cost_usd_without_cache": round(no_cache, 8),
        }, indent=2))
        return

    print(f"{m['id']}  ({m['vendor']})\n")
    print(f"{'component':<16}{'tokens':>12}{'rate / 1M':>12}{'cost USD':>14}")
    print("-" * 54)
    print(f"{'fresh input':<16}{fresh:>12,}{pin:>12.4f}{c_fresh:>14.6f}")
    print(f"{'cached input':<16}{cached:>12,}{pcache:>12.4f}{c_cached:>14.6f}")
    print(f"{'output':<16}{out:>12,}{pout:>12.4f}{c_out:>14.6f}")
    print("-" * 54)
    print(f"{'total':<16}{fresh + cached + out:>12,}{'':>12}{total:>14.6f}")
    if cached:
        saved = no_cache - total
        print(f"\nsame request without cache hits: {no_cache:.6f} USD"
              f"  (caching saves {saved:.6f} USD, {saved / no_cache * 100:.0f}%)")
    print(f"\nprices: {data['url']}/models   (updated {data.get('updated', '?')})")


def main() -> int:
    p = argparse.ArgumentParser(description="Estimate request cost from adzukiai.com prices.")
    p.add_argument("model", nargs="?", help="model id, e.g. deepseek-v4-pro")
    p.add_argument("--list", action="store_true", help="print all models and prices")
    p.add_argument("--in", dest="fresh", type=int, default=0, metavar="TOKENS",
                   help="fresh (uncached) input tokens")
    p.add_argument("--cached", type=int, default=0, metavar="TOKENS",
                   help="input tokens served from the prompt cache")
    p.add_argument("--out", dest="out", type=int, default=0, metavar="TOKENS",
                   help="output tokens")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    p.add_argument("--url", help="fetch a live price list instead of the local pricing.json")
    a = p.parse_args()

    data = load(a.url)
    if a.list or not a.model:
        cmd_list(data)
        return 0

    if a.fresh == 0 and a.cached == 0 and a.out == 0:
        p.error("give at least one of --in / --cached / --out")

    cmd_estimate(data, find(data, a.model), a.fresh, a.cached, a.out, a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
