# Step 04：检索链路接入 Chat API (Day 8)

日期：2026-06-12  
阶段：阶段 3 - 个人知识库 RAG  
目标：在 `/api/chat` 中，先检索相关 chunks，再把 context 注入 prompt，让 LLM 基于你的资料回答。

---

## 1. 今天的学习目标

【相关知识点】

- **RAG 完整链路**：`用户问题 → Embedding → 向量检索 top-k → 拼入 Prompt → LLM 生成`
- **Context Injection（上下文注入）**：检索到的 chunks 放进 system prompt 或单独的 context 消息里，并明确告诉模型「只基于以下资料回答，资料中没有的就说不知道」。
- **Prompt 结构（推荐）**：

```text
[System]
你是 Sophie 的 AI 分身。以下是从知识库检索到的相关资料：
---
[1] 来源: resume.md > 工作经历
{chunk text}
---
[2] 来源: projects.md > Light-Agent Flow
{chunk text}
---
请严格基于以上资料回答。如果资料中没有相关信息，请明确说「我的资料中没有提到这一点」。

[User]
{用户问题}
```

---

## 2. 对应 requirement.md

> 证明你理解 **Prompt Engineering**（性格塑造）+ **多 RAG 知识库 (Vector DB Namespaces)** 的动态调度。

今天 backend 根据 `request.persona` 路由到不同 collection，前端暂时不变。

---

## 3. 今天的实操任务

### 任务 1：抽取 `server/services/chat_service.py`

把 `main.py` 里的 prompt 组装 + LLM 调用逻辑抽到 service 层（项目级规范）：

```text
main.py          → 只注册路由，调用 chat_service
chat_service.py  → build_messages() + stream_completion()
rag_service.py   → retrieve()
```

### 任务 2：在 `build_messages` 中接入 RAG

伪代码流程：

```python
def build_messages(user_message: str, persona: str) -> tuple[list[dict], list[dict]]:
    # 1. 检索
    chunks = rag_service.retrieve(user_message, persona, top_k=3)

    # 2. 拼 context 字符串
    context = format_chunks_as_context(chunks)

    # 3. 组装 system prompt（persona 人格 + RAG context + 安全边界）
    system_prompt = f"{PERSONA_PROMPTS[persona]}\n\n{context}\n\n请严格基于以上资料回答……"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    # 4. 返回 messages 和 sources（供后续前端展示）
    sources = [{"source": c["metadata"]["source"], "title": c["metadata"]["title"]} for c in chunks]
    return messages, sources
```

### 任务 3：Sources 怎么传给前端？（MVP 方案）

流式响应不好夹带 JSON metadata，MVP 推荐 **方案 A**：

**方案 A（推荐）：先检索、再流式**

1. 后端在流开始前，通过 **响应 Header** 传递 sources：

```python
return StreamingResponse(
    generate(),
    media_type="text/event-stream",
    headers={"X-RAG-Sources": json.dumps(sources)},  # 前端 fetch 后读 res.headers
)
```

2. 前端在 `chatService.ts` 里读取 `res.headers.get("X-RAG-Sources")`

**方案 B（进阶）：改用 SSE 格式** 每条消息 `data: {"type":"chunk","text":"..."}\n\n`，最后 `data: {"type":"sources",...}\n\n`。Step 05 可升级。

---

## 4. 目标架构（本 step 完成后）

```text
server/
  main.py                    # 精简，只调 chat_service
  services/
    chat_service.py          # 编排：RAG + LLM
    rag_service.py           # 检索
    embedding_service.py
  rag/
    chunker.py
    ingest.py
```

---

## 5. 验收方式

1. 问 Sophie：「你做过哪些 LLM 项目？」→ 回答应提到 `projects.md` 里的真实项目名
2. 问 Sophie：「你得过诺贝尔物理学奖吗？」→ 应回答「资料中没有提到」
3. 切换到 Naval，问「什么是杠杆？」→ 回答基于 Naval 文档，不混入 Sophie 简历
4. 后端日志或 Header 中能看到检索到的 sources 列表
5. 流式输出仍然正常工作（Step 03 的能力不退化）

---

## 6. 常见错误排查

### LLM 仍然编造内容

**原因**：system prompt 不够强硬，或检索到的 chunks 不相关。  
**解决**：加强「只基于资料回答」指令；检查 top-k 结果是否命中。

### 流式输出变卡

**原因**：检索 + embedding 在流式 generator 内部同步调用，阻塞了。  
**解决**：检索放在 `StreamingResponse` **之前**完成，generator 只负责 yield LLM chunks。

### Header 传 sources 前端读不到

**原因**：CORS 默认不暴露自定义 Header。  
**解决**：后端 CORS 加 `expose_headers=["X-RAG-Sources"]`；Vite Proxy 模式下通常无此问题。

---

## 7. 今日学习记录

```md
## 今日复盘

- 今天我理解了：
- 今天我亲手实现了：
- 今天我卡住了：
- 明天我要继续：Step 05 前端引用展示
```
