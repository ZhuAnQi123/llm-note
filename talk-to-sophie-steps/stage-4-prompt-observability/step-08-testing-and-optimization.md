# Talk to Sophie Agent 概览与测试优化方案

## 1) 当前 Agent 概览（现有代码与知识库逻辑）

### 1.1 主链路逻辑（请求到回答）

- 入口：`/api/chat` -> `build_and_stream_chat()`。
- 查询改写：先用 `rewrite_search_query()` 把用户问题改写成检索 query（会处理“你/今年”等代词）。
- 意图路由 + RAG 检索：`resolve_retrieval_params()` 推断 `top_k` 与 metadata 过滤，再调用 `retrieve()` 从 Chroma 的 `{persona}_kb` 取片段。
- 上下文组装：按 `(source, title)` 去重合并 chunk，截断后拼成 XML 结构化 context。
- 系统提示词组装：`build_system_message()` 把 persona prompt + CoT + few_shot + `rag_context.j2` 渲染结果拼成 system prompt。
- 大模型输出：通过 LangChain `RunnableWithMessageHistory` 流式返回，保留最近 5 轮对话记忆。

### 1.2 数据来源与入库

- 数据目录：`server/data/documents/{persona}`，sophie 的数据源在 `server/data/documents/sophie`（被 `.gitignore` 忽略）。
- 切片策略：按 Markdown `##` 语义分段，超长段再做固定窗口切片。
- 元数据：支持从文档中 `> metadata: ...` 提取字段（如 `type=self project`）。
- 向量库：`data/chroma_data`，collection 为 `sophie_kb` / `naval_kb`。

### 1.3 知识库 metadata 类型一览（sophie）

| type              | 示例文档                            | 用途               |
| ----------------- | ----------------------------------- | ------------------ |
| `profile`         | `01-profile.md`                     | 基本信息、定位     |
| `skill`           | `02-skills.md`                      | 技术技能           |
| `experience`      | `03-experience.md`                  | 工作/学习经历      |
| `company project` | `projects/fx-marketing-agent.md` 等 | 公司项目           |
| `project`         | `projects/welab-bank-website.md`    | 公司项目（旧写法） |
| `self project`    | `projects/talk-to-sophie.md` 等     | 个人项目           |

---

## 2) 2026-07 实测问题（`测试文件.md`）与根因

### 测试 1：「你在上一架公司呆了.a几年」

**现象**：

- 大量语气词（「啊」「让我想想」）
- 没有正面回答，绕来绕去
- 编造「去年年底离开」「两年多」——与知识库 `2021.11 - 2026.07（共4年08个月）` 完全不符
- 末尾引导提问（「你是不是也在考虑换工作？」）

**根因**：

1. **P0 Bug**：`grouped_results` 循环未写入文本，RAG context 始终为空，模型在无资料情况下自由发挥。
2. 前端展示的「知识库来源」来自 `retrieved_results`，**不等于**模型实际读到了这些内容。
3. prompt version 默认不一致（`load_prompt` 默认 1.1，`build_system_message` 曾默认 1.0）。
4. `few_shot` 在 YAML 中定义了两次，「诚实拒答」示例被覆盖。
5. CoT 曾要求「引导性结尾」，与 system 规则矛盾。

### 测试 2：「你的上一家公司是什么」

**现象**：

- 回答「科技公司」「产品管理」——知识库明确是「汇立银行 Welab Bank · 前端开发工程师（AI应用方向）」
- 编造「规模不大但氛围好」「自由职业」

**根因**：同上，核心是无 RAG 正文 + 幻觉。

### 测试 3：「简单说说你的工作经历，不要绕弯子」

**现象**：稍好但仍错——说「三段经历含自由职业者」，知识库只有 **2 段公司经历**。

**根因**：即使明确要求简洁，没有资料注入时模型仍会编造。

### 问题汇总（用户观察的 4 点）

### 测试 4：「你在上家公司呆了几年？做什么岗位」

**现象**：回答了「在汇立银行（Welab Bank）担任前端开发相关职位...」，但**遗漏了关于“呆了几年”的回答**。单独询问时能正确回答，组合询问时产生遗漏。

**根因**：

1. **多意图注意力丢失**：大模型在处理复合问题时，注意力发生了偏移，仅聚焦到了“上家公司”和“岗位”上。
2. **Prompt 缺乏引导**：系统提示词缺少「拆解复合问题、逐一回答」的强指令约束。
3. **Query改写可能丢失细节**：`rewrite_search_query` 环节可能在浓缩意图时把多意图弱化为了单一意图。

### 问题汇总（用户观察的 5 点）

| # | 问题 | 直接原因 |
| --- | --- | --- |
| 1 | 语气词多、不专业 | 无 KB 约束 + v1.0 可能在跑 + few_shot 示范不足 |
| 2 | 不正面回答问题 | KB 未注入，模型不知道 Welab Bank 起止时间 |
| 3 | 编造经历/岗位/离职时间 | **纯幻觉**，检索到了但没喂给模型 |
| 4 | 乱引导用户继续提问 | CoT「引导性结尾」+ few_shot 末尾「我很乐意分享」 |
| 5 | 复合问题遗漏 | 模型未对多意图提问做拆解，回答顾此失彼 |

---

## 3) 代码层面发现的隐性风险（建议优先修）

### 已修复 ✅

1. **`grouped_results` 循环缺失 append** — 已补全写入 + 文本去重。
2. **prompt version 默认不一致** — `build_system_message()` 默认改为 `1.1`，与 `load_prompt()` 对齐。
3. **`few_shot` 重复定义** — 已合并为一个列表，含：技能、诚实拒答、待了几年、公司项目。
4. **`rag_context.j2` 为空** — 已补全模板，注入使用说明 + `{{ rag_context }}`。
5. **`v1.1.yaml` 中 `{{ rag_context }}` 占位符** — 已从 system 移除（由 `build_system_message` 统一注入）。
6. **CoT「引导性结尾」** — 已删除。
7. **metadata 意图路由** — 已在 `chat_service.py` 实现 `resolve_retrieval_params()`。

