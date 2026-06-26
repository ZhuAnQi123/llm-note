# 阶段 4：Prompt 工程化 & 可观测性 — 总览

日期：阶段 3 完成后（约 Day 12 起）  
阶段：阶段 4  
目标：把 Hero 聊天从「能跑」升级到「可度量、可迭代、可 A/B」的**业务级 Prompt 系统**，并用 Dashboard 展示工程化成果。

---

## 为什么要单独做这一阶段？

阶段 2–3 你已经有了：真实 LLM、流式、RAG、联网搜索。  
但 `main.py` 里的 system prompt 仍是**硬编码字符串**——这在面试里会被追问：

> 「你怎么证明你的 Prompt 更好？怎么回滚？怎么做 A/B？用户说答错了你怎么迭代？」

阶段 4 要回答这些问题，对应岗位能力：

| 岗位要求 | 本阶段落地 |
| -------- | ---------- |
| 设计并迭代业务场景 Prompt 模板 | `prompts/` 分 persona / 场景模板 + Few-shot / CoT |
| A/B 测试持续提升准确率 | `prompt_version` 分流 + 日志对比 |
| 建立提示词评估机制 | 自动化 Eval Runner + 测试用例集 |
| 构建测试用例集 | `eval/test_cases.yaml` 黄金集 |
| CoT / Few-shot / 系统提示 / 版本管理 | Step 01–04 逐一落地 |

---

## 两条主线（交织推进）

```text
Track A — Prompt 工程化（核心）
  模块化 → 版本管理 → 测试集 → Few-shot/CoT → 自动评估 → A/B → 用户反馈

Track B — 可观测性（支撑 A/B 与作品集展示）
  调用日志 → prompt_version 埋点 → Dashboard 指标 → GitHub/RAG 统计
```

**执行顺序有讲究**：没有版本管理就没法 A/B；没有测试集就没法证明迭代有效；没有日志就没法看 A/B 结果。所以按 Step 01→07 顺序走。

---

## Step 规划

| Step | 文件 | Day | 主题 | 关键产出 |
| ---- | ---- | --- | ---- | -------- |
| 01 | [step-01-prompt-versioning.md](./step-01-prompt-versioning.md) | 12 | Prompt 模块化 & 版本管理 | `server/prompts/` + `prompt_registry.py` |
| 02 | [step-02-eval-test-suite.md](./step-02-eval-test-suite.md) | 13 | 测试用例集（黄金集） | `server/eval/test_cases.yaml` |
| 03 | [step-03-fewshot-cot.md](./step-03-fewshot-cot.md) | 14 | Few-shot & CoT 模板迭代 | `sophie_v1.1.yaml` / `naval_v1.1.yaml` |
| 04 | [step-04-eval-runner.md](./step-04-eval-runner.md) | 15 | 自动化评估 Runner | `python -m eval.run` + 通过率报告 |
| 05 | [step-05-ab-testing-logging.md](./step-05-ab-testing-logging.md) | 16 | A/B 分流 + 调用日志 | `chat_logs` + `prompt_version` 字段 |
| 06 | [step-06-user-feedback.md](./step-06-user-feedback.md) | 17 | 用户反馈闭环 | 👍/👎 API + 反馈写入日志 |
| 07 | [step-07-dashboard-observability.md](./step-07-dashboard-observability.md) | 18 | Dashboard 可观测性 | `/api/stats` + Prompt 指标可视化 |

---

## 阶段 4 验收标准（全部勾选才算完成）

**Prompt 工程：**
- [ ] system prompt 不再硬编码在 `main.py`，全部走 `prompt_registry`
- [ ] 至少 2 个 prompt 版本（如 `sophie_v1.0` vs `sophie_v1.1`）可切换
- [ ] `eval/test_cases.yaml` ≥ 20 条（Sophie 12 + Naval 8），含「应拒绝回答」类
- [ ] `python -m eval.run` 输出通过率报告，v1.1 比 v1.0 通过率更高（或说明原因）
- [ ] A/B 实验：50/50 分流，日志可查到每条请求用的 `prompt_version`

**可观测性：**
- [ ] 每次 chat 记录：model、latency、prompt_version、persona、是否有 RAG hit
- [ ] 用户 👍/👎 反馈关联到 message_id
- [ ] Dashboard 展示：调用次数、Prompt 版本分布、Eval 通过率、RAG chunk 数

---

## 目标架构（阶段 4 结束时）

```text
server/
  prompts/
    sophie/
      v1.0.yaml          # 基线版
      v1.1.yaml          # Few-shot + CoT 优化版
    naval/
      v1.0.yaml
      v1.1.yaml
    rag_context.j2       # RAG context 注入模板（Jinja2）
  eval/
    test_cases.yaml      # 黄金测试集
    runner.py            # 自动化评估
    scorers.py           # 评分规则（关键词 / 拒绝检测 / 长度）
  services/
    prompt_registry.py   # 加载 + 版本选择 + A/B 分流
    chat_service.py      # 调用 prompt_registry
    stats_service.py     # 聚合日志指标
  middleware/
    chat_logger.py       # 每次请求写日志
  data/
    chat_logs.jsonl      # 调用日志（或 SQLite）
  main.py                # GET /api/stats, POST /api/feedback

src/
  components/
    HeroSection.tsx      # 👍/👎 反馈按钮
    DashboardSection.tsx # 真实指标
  services/
    statsService.ts
```

---

## 与阶段 3 的衔接

| 阶段 3 产出 | 阶段 4 如何复用 |
| ----------- | --------------- |
| `step-06-evaluation.md` 10 题手测表 | 扩展为 `test_cases.yaml` 20+ 条，自动化 |
| RAG context 拼接逻辑 | 抽成 `rag_context.j2` 模板，独立版本管理 |
| Hybrid RAG + 联网 | Eval 用例增加「应触发联网」「不应编造」类 |

---

## 作品集叙事（面试怎么说）

> 「我的个人网站 Hero 不只是一个 Chat UI。我建立了 **Prompt 版本管理 + 20 条黄金测试集 + 自动化 Eval + A/B 分流 + 用户反馈闭环**。每次改 Prompt 都跑 eval 对比通过率，Dashboard 实时看各版本调用分布和好评率。」

---

## 开始方式

阶段 3 Step 07 完成后 → 打开 **[step-01-prompt-versioning.md](./step-01-prompt-versioning.md)**。
