# Learning Notes

这个目录用于记录 Sophie Zhu 在构建个人 AI 前端网站过程中的学习笔记、阶段计划、踩坑记录和导师式指导。

目标不是让 AI 直接替你完成项目，而是作为导师把每一步拆成你能亲手理解和实现的小任务。

---

## 项目目标（来自 `requirement.md`）

| 网站模块 | 核心能力 | 对应阶段 |
| -------- | -------- | -------- |
| **Hero：AI 交互分身** | 多 Persona + 流式 UX + **多 RAG 知识库路由** | 阶段 2 ✅ → 阶段 3 |
| **Projects：Agent 工作流可视化** | React Flow 画布（已完成） | 阶段 1 ✅ |
| **Insights：技术博客** | Streaming UX / LLM 工程复盘文章 | 阶段 5 |
| **Dashboard：学习足迹** | LLM 调用统计、向量库规模、GitHub 热力图 | 阶段 4 |

---

## 进度总览

```text
阶段 1  网站骨架 & 视觉基线          ██████████  已完成
阶段 2  真实大模型（Qwen + Streaming） ██████████  已完成
阶段 3  个人知识库 RAG               ░░░░░░░░░░  ← 当前
阶段 4  Dashboard 数据化              ░░░░░░░░░░
阶段 5  专业化打磨 & 上线             ░░░░░░░░░░
```

勾选清单详见项目根目录 [`.ai/ROADMAP.md`](../.ai/ROADMAP.md)。

---

## 目录结构

```text
learning-notes/
  README.md                          ← 你在这里（总索引）
  stage-2-qwen/                      ← 阶段 2（已完成）
    step-01-backend-api-python.md
    step-02-connect-frontend.md
    step-03-streaming.md
    step-04-project-standards.md
  stage-3-rag/                       ← 阶段 3（当前）
    step-01-data-sources.md
    step-02-chunking.md
    step-03-embedding-vectorstore.md
    step-04-retrieval-in-chat.md
    step-05-citations-ui.md
    step-06-evaluation.md
    step-07-web-search.md
  stage-4-prompt-observability/    ← 阶段 4（规划）
    OVERVIEW.md
    step-01-prompt-versioning.md
    step-02-eval-test-suite.md
    step-03-fewshot-cot.md
    step-04-eval-runner.md
    step-05-ab-testing-logging.md
    step-06-user-feedback.md
    step-07-dashboard-observability.md
  stage-5-polish/                    ← 阶段 5（规划）
    OVERVIEW.md
```

---

## 阶段 2 回顾（已完成）

**验收标准**：聊天框能和真实模型对话、支持流式输出，密钥不暴露到浏览器。

| Step | 主题 | 产出 |
| ---- | ---- | ---- |
| 01 | Python 后端 + Qwen API | `server/main.py`, `schemas.py` |
| 02 | 前后端联调 | `HeroSection.tsx` 真实 fetch |
| 03 | 流式输出 | `StreamingResponse` + `getReader()` |
| 04 | 企业级规范 | Vite Proxy、`chatService.ts`、异常处理 |

**阶段 2 结束时，你的 `server/` 架构：**

```text
server/
  main.py           # 路由入口
  schemas.py        # Pydantic 数据模型
  exceptions.py     # 统一异常处理
  requirements.txt
```

**阶段 2 结束时，你的 `src/` 新增：**

```text
src/
  services/
    chatService.ts  # API 调用与流式解析（UI 不碰底层 fetch）
  components/
    HeroSection.tsx # 只负责 UI + 调用 service
```

---

## 阶段 3：个人知识库 RAG（当前）

**对应 `requirement.md` 的哪一块？**

> Hero 区域的「Virtual Board of Directors」——用简历喂给 Sophie，用《那瓦尔宝典》喂给 Naval，展示**多 Agent 路由 / 多知识库检索**能力。  
> 目前 UI 上已有 `RAG ENABLED` / `NAMESPACE: NAVAL_DB` 标签，但仍是 Prompt 硬编码，阶段 3 要让它**真的检索**。

