#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seedance 智能路由 —— 真实测试案例（标准库版，无第三方依赖）
===============================================================
通过中文站网关（console.jinxiaodouai.cn，客户真实入口）端到端生成视频。

用法：
  python3 test_case.py single    # 只跑一条 mini 480p 验证链路
  python3 test_case.py full      # 跑完整 3 镜头对比
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error

GATEWAY = os.environ.get("SEEDANCE_GATEWAY", "https://console.jinxiaodouai.cn")
TOKEN = os.environ.get("SEEDANCE_TOKEN", "")

M_MINI = "doubao-seedance-2-0-mini-260615"
M_FAST = "doubao-seedance-2-0-fast-260128"
M_PRO = "doubao-seedance-2-0-260128"
M_25 = "doubao-seedance-2-5-260628"


def call(path, method="GET", body=None, timeout=30):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(GATEWAY + path, data=data, method=method)
    r.add_header("Authorization", "Bearer " + TOKEN)
    r.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    if data:
        r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return -1, repr(e)


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def create_video(model, prompt, resolution, duration=5, ratio="16:9"):
    """⚠ resolution 放 metadata（放顶层被忽略，默认 720p 多花钱）。"""
    body = {
        "model": model,
        "prompt": prompt,
        "duration": duration,
        "ratio": ratio,
        "metadata": {"resolution": resolution},
        "generate_audio": False,
    }
    return call("/v1/videos", "POST", body)


def get_video_url(task_id):
    """走 /content 端点，302 重定向到 OSS 签名 URL（中文站已配视频转存）。"""
    code, raw = call(f"/v1/videos/{task_id}/content")
    # call() 会跟随重定向，返回最终内容；这里需要拿 location 头，用底层请求
    r = urllib.request.Request(GATEWAY + f"/v1/videos/{task_id}/content")
    r.add_header("Authorization", "Bearer " + TOKEN)
    r.add_header("User-Agent", "Mozilla/5.0")
    try:
        import urllib3  # noqa
    except Exception:
        pass
    # 用 opener 不跟随重定向拿 location
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None
    opener = urllib.request.build_opener(NoRedirect)
    try:
        resp = opener.open(r, timeout=20)
        return resp.headers.get("Location")
    except urllib.error.HTTPError as e:
        return e.headers.get("Location")
    except Exception as e:
        return None


def poll_video(task_id, timeout=300):
    t0 = time.time()
    while time.time() - t0 < timeout:
        code, raw = call(f"/v1/videos/{task_id}")
        if code != 200:
            return f"http_{code}", {"raw": raw[:300]}
        try:
            d = json.loads(raw)
        except Exception:
            d = {"raw": raw[:300]}
        # 兼容两种返回结构
        st = d.get("status") or (d.get("data") or {}).get("status") or "unknown"
        if st in ("succeeded", "completed", "failed", "expired", "cancelled"):
            return st, d
        time.sleep(8)
    return "timeout", {"elapsed": timeout}


def run_one(model, prompt, resolution, tag):
    log(f"=== {tag} === model={model} res={resolution}")
    t0 = time.time()
    code, raw = create_video(model, prompt, resolution)
    log(f"  创建 HTTP {code}: {raw[:200]}")
    if code != 200:
        return {"tag": tag, "ok": False, "create_http": code, "err": raw[:300]}

    try:
        d = json.loads(raw)
        task_id = d.get("id") or (d.get("data") or {}).get("id")
    except Exception:
        task_id = raw[:100]
    log(f"  task_id={task_id}")

    status, data = poll_video(task_id)
    elapsed = round(time.time() - t0, 1)
    log(f"  终态 status={status} 耗时={elapsed}s")

    url = get_video_url(task_id) if status in ("succeeded", "completed") else None
    if url:
        log(f"  视频URL: {url[:100]}...")
    return {
        "tag": tag, "ok": status in ("succeeded", "completed"),
        "model": model, "resolution": resolution,
        "task_id": task_id, "status": status,
        "elapsed": elapsed, "video_url": url,
    }


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "single"
    results = []

    shots = [
        (M_MINI, "一个古装女子站在竹林中，微风吹动她的发丝和衣角，镜头缓慢向前推进，电影感柔光，人物轻微呼吸", "480p", "镜头1_静态微动"),
        (M_FAST, "两个古装人物面对面交谈，一人抬手做手势，镜头中景轻微运镜，光线柔和", "720p", "镜头2_常规对话"),
        (M_PRO, "两名剑客在雨中激斗，剑光交错，身形快速移动，水花飞溅，慢动作特写，动态运镜", "1080p", "镜头3_复杂动作"),
    ]

    if mode == "single":
        shots = shots[:1]

    for model, prompt, res, tag in shots:
        results.append(run_one(model, prompt, res, tag))
        time.sleep(2)

    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for r in results:
        print(f"  {r['tag']}: ok={r['ok']} model={r.get('model')} res={r.get('resolution')} "
              f"耗时={r.get('elapsed')}s status={r.get('status')}")
        if r.get("video_url"):
            print(f"    视频URL: {r['video_url'][:120]}...")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_results.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存: {out}")


if __name__ == "__main__":
    main()
