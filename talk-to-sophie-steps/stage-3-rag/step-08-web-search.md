# Step 08：联网搜索（Hybrid RAG） (Day 11)

日期：2026-06-15  
阶段：阶段 3 - 个人知识库 RAG  
目标：在本地 RAG 检索基础上，增加联网搜索能力——知识库不够或需要最新信息时，自动补充 Web 结果。

---

## 1. 今天的学习目标

【相关知识点】

- **Hybrid RAG（混合检索）**：不只用向量库，还结合实时 Web 搜索。本地库擅长「你的简历 / 那瓦尔经典观点」；联网擅长「最新技术动态 / 知识库没有的细节」。
- **何时触发联网？** 常见策略：
  1. **相似度阈值**：RAG top-1 score < 0.7 → 触发搜索
  2. **关键词规则**：用户问题含「最新」「今天」「2026」等 → 触发搜索
  3. **显式开关**：前端加一个「🌐 联网搜索」toggle（可选）
- **引用来源分级**：本地 chunk 显示 `📎 resume.md`；Web 结果显示 `🔗 标题 · domain.com`，让用户知道信息从哪来。

---

## 2. 对应 requirement.md

> Hero 区域要证明你懂 **多 Agent 路由 + 工具链**。  
> Agent Flow 画布里已有 `Tool Executor` 节点——联网搜索就是第一个真实落地的 **Tool**。

```text
用户问题
  → RAG 检索（本地 VectorDB）
  → [可选] Web Search（联网）
  → 合并 Context → LLM 生成 → 流式返回 + 引用
```

---

## 3. 推荐技术选型