**验收标准：**

- [ ] Sophie 问「你的技术栈是什么」→ 回答基于你的简历，不编造
- [ ] Naval 问「什么是特殊知识」→ 回答基于 Naval 知识库文档
- [ ] 回答下方展示**引用来源**（文档名 / 段落）
- [ ] 知识库没有的内容 → 明确说「资料中没有提到」，或触发**联网搜索**补充（Step 07）
- [ ] 用 10 个典型问题测试，记录命中率
- [ ] 联网搜索可手动 toggle，且 Web 来源以 `🔗 URL` 形式展示

**推荐技术选型（与现有栈一致）：**

| 层级 | 选型 | 理由 |
| ---- | ---- | ---- |
| Embedding | DashScope `text-embedding-v3` | 与 Qwen 同一供应商，Key 复用 |
| 向量库 | ChromaDB（本地持久化） | 零运维、Python 生态成熟、支持 collection 隔离 |
| 切片 | 按 Markdown 标题 + 固定窗口 | 简单可控，metadata 可挂项目名/日期 |
| 检索 | top-k=3 + cosine similarity | 够用；rerank 留作进阶 |
| 联网搜索 | Tavily API（Step 07） | LLM 友好、返回 snippet、有免费额度 |

**阶段 3 结束时，目标 `server/` 架构：**

```text
server/
  main.py
  schemas.py
  exceptions.py
  services/
    chat_service.py      # 聊天编排（RAG → [Web Search] → 拼 prompt → 调 LLM）
    rag_service.py         # 检索逻辑
    search_service.py      # 联网搜索（Step 07）
  rag/
    chunker.py             # 文档切片
    ingest.py              # 入库脚本（CLI）
  data/
    documents/
      sophie/              # 你的简历、项目说明
      naval/               # 那瓦尔相关资料
    chroma/                # 向量库持久化目录（加入 .gitignore）
```

**Step 执行顺序：**

| Step | 文件 | 预计 | 你要做什么 |
| ---- | ---- | ---- | ---------- |
| 01 | [step-01-data-sources.md](./stage-3-rag/step-01-data-sources.md) | Day 5 | 整理 3 份 Sophie 文档 + 2 份 Naval 文档，规范目录 |
| 02 | [step-02-chunking.md](./stage-3-rag/step-02-chunking.md) | Day 6 | 写 `chunker.py`，按标题切片并挂 metadata |
| 03 | [step-03-embedding-vectorstore.md](./stage-3-rag/step-03-embedding-vectorstore.md) | Day 7 | Embedding 入库 ChromaDB，按 persona 分 collection |
| 04 | [step-04-retrieval-in-chat.md](./stage-3-rag/step-04-retrieval-in-chat.md) | Day 8 | `/api/chat` 接入检索，context 注入 system prompt |
| 05 | [step-05-citations-ui.md](./stage-3-rag/step-05-citations-ui.md) | Day 9 | 前端展示引用来源，RAG 标签变「真」 |
| 06 | [step-06-evaluation.md](./stage-3-rag/step-06-evaluation.md) | Day 10 | 10 题评估表，测命中率与幻觉率 |
| 07 | [step-07-web-search.md](./stage-3-rag/step-07-web-search.md) | Day 11 | Hybrid RAG：本地检索 + Tavily 联网，前端 toggle + Web 引用 |

> **导师建议**：Step 01–06 先跑通纯本地 RAG；Step 07 再加联网，避免同时调试两套链路。联网是 Agent Flow 里 `Tool Executor` 的第一个真实 Tool。

---

## 阶段 4：Prompt 工程化 & 可观测性（规划）

**对应岗位要求 & `requirement.md`：**

> Prompt 模板设计迭代、A/B 测试、评估机制、测试用例集（CoT / Few-shot / 版本管理）  
> Dashboard 数据墙——LLM 调用、Prompt 版本分布、Eval 通过率、RAG 规模、GitHub 热力图