### 仍待关注 ⚠️

1. `.gitignore` 忽略 `server/data/documents/sophie`，团队协作下容易出现「本地有文档、他人环境无文档、效果不一致」。
2. 「上一家公司」语义歧义：可能指 Welab Bank（当前/最近）或光速智能（前一家），模型应优先引用资料中的时间段，必要时澄清。
3. 列举类问题仍依赖 TopK 召回，极端情况下可能漏项（P1 聚合回答器可进一步改善）。

---

## 4) 优化方案（按优先级）

### P0（今天就能做，最小改动高收益）

- [x] **P0-1** 提升「列举类问题」的召回覆盖
  - 命中 `所有/全部/几段/哪些/分别/列举` 时 `top_k=12`，否则 `top_k=8`。

- [x] **P0-2** 加入 metadata 过滤路由
  - 个人项目 → `{"type": "self project"}`
  - 公司项目 → `{"type": {"$in": ["company project", "project"]}}`
  - 工作经历/待了几年 → `{"type": "experience"}`
  - 技能 → `{"type": "skill"}`
  - 过滤无结果时自动降级为无过滤检索。

- [x] **P0-3** 修复 prompt/version 生效链路
  - `DEFAULT_PROMPT_VERSION` 默认 `1.1`。

- [x] **P0-4** 修复已知实现 bug
  - `grouped_results` append + 去重
  - 合并 `few_shot` 为一个节点
  - 补全 `rag_context.j2`

---

### P1（1-3 天，稳定性显著提升）

- [ ] **P1-1** 数据分层：统一 metadata 命名
  - 建议将 `welab-bank-website.md` 的 `type=project` 改为 `type=company project`。
  - 每篇文档统一：`type`, `company`, `time_start`, `time_end`。

- [ ] **P1-2** 加「聚合回答器」（Retriever 后处理）
  - 列举类问题：拉 top_k=20 → 按 source/title 去重 → 截断后交给模型。
  - 当前已有按 source/title 去重，可进一步增大列举类 top_k。

- [-] **P1-3** 时间计算规则化
  - 知识库已写「共4年08个月」，优先让模型直接引用原文。
  - 后续可加 functional-calling 做程序侧年限计算。

- [ ] **P1-4** 多意图问题处理（防遗漏）
  - 优化系统提示词（System Prompt），要求「若包含多个问题，需逐一解答」。
  - 在 few_shot 中增加多意图问答的示范。

---

### P2（中期优化）

- [ ] **P2-1** 构建可执行评测闭环（`server/eval/test_cases.yaml` + runner）
- [ ] **P2-2** 混合检索 / reranker

---

## 5) 针对测试问题的「目标回答标准」

1. **`你在上一家公司待了几年`**
   - 应返回：「在汇立银行（Welab Bank）约 4 年 8 个月（2021.11 - 2026.07）。」
   - 若用户意指「光速智能」，应返回约 1 年 4 个月（2020.06 - 2021.10）。

2. **`你的上一家公司是什么`**
   - 应返回：「汇立银行（Welab Bank），岗位是前端开发工程师（AI 应用方向）。」

3. **`你有过几段工作经历`**
   - 应返回 2 段：汇立银行、光速智能，附时间段。

4. **`你做过什么个人项目（所有）`**
   - 应覆盖：`Talk to Sophie`、`念头驯养员`、`Vibe UI` 等（metadata `type=self project`）。

5. **`你在上家公司呆了几年？做什么岗位`**
   - 应返回：「在上一家公司汇立银行（Welab Bank），我担任前端开发工程师（AI应用方向）。我在那里呆了大约 4 年 8 个月（2021.11 - 2026.07）。」

---

## 6) 关键实现说明（给维护者）

### 6.1 `rag_context.j2` 怎么写

Jinja2 模板只负责「包一层说明文字」，真正的文档内容由 Python 拼好后传入 `rag_context` 变量：

```jinja2
## 参考资料
...使用规则说明...
{{ rag_context }}
```

渲染入口在 `prompt_registry.py` → `build_system_message()`：

```python
template = env.get_template("rag_context.j2")
rag_addition = template.render(rag_context=rag_context)
parts.append(rag_addition)
```

`rag_context` 的内容由 `chat_service.py` 生成，格式为多个 `<document>` XML 块。

### 6.3 metadata 过滤怎么做

1. 入库时：`chunker.py` 从 `> metadata: type=experience` 解析进 Chroma metadata。
2. 检索前：`resolve_retrieval_params()` 用正则匹配用户意图 → 返回 `(top_k, filters)`。
3. 检索时：`retrieve(..., filters={"type": "experience"})` 传给 Chroma `where` 参数。
4. 降级：过滤后 0 条结果 → 去掉 filter 重检。

扩展新类型时：在知识库文档加 metadata，再在 `resolve_retrieval_params()` 加一条正则分支即可。

---

## 7) 建议落地顺序

1. ✅ 修 bug（grouped_results / version / few_shot / rag_context.j2）
2. ✅ 加意图路由 + metadata 过滤 + 列举类 top_k 提升
3. ⬜ 统一文档 metadata 命名（`project` → `company project`）
4. ⬜ 补 eval runner，改一次测一次可回归

按此顺序，测试文件中的语气词、编造、不正面回答问题应明显改善。修完后请用 `测试文件.md` 中 3 个 case 重新验证。
