# Day 34：框架对比与选择 - 什么时候用 LangChain？什么时候用 LlamaIndex？

## 🎯 学习目标
*   对比 **LangChain** 与 **LlamaIndex** 的优缺点、应用场景。
*   理解 **Orchestration (编排)** vs **Retrieval (检索)** 的区别。
*   掌握什么时候“混用”这两个框架。
*   学习如何在一个项目中集成两个框架的长处。

---

## 📚 学习资源
*   **LangChain vs LlamaIndex**: [Blog Post Comparison](https://www.topbots.com/langchain-vs-llamaindex-for-llm-apps/)
*   **Integration Example**: [LlamaIndex to LangChain Conversion](https://docs.llamaindex.ai/en/stable/community/integrations/using_llamaindex_with_langchain/)
*   **Reddit Discussions**: [Search on r/LangChain](https://www.reddit.com/r/LangChain/) (看看真实开发者在用什么)

---

## 🛠️ 新手必会知识点 (附例子)

### 1.1 一句话说清楚

| 框架 | 核心定位 | 一句话理解 |
|------|---------|-----------|
| **LlamaIndex** | 检索专家 | 核心功能是 **RAG (知识库问答)**.解决“LLM对我的私有数据一无所知”的问题 |
| **LangChain** | 编排大师 | 构建一个复杂的 **Agent**调用外部工具，解决“LLM只会想和说，不会做事”的问题 |

### 1.2 设计哲学差异

```
LlamaIndex 的思考方式：
“如何让LLM高效、精准地找到最相关的信息？”
→ 专注：数据加载 → 索引构建 → 语义检索 → 召回优化

LangChain 的思考方式：
“如何让LLM完成一个复杂的多步骤任务？”
→ 专注：组件编排 → 工具调用 → 状态管理 → 流程控制
```




## Part 2: 核心概念深度解析 🔬

### 2.1 什么是 Retrieval（检索）？

**检索**是指从知识库中找到与用户问题最相关的信息片段的过程。

```python
# 检索的典型流程
用户问题："感时花溅泪的下一句是什么？"
    ↓
[Embedding模型] 将问题转为向量
    ↓
[向量检索] 在知识库中找最相似的文本块
    ↓
检索结果："恨别鸟惊心。烽火连三月..."
```

**LlamaIndex 在检索上的专长**：
- 多种索引类型：向量索引适合语义搜索，关键词索引适合精确匹配
- 高级检索策略：递归检索、检索重排序(Cross-Encoder)、多索引融合
- 精细控制：similarity_top_k、similarity_cutoff等参数可调

### 2.2 什么是 Orchestration（编排）？

**编排**是指协调多个组件（LLM调用、工具使用、条件判断等）按顺序执行的过程。

```python
# 编排的典型流程
用户问题："帮我订一张明天去北京的最便宜机票"
    ↓
[Agent思考] 我需要调用：1)搜索航班API 2)比价 3)下订单
    ↓
[调用工具1] search_flights("北京", "2024-01-15")
    ↓
[调用工具2] compare_prices(搜索结果)
    ↓
[执行动作] book_cheapest_flight()
    ↓
[生成回复] "已为您预订航班XXXX，价格¥500"
```

**LangChain 在编排上的专长**：
- LCEL表达式语言：声明式组合组件
- LangGraph：有状态的图结构编排，支持循环和分支
- Agent框架：ReAct模式的思考-行动-观察循环（比如我们之前学习的，模型思考去判断是否要调用外部工具然后再回答就是ReAct）

### 2.3 两者的互补关系

> “LlamaIndex 解决LLM如何获取私有数据，LangChain 解决LLM如何整合基础工具与流程”

```
┌─────────────────────────────────────────────────────────┐
│                    LangChain 编排层                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Step1: 理解用户意图 → Step2: 调用工具 → Step3: 整合结果 │   │
│  └─────────────────────────────────────────────────┘   │
│                           ↓ 需要知识时调用                │
│  ┌─────────────────────────────────────────────────┐   │
│  │           LlamaIndex 检索层                       │   │
│  │  向量索引 │ 关键词索引 │ 树形索引 │ 路由查询引擎    │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---


## Part 3: 什么时候混用？🤝

### 3.1 核心原则

> “LangChain和LlamaIndex是互补关系而非替代关系”

**应该混用的场景**：
- 需求既需要**高质量的知识检索**（LlamaIndex的强项），又需要**复杂的流程控制**（LangChain的强项）
- Agent的工作核心是“基于知识库回答问题”，但同时需要调用其他工具



### 3.2 架构模式

**模式1：LlamaIndex作为LangChain的检索工具**
```
LangChain Agent
    ├── Tool: LlamaIndex查询引擎（检索知识库）
    ├── Tool: 搜索API
    ├── Tool: 计算器
    └── Tool: 数据库查询
```

**模式2：LlamaIndex处理索引，LangChain处理流程**
```
用户请求 → LangChain (意图识别/路由)
              ↓
         ┌────┴────┐
         ↓         ↓
    LlamaIndex  其他API
    (检索知识)   (调用服务)
         ↓         ↓
         └────┬────┘
              ↓
         LangChain (结果整合)
```


---


## 💻 完整可运行范例：混搭实战 - 把 LlamaIndex 作为 LangChain 的工具
这是一个典型的“企业级 AI 助手”架构：LangChain 负责对话和决策，LlamaIndex 负责查文档。

```python
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.dashscope import DashScope
from llama_index.embeddings.dashscope import DashScopeEmbedding
from langchain.agents import Tool, initialize_agent, AgentType
from langchain_community.chat_models import ChatDashScope

# 1. 配置 LlamaIndex (作为数据引擎)
Settings.llm = DashScope(model_name="qwen-turbo")
Settings.embed_model = DashScopeEmbedding(model_name="text-embedding-v2")

# 假设 data 文件夹里有我们的知识文档
documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

# 2. 定义 LangChain 工具 (Tool)
tools = [
    Tool(
        name="KnowledgeBase",
        func=lambda q: str(query_engine.query(q)),
        description="当你需要回答关于公司产品、技术细节或 Cursor 的相关问题时，使用此工具。"
    )
]

# 3. 初始化 LangChain Agent (作为对话大脑)
llm = ChatDashScope(model_name="qwen-turbo")
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True # 开启详细日志，看 AI 的思考过程 (CoT)
)

# --- Main ---
if __name__ == "__main__":
    print("🤖 Agent 已准备就绪，可以提问了！")
    
    # AI 应该会决定调用 KnowledgeBase 工具
    response = agent.run("请根据知识库告诉我，Cursor 是由哪家公司开发的？")
    print(f"\nFinal Answer: {response}")
```

---

## 💡 老师的建议 (必看)
1.  **不要过度设计 (Over-engineering)**：如果你的需求只是简单的 PDF 问答，用 **LlamaIndex** 就够了，别强行加 LangChain。
2.  **Verbose=True 是你的好帮手**：在开发 Agent 时，开启 `verbose=True` 能让你看到 AI 到底在想什么（Action, Action Input, Observation），这是调试 Agent 的唯一方法。
3.  **未来的方向**：目前行业内逐渐倾向于用 **LlamaIndex** 处理数据管道，用 **LangGraph (LangChain 的进阶)** 处理复杂的状态机流程。

---

## 📝 本日练习
1.  运行上面的混搭代码。看看控制台里显示的 `Thought`, `Action`, `Observation` 是不是和 Day 23 学的 **Chain of Thought (思维链)** 一模一样？
2.  **思考题**：如果用户问的是“今天天气怎么样？”，上面的 Agent 会去知识库里查吗？如果不查，它会报错吗？（提示：查找 **ReAct** 模式的逻辑）。
3.  挑战：再给 Agent 增加一个工具 `get_current_time`（参考 Day 22 的 Function Calling 逻辑），看看 Agent 能否在“查知识”和“报时间”之间自由切换。
    