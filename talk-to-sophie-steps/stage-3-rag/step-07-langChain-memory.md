# Step 07：使用 LangChain 新式封装实现多轮对话记忆

日期：2026-06-22  
阶段：阶段 3 - 个人知识库 RAG  
目标：使用 LangChain `RunnableWithMessageHistory` 为 Chat API 添加多轮对话记忆，并将其限制在保留最近 5 轮（短期记忆），同时不将每次检索的 RAG Context 污染进历史记录。

---

## 1. 今天的学习目标

【相关知识点】

- **LangChain 消息历史（LCEL）**：使用 `RunnableWithMessageHistory` 搭配 `InMemoryChatMessageHistory`。
- **系统提示词与记忆隔离**：把 System Prompt（包含每次检索到的 RAG chunk）作为每一轮单独传入的变量，**不写入**到历史记录里，从而避免 Token 随轮次无限爆炸！
- **短期记忆截断**：通过在 `get_session_history` 时截断 `history.messages` 列表，只保留最近的 N 条聊天记录（例如 5 轮对话 = 10 条消息）。

---

## 2. 准备工作

由于我们通过 LangChain 的新式封装调用 OpenAI 兼容接口，请确保你安装了 `langchain-openai` 包。如果还没有安装，可以通过下面的命令安装：

```bash
pip install langchain-openai
```

_(你也可以把它补充进 `server/requirements.txt` 中)_

---

## 3. 今天的实操任务

### 任务 1：更新 schemas 支持 session_id（可选但推荐）

要隔离不同页面刷新或不同用户的对话，我们需要传入一个 `session_id`。修改 `server/schemas.py`，给 `ChatRequest` 加上 `session_id` 字段（给定一个默认值方便向后兼容）：

```python
from pydantic import BaseModel
from enum import Enum

class Persona(str, Enum):
    sophie = "sophie"
    naval = "naval"

class ChatRequest(BaseModel):
    message: str
    persona: Persona
    session_id: str = "default_session"  # 新增：用于多轮对话历史隔离
```

### 任务 2：重构 `server/services/chat_service.py`

目前的代码仅仅是拼接字符串。按照项目规范，我们需要将大模型调用和记忆封装统一在这个文件中，做到职责分明。

将 `chat_service.py` 修改为以下逻辑：

```python
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

from services.rag_service import retrieve

# 全局的会话存储字典，用于在内存中保存多个 session 的对话历史
session_store = {}

def get_session_history(session_id: str):
    if session_id not in session_store:
        session_store[session_id] = InMemoryChatMessageHistory()

    # 【核心】保留 5 条短期记忆：每次获取 history 时，检查并截取最后 10 条消息 (5次 User + 5次 AI)
    # Langchain 中的一轮对话包含一条 HumanMessage 和一条 AIMessage
    if len(session_store[session_id].messages) > 10:
        session_store[session_id].messages = session_store[session_id].messages[-10:]

    return session_store[session_id]

# 1. 初始化 LangChain 模型实例
llm = ChatOpenAI(
    api_key=os.getenv("QWEN_API_KEY"),
    base_url=os.getenv("QWEN_BASE_URL"),
    model=os.getenv("QWEN_MODEL")
)

# 2. 构建带记忆的 prompt 模板
# system_prompt 作为变量每次动态注入，而 MessagesPlaceholder 会自动展开历史记录
prompt = ChatPromptTemplate.from_messages([
    ("system", "{system_prompt}"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{user_message}")
])

chain = prompt | llm

# 3. 封装为带历史记忆的 Runnable
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="user_message", # 告诉 LangChain 仅把 user_message 存为 HumanMessage，防止 system_prompt 污染历史
    history_messages_key="history",    # 历史记录注入到 prompt 中的占位符名称
)

def build_and_stream_chat(user_message: str, persona: str, session_id: str = "default_session"):
    """
    暴露给 main.py 的主干函数：返回 (流式生成器, sources)
    """
    # 1. 检索数据 (RAG)
    retrieved_results = retrieve(user_message, persona)

    # 2. 把检索出的结果拼接成 context
    context = "\n\n".join([f"知识库来源：{item['metadata']['source']}，标题：{item['metadata']['title']}，内容：{item['text']}" for item in retrieved_results])

    # 3. 动态组装 system prompt
    system_prompt = "你是 Sophie Zhu(朱安琪)个人网站中的AI交互分身，\n" if persona == "sophie" else "你是 Naval Ravikant(那瓦尔)个人网站中的AI交互分身，\n"
    system_prompt += f"请根据以下提供的知识库内容回答用户的问题，如果知识库内容无法回答用户的问题，请基于你的设定正常交流，不要编造资料中的内容。\n以下为知识库内容：\n{context}"

    # 4. 组装 sources 供前端引用展示
    sources = [
        {"source": item['metadata']['source'], "title": item['metadata']['title']}
        for item in retrieved_results
    ]

    # 5. 定义 Stream 生成器
    def generate():
        # 调用 langchain 封装链的 stream 方法
        for chunk in chain_with_history.stream(
            {
                "system_prompt": system_prompt,
                "user_message": user_message
            },
            config={"configurable": {"session_id": session_id}}
        ):
            if chunk.content:
                yield chunk.content

    return generate, sources
```

### 任务 3：修改 `server/main.py` 的路由

现在大模型调用已经被我们抽离到了 Service 层中。我们需要精简 `main.py` 的处理逻辑，不再在此处调用原生的 `OpenAI` Client。

```python
import json
from fastapi import FastAPI
from dotenv import load_dotenv
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from schemas import ChatRequest
from exceptions import raise_for_openai_error
# 引入新写好的核心方法
from services.chat_service import build_and_stream_chat

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # 此时调用的是我们封装好的带有上下文和 LangChain 记忆的业务方法
        generate, sources = build_and_stream_chat(
            request.message,
            request.persona.value,
            request.session_id # 加入 session ID 实现路由记忆隔离
        )

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={"X-RAG-SOURCES": json.dumps(sources)}
        )
    except Exception as e:
        raise_for_openai_error(e)

```

---

## 4. 验收方式

1. 开启后端，从前端发送两条连贯的信息：
   - 第一句：「你好，我叫 小明，我是来学习的。」
   - 第二句：「请问我刚才说我的名字是什么？」
   - **预期**：大模型能够顺利说出「你叫小明」，证明多轮记忆生效。
2. 不断和模型聊天，发过 6 条以上的对话之后，测试模型是否会忘记最开始提到的信息。
   - **预期**：在第 6 轮时，大模型应该不再记得第 1 轮的内容，证明截断 `session_store[session_id].messages` 的机制成功实现了「保留5条短期记忆」。
3. 验证流式打字机效果依然正常，并且前端能够正常接收到 sources。

---

## 5. 今日学习记录

```md
## 今日复盘

- 今天我理解了：如何使用 LangChain 新式的 `RunnableWithMessageHistory` 进行记忆管理。
- 今天我亲手实现了：通过 `session_id` 隔离记录、在 `get_session_history` 钩子中动态切片截断最近的 5 次短时记忆。
- 今天我卡住了：
- 明天我要继续：
```
