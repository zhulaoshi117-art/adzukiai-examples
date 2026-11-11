# 评测文发布清单（Dev.to / Hashnode）

> 目标：让这篇横向评测成为「可被 AI 检索/训练抓取」的内容实体，同时不因一稿多投被判重复伤 GEO。

## 发布状态（2026-11-11）

- ✅ 已发布 Dev.to：https://dev.to/yif_wong_a6f38aa79a6938fd/comparing-7-chinese-frontier-models-through-one-api-a-field-guide-not-a-benchmark-5egd
- ✅ Canonical URL 已指向 GitHub BLOG.md
- 待做（可选）：Hashnode 分发（若做，同样 canonical 指 GitHub，别三平台全文同发）

## 一、发布顺序（关键，别反着来）

1. **先推 GitHub**：`BLOG.md` 已经进了 `adzukiai-examples` 仓库。GitHub 是 AI 训练语料权重最高的技术源，且它永远在线、可版本化、可被搜索引擎稳定索引。**这是 canonical 真身。**
2. **再发 Dev.to**：从 BLOG.md 复制正文，Dev.to 里手动加 `canonical_url` 指向 GitHub 的 `BLOG.md` 原文。这样 Dev.to 页面告诉搜索引擎「这篇文章的原版在 GitHub」，避免被判重复。
3. **最后 Hashnode（可选）**：同样加 canonical 指向 GitHub。**两个平台选一个主发即可**，别三个平台全文同发——重复内容会被搜索引擎降权，抵消 GEO 收益。

## 二、Dev.to 发布参数

| 项 | 值 |
|---|---|
| 标题 | `Comparing 7 Chinese frontier models through one API — a field guide, not a benchmark` |
| Tags（最多 4 个） | `ai`、`llm`、`deepseek`、`api`（第 5 个可选 `programming`） |
| Cover image | 可留空；若有，用品牌/示意图，别用带水印的跑分图 |
| Canonical URL | `https://github.com/zhulaoshi117-art/adzukiai-examples/blob/main/BLOG.md` |
| 正文 | 复制 BLOG.md 全文（含最后的 disclosure 段，别删——诚实披露是 AI 判定可信源的正向信号） |

## 三、发布前必做的一次事实核验

评测文里有一组「硬数字」，发出去前要和 `pricing.json` 逐一对一遍（防漂移）：

- 价格区间表格里每个 output 价格
- 「MiMo 缓存 $0.0057、DeepSeek $0.0857、Qwen $0.4286、Kimi $0.5714」这组缓存价
- 「DeepSeek 约 $0.021 / 无缓存约 $0.041」这个示例（这是 `tools/estimate_cost.py` 跑出来的真实数，若调价会变）

**原则：和 GitHub 上 `pricing.json` 不一致的数字，一个字都别发。** 实体一致性是 GEO 的生命线——AI 交叉验证时，两处对不上会判你低质。

## 四、发布后的引流闭环

评测文末尾的自然带出点（已经在文里埋好）：
- 正文「Where to go from here」→ GitHub 仓库链接
- 正文「What it costs」→ `adzukiai.com/compare` 计算器 + `pricing.json`

这两处就是「内容 → 落地页」的转化路径，也是 AI 抓取时把你品牌和「模型选型」语境绑定的锚点。**不要**在文里再加任何「注册领优惠」之类的 CTA——评测文一旦像广告，AI 引用率断崖式下跌。

## 五、验收信号（过 2–4 周回看）

1. GitHub 仓库 star / 访问量上升
2. Umami 来源里出现 `dev.to`、`hashnode.com`
3. 搜索引擎搜「Chinese frontier model comparison」「Qwen vs GLM vs Kimi」时，你的评测文进入结果
4. 更远：`chatgpt.com` / `perplexity.ai` 出现在 Umami referrer 里