| 组件 | 推荐 | 说明 |
| --- | --- | --- |
| 搜索 API | [Tavily API](https://tavily.com) | LLM 场景常用，返回已清洗的 snippet，有免费额度 |
| 备选 | Serper / Bing Search API | 可自行对比 |
| 密钥 | `.env` 新增 `TAVILY_API_KEY` | **绝不放前端** |

`.env` 示例：

```env
TAVILY_API_KEY=tvly-xxx
WEB_SEARCH_ENABLED=true
WEB_SEARCH_MAX_RESULTS=3
```

---

## 4. 今天的实操任务

为了实现“条件触发式”联网搜索（针对 Naval Persona），你需要按照以下顺序改动代码：

### 任务 1：修改数据模型接收控制开关

**文件**：`server/schemas.py` 在请求体模型中加入 `web_search` 字段，允许前端显式要求联网。

```python
class ChatRequest(BaseModel):
    message: str
    persona: Persona
    session_id: str = "default_session"
    web_search: bool = False  # 新增：显式联网开关
```

### 任务 2：封装独立的搜索服务

**文件**：`server/services/web_search_service.py` (🔥 新建文件) 将联网能力单独封装，避免污染原有 LangChain 业务逻辑。你可以使用你选定的搜索 API（如 Tavily 或 duckduckgo）。

- 编写核心方法 `perform_web_search(query: str, top_k: int = 3) -> list[dict]`
- **关键设计**：让返回格式与 `rag_service.retrieve` 保持一致，以便后续无缝拼接。
  ```python
  # 统一的返回格式要求
  [
      {
          "text": "网页正文片段...",
          "metadata": {"source": "网页URL", "title": "网页标题", "type": "web"}
      }
  ]
  ```

### 任务 3：在核心层实现路由与规则判定

**文件**：`server/services/chat_service.py` 在 `build_and_stream_chat` 方法中，在组装 `system_prompt` **之前**加入你的路由判断逻辑。

- 引入 `re` 正则模块和 `perform_web_search`。
- 接收 `web_search` 参数。
- 实现规则树判定：

  ```python
  # 1. 正常执行 RAG 检索
  retrieved_results = retrieve(user_message, persona)

  need_search = False

  # 仅针对 Naval 开启智能路由判定 (或者全开也行，视你需求而定)
  if persona == "naval":
      # 规则 1：前端强制开启
      if web_search:
          need_search = True

      # 规则 2：关键词命中
      elif re.search(r"最新|最近|今天|2026", user_message.lower()):
          need_search = True

      # 规则 3：RAG 无结果或结果置信度低 (注意分析距离分数的意义，距离越大越不相似)
      elif not retrieved_results:
          need_search = True
      else:
          # 假设 distances 越小越好。你需要观察日志确认你的阈值到底设多少合适。
          top_score = retrieved_results[0].get('score', 0)
          if top_score is None or top_score > 1.2: # L2距离举例
              need_search = True

  # 执行搜索并合并上下文
  if need_search:
      web_results = perform_web_search(user_message)
      retrieved_results = web_results + retrieved_results # 合并结果
  ```

### 任务 4：API 层透传参数

**文件**：`server/main.py` 修改 `/api/chat` 的入参提取逻辑，将前端传来的 `web_search` 传递给核心业务层。

```python
generate, sources = build_and_stream_chat(
    request.message,
    request.persona.value,
    request.session_id,
    request.web_search  # 新增透传
)
```

---

## 5. 目标架构（本 step 完成后）

完成以上步骤后，你的路由机制将演变为**「混合上下文拼装层 (Hybrid Context Builder)」**架构：

```text
               [User Request: "2026最新观点", web_search=False]
                             |
                             v
               +---------------------------+
               |     chat_service.py       |
               +---------------------------+
                             |
                   1. 默认查询 RAG VectorDB
                             |
                   2. 规则引擎判断 (Routing)
                      ├── 包含"最新" ? -> YES
                      └── 距离分数 > 1.2 ? -> NO
                             |
                    3. 触发 Web Search Tool
                             |
            4. 组装 [RAG Chunks + Web Snippets] -> 统一数据结构
                             |
                 5. 格式化注入 Prompt Context
                             |
                 6. LangChain 生成 & 流式返回
                             +
                 7. 组装复合 Sources (包含本地和 URL) -> Header 返回
```

**架构优势**：

---

## 6. 验收方式

1. **纯本地**：问 Sophie「你的技术栈」→ 只出现 `📎` 本地来源，不触发 Web
2. **强制联网**：打开 toggle，问「2026 年 React 最新版本是什么」→ 出现 `🔗` Web 来源
3. **自动 fallback**：关 toggle，问一个知识库完全没有的问题 → 自动联网（若你实现了阈值规则）
4. 流式输出不退化，sources Header 同时包含 local + web
5. `TAVILY_API_KEY` 只在 `.env`，Network 面板看不到 Key

---

## 7. Prompt 安全边界

联网结果也要加约束，避免模型把 Web snippet 当绝对真理：

```text
以下包含知识库资料和联网搜索结果。请优先使用知识库内容回答关于 Sophie/Naval 的问题。
联网结果仅供参考，请标注来源。若信息冲突，以知识库为准。
```

---

## 8. 常见错误排查

### 每次请求都联网（成本爆炸）

**原因**：阈值设太低或规则太宽。  
**解决**：默认关 toggle；仅低置信度或显式开启时才搜。

### Web 来源 chip 点不开

**解决**：`type: "web"` 的 chip 渲染为 `<a href={url} target="_blank">`。

### 联网超时拖慢首字

**原因**：搜索 API 慢。  
**解决**：设 5s timeout；搜索与 RAG 可 `asyncio.gather` 并行（进阶）。

---

## 9. 今日学习记录

```md
## 今日复盘

- 今天我理解了：
  1. `langchain_community` 中的 `TavilySearchResults` 工具比手写 requests 调用更简单，且返回结果格式良好，能够快速实现 Web Search 逻辑。
  2. Prompt 中传入的 query 要保留上下文，比如对 Naval persona 提问“你今年有什么演讲”，如果直接用该原话进行 Web Search，搜索引擎会丢失“Naval”这个上下文，导致搜出不相关的内容。需要在 Web Search 时携带 Persona 的背景信息。
- 今天我亲手实现了：
  1. 梳理了在项目中增加条件触发式联网搜索（Hybrid RAG）的四个具体任务（修改数据模型、新建搜索服务、实现路由判定、API透传参数）。
  2. 发现了 `ModuleNotFoundError: No module named 'langchain_community'` 的问题，提醒自己在使用新工具前要先 `pip install langchain_community`。
- 今天我卡住了：
  1. 前端显示来源的问题：当前所有来源都显示“知识库：”，没有针对网络搜索结果区分显示（如“网络：”和对应标题），需要修改前端逻辑。
  2. uvicorn 启动报错 `[Errno 48] Address already in use`，端口被占用，需要杀掉旧的后台进程。
  3. `chunker.py` 的逻辑和源文档格式不够规范，导致切片效果不好，后续需要整理一套 Markdown 文件规范（一级/二级标题、metadata等）再重新调整。
- 明天我要继续：阶段 4 Dashboard
```
