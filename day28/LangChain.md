# 🚀 LangChain 学习文档：从入门到实战

这是一份帮助你快速上手指南，结合你正在学习的 RAG 知识，让你理解 LangChain 如何帮助我们构建 LLM 应用。文档附带官网链接和大量可运行的代码示例。


## 📚 目录
1. [LangChain 是什么](#1-langchain-是什么)
2. [为什么需要 LangChain](#2-为什么需要-langchain)
3. [核心概念速览](#3-核心概念速览)
4. [环境搭建](#4-环境搭建)
5. [实战代码示例](#5-实战代码示例)
6. [学习路径建议](#6-学习路径建议)
7. [常见陷阱与解决方案](#7-常见陷阱与解决方案)
8. [资源汇总](#8-资源汇总)


## 1. LangChain 是什么

**一句话定义**：LangChain 是一个用于开发由大语言模型驱动的应用程序的开源框架。

**官方定位**：它提供标准化的接口和组件，帮助开发者快速构建复杂的 LLM 应用，而不用从零写大量样板代码。

> 🔗 **官网链接**：[https://www.langchain.com/](https://www.langchain.com/)
> 
> 📖 **官方文档（中文）**：[https://docs.langchain.org.cn/](https://docs.langchain.org.cn/)


## 2. 为什么需要 LangChain

在实际开发中，直接调用 LLM API 会遇到三大痛点：

| 痛点 | 说明 | LangChain 的解决方案 |
|------|------|---------------------|
| **知识边界固化** | 模型无法获取实时或私有数据 | **Retrieval 模块**：集成向量数据库实现 RAG |
| **能力扩展受限** | 模型无法与外部系统交互 | **Tools + Agents**：让模型调用 API、数据库等 |
| **开发效率低下** | 实现 RAG 需要手动写 2000+ 行代码 | **Chains + Components**：标准化组件，几行代码搞定 |

**简单来说**：LangChain 之于 LLM 应用，就像 Spring 之于 Java 后端、React 之于前端——它让你专注业务逻辑，而不是重复造轮子。


## 3. 核心概念速览

LangChain 采用模块化设计，包含六大核心组件：

### 3.1 概念地图

```
┌─────────────────────────────────────────────────────────────┐
│                      LangChain 架构                          │
├─────────────────────────────────────────────────────────────┤
│  Model I/O      │  Prompts │ Models │ Output Parsers        │
│ ─────────────── │  模板管理  │ 统一接口 │  结构化输出          │
├─────────────────────────────────────────────────────────────┤
│  Retrieval      │  Document Loaders │ Text Splitters        │
│  (RAG 核心)      │  Vector Stores    │ Embeddings           │
├─────────────────────────────────────────────────────────────┤
│  Chains         │  将多个组件串联成完整工作流                  │
├─────────────────────────────────────────────────────────────┤
│  Agents         │  LLM 自主决策 + 工具调用                    │
├─────────────────────────────────────────────────────────────┤
│  Memory         │  跨对话轮次保持上下文                        │
├─────────────────────────────────────────────────────────────┤
│  Callbacks      │  日志、监控、追踪（如 Langfuse）             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 各组件一句话解释

| 组件 | 英文 | 一句话解释 | 类比 |
|------|------|-----------|------|
| **模型接口** | Model I/O | 统一调用各种 LLM（OpenAI、通义千问等） | 充电器万能插头 |
| **提示词模板** | PromptTemplate | 可复用的提示词，支持动态变量 | 邮件模板 |
| **检索** | Retrieval | 从向量数据库找相关文档，实现 RAG | 搜索引擎 |
| **链** | Chains | 把多个步骤串起来执行 | 工厂流水线 |
| **智能体** | Agents | LLM 自己决定调用什么工具 | 自动驾驶 |
| **记忆** | Memory | 记住之前的对话内容 | 聊天记录 |
| **回调** | Callbacks | 监控每一步的执行情况 | 行车记录仪 |


## 4. 环境搭建

### 4.1 安装 LangChain

```bash
# 基础安装
pip install langchain

# 推荐：安装常用集成
pip install langchain langchain-openai langchain-community chromadb tiktoken
```

> **注意**：LangChain 采用模块化设计，核心包 `langchain` 不包含具体集成，需要单独安装对应集成包（如 `langchain-openai`、`langchain-community`）。

### 4.2 配置 API Key

```python
# 方式一：环境变量（推荐）
import os
os.environ["OPENAI_API_KEY"] = "your-api-key"

# 方式二：直接在代码中传入（不推荐生产环境）
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(api_key="your-api-key")
```

### 4.3 验证安装

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo")
response = llm.invoke("Say hello!")
print(response.content)  # 应该输出 'Hello!'
```


## 5. 实战代码示例

### 🎯 示例 1：最基本的 LLM 调用

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# 1. 初始化模型
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# 2. 方式一：简单调用
response = llm.invoke("什么是RAG？")
print(response.content)

# 3. 方式二：多轮对话（带系统提示）
messages = [
    SystemMessage(content="你是一个AI技术专家，用通俗易懂的方式解释概念。"),
    HumanMessage(content="什么是RAG？")
]
response = llm.invoke(messages)
print(response.content)
```

**说明**：
- `invoke()` 是最常用的调用方法，返回完整的响应对象
- `temperature` 控制输出的随机性（0=确定性强，1=更随机）


### 🎯 示例 2：PromptTemplate + Chain（提示词模板与链）

这是从原始调用走向工程化的第一步。

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. 定义 prompt 模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}专家，请用{style}的风格回答问题。"),
    ("user", "{question}")
])

# 2. 初始化模型
llm = ChatOpenAI(model="gpt-3.5-turbo")

# 3. 输出解析器（将LLM输出转为字符串）
output_parser = StrOutputParser()

# 4. 使用 LCEL (LangChain Expression Language) 构建链
#    | 符号表示将前一个的输出传给后一个
chain = prompt | llm | output_parser

# 5. 调用链
result = chain.invoke({
    "role": "Python",
    "style": "简洁",
    "question": "什么是装饰器？"
})
print(result)
```

**LCEL 核心语法**：`chain = 组件1 | 组件2 | 组件3`


### 🎯 示例 3：RAG 完整实现（与你的学习目标对应！）

这是 LangChain 最强大的场景之一——**只用 20 行代码实现一个完整的文档问答系统**：

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA

# ============ 第一步：加载文档 ============
loader = TextLoader("my_document.txt")  # 也支持 PyPDFLoader, WebBaseLoader 等
documents = loader.load()

# ============ 第二步：文本分块 ============
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # 每块最大字符数
    chunk_overlap=50     # 块间重叠，避免信息丢失
)
docs = text_splitter.split_documents(documents)

# ============ 第三步：向量化 + 存储 ============
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(docs, embeddings)  # 自动计算向量并存储

# ============ 第四步：创建检索器 ============
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})  # 返回top3相关文档

# ============ 第五步：构建 RAG 问答链 ============
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(),
    chain_type="stuff",      # 将检索到的文档全部塞入 prompt
    retriever=retriever,
    return_source_documents=True  # 返回引用来源
)

# ============ 调用 ============
result = qa_chain.invoke({"query": "文档中提到了什么关键技术？"})
print(f"答案：{result['result']}")
print(f"引用来源：{result['source_documents']}")
```

**对照你手写 RAG 的实现**：
- 你手动做：加载 → 分块 → embedding → 存向量 → 检索 → 构造 prompt → 调用
- LangChain 做：上述代码 5 步搞定，且支持 20+ 种文档格式、10+ 种向量数据库

> **分块参数建议**：中文技术文档推荐 `chunk_size=800~1200`，`chunk_overlap=80~150`


### 🎯 示例 4：Memory（让 AI 记住你说过的话）

```python
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# 1. 带记忆的对话链
llm = ChatOpenAI()
memory = ConversationBufferMemory()  # 简单缓存历史
conversation = ConversationChain(llm=llm, memory=memory)

# 2. 多轮对话
print(conversation.predict(input="我叫小明，我喜欢编程。"))
# AI: 你好小明！编程是个很棒的爱好。

print(conversation.predict(input="还记得我叫什么吗？"))
# AI: 当然记得，你叫小明。

# 3. 查看记忆内容
print(memory.load_memory_variables({}))
```

**记忆类型选择**：
| 类型 | 说明 | 适用场景 |
|------|------|----------|
| `ConversationBufferMemory` | 缓存所有历史 | 短对话 |
| `ConversationBufferWindowMemory` | 只保留最近 K 轮 | 控制 token 消耗 |
| `ConversationSummaryMemory` | 用 LLM 总结历史 | 长对话 |


### 🎯 示例 5：Agent（让 AI 自己决定用什么工具）

Agent 是 LangChain 最令人兴奋的特性——LLM 可以自主决策调用哪些工具来完成任务。

```python
from langchain_openai import ChatOpenAI
from langchain.agents import tool, create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate

# 1. 定义工具（用 @tool 装饰器）
@tool
def calculate(expression: str) -> str:
    """计算数学表达式的结果。输入应该是一个有效的数学表达式，如 '2+3*4'。"""
    try:
        return str(eval(expression))
    except:
        return "计算错误，请检查表达式"

@tool
def get_current_weather(city: str) -> str:
    """获取指定城市的天气（模拟数据）。"""
    weather_data = {"北京": "晴朗 25°C", "上海": "多云 28°C", "深圳": "阵雨 30°C"}
    return weather_data.get(city, f"未找到{city}的天气数据")

# 2. 初始化模型和工具
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
tools = [calculate, get_current_weather]

# 3. 定义 prompt（ReAct 格式）
prompt = PromptTemplate.from_template("""
你是一个可以调用工具的助手。你有以下工具可用：

{tools}

使用以下格式回答：
Question: 用户的问题
Thought: 思考需要用什么工具
Action: 工具名称，必须是 [{tool_names}] 之一
Action Input: 工具的输入
Observation: 工具返回的结果
... (重复 Thought/Action/Observation 如果需要)
Thought: 我现在可以回答用户了
Final Answer: 对用户的最终回答

开始！

Question: {input}
Thought: {agent_scratchpad}
""")

# 4. 创建 Agent
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 5. 运行 Agent
result = agent_executor.invoke({
    "input": "计算 (25 + 17) * 3 的结果，然后告诉我北京今天的天气。"
})
print(result["output"])
```

> **注意**：Agent 的生产环境使用需要谨慎，建议限制最大步数、添加 fallback，避免无限循环或昂贵调用。


## 6. 学习路径建议

根据你的情况（已有手工实现 RAG 的经验），推荐以下 2-3 周学习路径：

### 第 1 周：核心概念 + 基础链
- ✅ **目标**：掌握 PromptTemplate、LCEL、OutputParser
- 🛠️ **实践项目**：构建一个简单的问答机器人
- 📖 **推荐资料**：[官方 Quickstart](https://docs.langchain.com/oss/python/langchain/quickstart)

### 第 2 周：RAG 深入（与你当前学习最相关）
- ✅ **目标**：用 LangChain 替代你的手工 RAG，理解其优势与局限
- 🛠️ **实践项目**：企业文档问答系统
- 📖 **推荐资料**：
  - [官方 RAG 教程](https://docs.langchain.org.cn/oss/python/learn#rag-agent)
  - 文本分块策略调优

### 第 3 周：Agent + Tools
- ✅ **目标**：学会让 LLM 调用外部工具
- 🛠️ **实践项目**：自动数据分析助手
- 📖 **推荐资料**：[官方 Agent 教程](https://docs.langchain.com/oss/python/langchain/quickstart)

### 可选进阶：LangGraph（复杂工作流）
- 当你觉得 Agent 太“黑盒”时，LangGraph 提供更强的可控性


## 7. 常见陷阱与解决方案

| 陷阱 | 表现 | 解决方案 |
|------|------|----------|
| **分块不当** | 检索不到信息或回答不完整 | 先用 `chunk_size=1000, overlap=200`，根据文档类型调优 |
| **忽略评估** | 上线后效果差 | 至少准备 20-50 个测试用例，建立评估集 |
| **Agent 无限循环** | 调用次数过多、费用飙升 | 限制 `max_iterations`；添加 fallback 规则 |
| **硬编码 API Key** | 代码泄露风险 | 使用 `python-dotenv` + `.env` 文件管理 |
| **版本不兼容** | 代码突然报错 | 使用 `pip freeze > requirements.txt` 锁定版本 |


## 8. 资源汇总

### 🔗 官方核心链接
| 资源 | 链接 | 用途 |
|------|------|------|
| 官网 | [langchain.com](https://www.langchain.com/) | 整体了解 |
| 文档中心 | [docs.langchain.com](https://docs.langchain.com/) | 最权威的学习资料 |
| 中文文档 | [docs.langchain.org.cn](https://docs.langchain.org.cn/) | 中文开发者首选 |
| API 参考 | [api.python.langchain.com](https://api.python.langchain.com/) | 查具体类/方法 |
| GitHub | [github.com/langchain-ai/langchain](https://github.com/langchain-ai/langchain) | 源码 + Issues |
| LangGraph | [langchain-ai.github.io/langgraph/](https://langchain-ai.github.io/langgraph/) | Agent 进阶 |

### 📖 教程与学习
- [官方 Learn 页面](https://docs.langchain.org.cn/oss/python/learn) - 按用例组织的教程
- [LangChain Academy](https://www.langchain.com/academy) - 官方课程

### 🛠️ 生态工具
- **LangSmith**：LLM 应用调试、评估、监控平台
- **LangServe**：将 LangChain 应用部署为 REST API

---

## 给你的最后建议

你正在**手工实现 RAG**，这是非常正确的学习路径。下一步可以这样做：

1. **先完成手写 RAG**（你当前目标）→ 彻底理解原理
2. **然后用 LangChain 重构** → 体会框架带来的效率提升
3. **对比两者**，思考：哪些抽象是好的？哪些是过度设计？
4. **根据项目需要决定**：简单项目用手写，复杂项目用 LangChain

记住：**框架是工具，不是目的**。理解原理的你，已经比很多只会调包的人走得更远。

加油！🚀