# Seedance smart routing — comic-drama shots

Routing comic-drama shots to the right Seedance video tier, instead of paying the
flagship price for every shot. A real end-to-end test: three shots, real charges,
**52.8% cheaper than "always flagship at 1080p"**.

## What's here

| File | What it is |
|---|---|
| [`SEEDANCE-ROUTING.md`](SEEDANCE-ROUTING.md) | The canonical write-up — routing logic, the real test, and the numbers (English) |
| [`Seedance漫剧智能路由方案.pptx`](Seedance漫剧智能路由方案.pptx) | Client-facing proposal deck (Chinese) |
| [`测试案例报告.md`](测试案例报告.md) | Detailed test report with raw charges (Chinese) |
| [`test_case.py`](test_case.py) | End-to-end test harness, stdlib only |
| [`videos/`](videos/) | The three generated shots, one per tier |

## Run the test yourself

```bash
export SEEDANCE_TOKEN=sk-...   # your gateway token
python3 test_case.py single    # one cheap shot to verify the link
python3 test_case.py full      # all three shots
```

The harness uses only the Python standard library — no third-party dependencies.
See the write-up for the two footguns worth knowing first (`resolution` belongs
in `metadata`; copyright/sensitivity filters on costumed prompts).