**验收标准：**

- [ ] system prompt 模块化，支持 v1.0 / v1.1 版本切换
- [ ] 黄金测试集 ≥ 20 条，`python -m eval.runner` 输出通过率
- [ ] v1.1（Few-shot + CoT）通过率 ≥ v1.0
- [ ] A/B 50/50 分流，日志记录 `prompt_version`
- [ ] 用户 👍/👎 反馈关联 message_id，可算各版本好评率
- [ ] Dashboard 展示真实指标（非 mock）

**Step 执行顺序（详见 [stage-4-prompt-observability/OVERVIEW.md](./stage-4-prompt-observability/OVERVIEW.md)）：**

| Step | 文件 | Day | 主题 |
| ---- | ---- | --- | ---- |
| 01 | [step-01-prompt-versioning.md](./stage-4-prompt-observability/step-01-prompt-versioning.md) | 12 | Prompt 模块化 & 版本管理 |
| 02 | [step-02-eval-test-suite.md](./stage-4-prompt-observability/step-02-eval-test-suite.md) | 13 | 黄金测试用例集 |
| 03 | [step-03-fewshot-cot.md](./stage-4-prompt-observability/step-03-fewshot-cot.md) | 14 | Few-shot & CoT 模板迭代 |
| 04 | [step-04-eval-runner.md](./stage-4-prompt-observability/step-04-eval-runner.md) | 15 | 自动化 Eval Runner |
| 05 | [step-05-ab-testing-logging.md](./stage-4-prompt-observability/step-05-ab-testing-logging.md) | 16 | A/B 分流 + 调用日志 |
| 06 | [step-06-user-feedback.md](./stage-4-prompt-observability/step-06-user-feedback.md) | 17 | 用户反馈闭环 👍/👎 |
| 07 | [step-07-dashboard-observability.md](./stage-4-prompt-observability/step-07-dashboard-observability.md) | 18 | Dashboard 可观测性 |

> **导师建议**：先跑通 Step 01–04（Prompt + Eval），再加 A/B 和反馈。没有测试集就做 A/B，等于盲人摸象。

---

## 阶段 5：专业化打磨 & 上线（规划）

**对应 `requirement.md`：**

> Insights 技术文章、Streaming UX 复盘、开源 UI 组件、上线后的 SEO 与性能。

**验收标准：**

- [ ] 网站可公开访问（HTTPS + 自定义域名或 Vercel 子域）
- [ ] 首页有完整 meta / OG 标签
- [ ] Insights 区域至少 1 篇技术文章
- [ ] Lighthouse 性能 / 可访问性无明显红灯

**Step 预览（详见 [stage-5-polish/OVERVIEW.md](./stage-5-polish/OVERVIEW.md)）：**

| Step | 主题 |
| ---- | ---- |
| 01 | 前后端部署（Vercel + Railway / Render） |
| 02 | SEO：meta、sitemap、robots.txt |
| 03 | Insights 首篇文章 + 代码高亮 |
| 04 | 性能优化 & 可访问性审查 |
| 05 | 开源 Chat 组件 README + 网站挂「Open Sourced」标签 |

---

## 学习方式

每个 step 文件都建议按这个节奏推进：

1. 先读「今天要理解什么」（【相关知识点】）
2. 再读「你要创建/修改哪些文件」
3. **自己写代码**，不直接复制完整答案
4. 用「验收方式」自测
5. 把卡住的问题记录到当天笔记底部的「今日复盘」

---

## 每日复盘模板

```md
## 今日复盘

- 今天我理解了：
- 今天我亲手实现了：
- 今天我卡住了：
- 明天我要继续：
```

---

## 从哪开始？

阶段 2 已完成 → 打开 **[stage-3-rag/step-01-data-sources.md](./stage-3-rag/step-01-data-sources.md)** 开始 Day 5。
