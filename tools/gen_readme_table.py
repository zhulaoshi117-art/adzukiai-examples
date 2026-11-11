#!/usr/bin/env python3
"""Regenerate the model/vendor parts of README.md from pricing.json.

Why this exists: the README's "Models and prices" table and the "7 models from
4 vendors" summary were once typed by hand. The moment the catalogue changes,
the hand-typed numbers drift from pricing.json (and therefore from the live
site), which is exactly the entity-consistency failure GEO punishes. This
script rebuilds those blocks from pricing.json so they can never disagree.

Run:  python3 tools/gen_readme_table.py
The blocks are delimited by HTML comments (<!-- MODELS:START/END --> etc.), so
everything outside them is left untouched.
"""

import json
import re
import sys
from collections import OrderedDict


def usd(v):
    """Format a USD price the way the site's money() does: trim trailing zeros
    but keep at least two decimals."""
    s = "%.4f" % v
    s = s.rstrip("0")
    if s.endswith("."):
        s += "00"
    elif len(s.split(".")[1]) < 2:
        s = s.split(".")[0] + "." + s.split(".")[1].ljust(2, "0")
    return s


def load():
    with open("pricing.json", "r", encoding="utf-8") as f:
        return json.load(f)


def replace_block(text, marker, new_body):
    """Replace the content between <!-- marker:START --> and <!-- marker:END -->."""
    start = "<!-- %s:START -->" % marker
    end = "<!-- %s:END -->" % marker
    pat = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    if not pat.search(text):
        raise SystemExit("marker %s not found in README" % marker)
    return pat.sub(start + "\n" + new_body + end, text, count=1)


def main():
    d = load()
    models = d["models"]

    # vendor order: first-seen in the catalogue (stable), not alphabetical.
    vendors = OrderedDict()
    for m in models:
        vendors.setdefault(m["vendor"], 0)
        vendors[m["vendor"]] += 1

    n_models = len(models)
    n_vendors = len(vendors)

    # --- summary line: "13 models from 7 vendors" ---
    summary = "%d models from %d vendors." % (n_models, n_vendors)

    # --- vendor list for the opening paragraph ---
    # "DeepSeek, GLM, Kimi, Doubao, Qwen, MiniMax and Xiaomi MiMo"
    names = list(vendors.keys())
    if len(names) == 1:
        vendor_phrase = names[0]
    elif len(names) == 2:
        vendor_phrase = " and ".join(names)
    else:
        vendor_phrase = ", ".join(names[:-1]) + " and " + names[-1]

    # --- the table (header stays in README outside the marker) ---
    rows = []
    for m in models:
        mid = m["id"]
        vendor = m["vendor"]
        pin = usd(m["input_per_1m"])
        pcache = usd(m["cached_input_per_1m"])
        pout = usd(m["output_per_1m"])
        ctx = m.get("context_tokens")
        if ctx:
            if ctx % 1000000 == 0:
                ctx_cell = "{:,}M".format(ctx // 1000000)
            else:
                ctx_cell = "{:,}K".format(ctx // 1000)
        else:
            ctx_cell = "&mdash;"
        page = m.get("pricing_page", "")
        # link the model id to its per-model page when one exists, else to /models
        if page and page.rstrip("/").rsplit("/", 1)[-1] == mid:
            cell = "[`%s`](%s)" % (mid, page)
        else:
            cell = "`%s`" % mid
        rows.append("| %s | %s | $%s | $%s | $%s | %s |"
                    % (cell, vendor, pin, pcache, pout, ctx_cell))
    table = "\n".join(rows)

    # --- the trailing sentence about output vs input ---
    # keep it factual: output is several times input on every model.
    tail = ("Output costs several times more than input on every model, so the cost of "
            "a request is dominated by what it generates, not by what you send.")

    text = open("README.md", "r", encoding="utf-8").read()

    text = replace_block(text, "VENDOR_LIST", vendor_phrase)
    text = replace_block(text, "MODEL_COUNT", summary)
    text = replace_block(text, "MODEL_TABLE", table)
    text = replace_block(text, "MODEL_TABLE_TAIL", tail)

    open("README.md", "w", encoding="utf-8", newline="\n").write(text)
    print("README regenerated: %d models, %d vendors" % (n_models, n_vendors))


if __name__ == "__main__":
    main()
