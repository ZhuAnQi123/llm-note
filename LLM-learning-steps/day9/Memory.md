# [Memory](https://docs.langchain.com/oss/python/concepts/memory#memory-overview)

*   **短期记忆**：负责记住“刚才说了什么”，是同一个`thread_id`下的聊天记录，主要用于保持对话流畅。
*   **长期记忆**：负责记住“用户是谁”，是`namespace`下的用户画像、偏好，主要用于提供个性化服务。


## 编译图`LangGraph`
先要理解编译图概念。`LangGraph`的名字里“Graph”不是数据可视化图表，而是计算机科学中的“有向图”——由**节点（Node**） 和**边（Edge）** 组成的网络。

* **节点**：就是处理业务逻辑的函数，比如“调用LLM”、“查询数据库”、“发送邮件”
* **边**：定义节点之间的流转方向，比如“调用LLM → 判断是否需要工具 → 如果需要就调用工具 → 回到LLM”

**简单类比**：就像一个工作流流程图。您画好流程图（定义节点和边），然后LangGraph负责按规则执行它。

`LangGraph`提供了一套标准的“三板斧”来实现这个目标。下面我将结合这套机制，为您拆解具体的实现步骤。



## 🎯 短期记忆——给对话装上“会话存档”

短期记忆的核心是管理好单次会话的历史消息，让AI不“断片”。LangGraph通过**检查点（Checkpointer）** 机制自动处理这一点。

**1. 核心配置**
通过MemorySaver方法，在编译图时传入`checkpointer`，并在每次调用时指定唯一的`thread_id`。这样，同一`thread_id`的消息就会被自动保存下来。

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, START

# ... (定义图节点，如chatbot节点)

# 1. 初始化一个内存检查点（MemorySaver用于开发测试）
checkpointer = MemorySaver()

# 2. 编译图时启用检查点
graph = StateGraph(MessagesState)
graph.add_node("chatbot", call_model)
graph.add_edge(START, "chatbot")
app = graph.compile(checkpointer=checkpointer) # 关键：挂载checkpointer

# 3. 使用时指定thread_id
config = {"configurable": {"thread_id": "user_123_session_456"}}
# 第一次提问
app.invoke({"messages": [("user", "你好，我叫小明")]}, config)
# 第二次提问，模型能记住名字
app.invoke({"messages": [("user", "我叫什么名字？")]}, config)

```


### 短期记忆checkpointer 的几种选择
| 类型 | 适用场景 | 示例 |
|------|---------|------|
| `MemorySaver` | 开发测试，单进程 | `from langgraph.checkpoint.memory import MemorySaver` |
| `SqliteSaver` | 本地持久化 | `from langgraph.checkpoint.sqlite import SqliteSaver` |
| `PostgresSaver` | 生产环境 | `from langgraph.checkpoint.postgres import PostgresSaver` |



**2. 进阶：管理过长的“记忆”**
如果对话非常长，超出大模型的上下文窗口，您可以使用**总结（Summarization）** 节点。当消息超过阈值时，调用LLM生成摘要替换原始消息，保持记忆精简。

```python
from langgraph.graph import MessagesState

# 在State中定义一个用于存储摘要的字段
class State(MessagesState):
    summary: str = ""
    
def summarize_conversation(state: State):
    """当消息过长时，调用LLM生成摘要"""
    if len(state["messages"]) > 10: # 假设超过10条就总结
        prompt = f"请总结以下对话：{state['messages']}"
        summary = llm.invoke(prompt)
        # 返回摘要，并清除历史消息
        return {"summary": summary, "messages": []}
    return {}
```

## 🎯 第二步：长期记忆——给AI装上“用户档案”

长期记忆用于跨会话存储用户信息（如偏好、背景）。LangGraph通过**存储（Store）** 接口和**Mem0**等专门工具实现。

**1. 方案一：使用LangGraph内置的Store**
在节点函数中，通过`runtime`参数访问`store`对象，实现手动读写。

```python
from langgraph.store.memory import InMemoryStore
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.checkpoint.memory import MemorySaver  

# 1. 先创建checkpointer（管理短期记忆）
checkpointer = MemorySaver()  # ← 这就是您问的checkpointer的来源

# 2. 再创建store（管理长期记忆）（生产环境可用PostgresStore等）
store = InMemoryStore()       # ← 长期记忆的存储


# 3. 【取读】在节点中读写长期记忆
def call_model(state, runtime):
    user_id = runtime.context.user_id # 假设从上下文获取用户ID


    # 这是Python的元组（tuple） 写法，LangGraph用它来表示层级路径。用来定位到preferences的位置
    namespace = ("user_profiles", user_id)
    
    # 读取记忆
    profile = runtime.store.get(namespace, "preferences")
    if profile:
        preferences = profile.value
        print(f"读取到用户偏好：{preferences}")
    
    # ... 调用模型生成回复 ...
    
    # 写入记忆（例如从对话中提取到偏好）
    runtime.store.put(namespace, "preferences", {"theme": "dark", "language": "zh"})
    return {"messages": [response]}

# 4.【存储】

# 先构建图
builder=StateGraph(MessageState)
builder.add_node('chatbot',call_modal)
builder.add_edge(START,'chatbot')


# 编译图时传入store
app = builder.compile(
    checkpointer=checkpointer,  # 短期记忆
    store=store                 # 长期记忆
)
```




**2. 方案二：使用Mem0（更智能，推荐）**
`Mem0`是一个专门的记忆层，它能自动从对话中提取、更新和检索相关事实，比手动管理更高效。

```python
from mem0 import Memory

# 初始化Mem0（默认使用内置向量库）
mem0_client = Memory()

def call_model_with_mem0(state, runtime):
    user_id = runtime.context.user_id
    # 本轮对话最新的一条消息
    query = state["messages"][-1].content

    # 1. 检索：根据当前问题搜索相关记忆
    memories = mem0_client.search(query, user_id=user_id)
    context = "\n".join([mem["memory"] for mem in memories]) if memories else ""

    # 2. 生成：将记忆作为上下文提供给LLM
    prompt = f"用户历史信息：{context}\n当前问题：{query}"
    response = llm.invoke(prompt)
    
    # 3. 存储：异步保存本轮对话的所有消息，供未来使用
    mem0_client.add(state["messages"], user_id=user_id)

    # 注意这歌return也有好几种写法的
    # 首先理解返回的messages要符合List[AIMessage] 类型
    # 所以完整写法应该是有带上role的
    return {'role':'ai','message':response.content}
    # 也可以使用python元祖方法
    return {'ai',response.content}
    # 也可以⬇️用AIMessage包裹
    return {'message':[AIMessage(content=response.content)]}
    # 如果response已经是AIMessage对象并且state中已经有消息了，就可以直接追加
    return {"messages": [response]}
```

### 🤝 实战模板：一个完整的双记忆Agent

为了更清晰地展示全貌，这里提供一个整合了两者思想的`LangGraph`节点逻辑（**并非完整可运行代码，重在理清思路**）：

```python
# 核心节点：处理用户输入，同时管理长短时记忆
def process_node(state, config, store, user_id):
    # 1. 短期记忆：直接从 state 中获取当前会话的完整消息列表
    conversation_history = state["messages"]
    
    # 2. 长期记忆：从 store（或 Mem0）中检索用户画像
    # 这里假设使用 LangGraph 自带的 store，并从名为 "user_profile" 的键中读取数据
    namespace = ("memories", user_id)
    item = store.get(namespace, "user_profile")
    user_profile = item.value if item else None
    
    # 3. 构建最终Prompt
    final_prompt = f"""
    [用户档案]：{user_profile}
    [对话历史]：{conversation_history}
    [用户最新提问]：{state["messages"][-1].content}
    请根据以上信息回答。
    """
    
    # 4. 调用LLM
    response = llm.invoke(final_prompt)
    
    # 5. 更新记忆（如果需要）
    # 例如，如果检测到用户说了“我喜欢科幻电影”，可以调用 store.put() 或 Mem0 的 API 更新档案
    # store.put(namespace, "user_profile", {"genre_preference": "sci-fi"})
    return {"messages": [response]}
```


## 知识压缩记忆🧠
*   **短期记忆**：`checkpointer = MemorySaver()`/由checkpointer**自动**管理/存在于当个会话
*   **长期记忆**：`store = InMemoryStore() `/要**手动**通过`store.get/put`存取/跨会话，跨用户存在`namespace`中

管理过长的记忆可以用`state.get("summary", "")`


代码对比记忆🧠
```py
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

# 创建两个组件
checkpointer = MemorySaver()  # 短期记忆
store = InMemoryStore()       # 长期记忆

# 编译(compile)时同时传入,把定义的“流程图”通过`compile`处理之后变成一个可以`invoke()`调用的应用程序（app）compile()之后返回的app对象，就是可以调用的最终程序。
app = builder.compile(
    checkpointer=checkpointer,  # 自动管理短期记忆
    store=store                 # 手动管理长期记忆
)

# === 短期记忆：自动存取 ===
config = {"configurable": {"thread_id": "session_001"}}
app.invoke({"messages": [HumanMessage("你好")]}, config)  # 自动保存
# 下次调用同一thread_id，自动读取历史

# === 长期记忆：手动存取 ===
namespace = ("user_profiles", "user_123")

# 写入
store.put(namespace, "preferences", {"food": "pizza", "language": "zh"})

# 读取
profile = store.get(namespace, "preferences")  # 需要手动调用

# 在节点中使用
def call_model(state, runtime):
    # 手动读取长期记忆
    user_profile = runtime.store.get(("user_profiles", user_id), "preferences")
    
    # 短期记忆自动在state中
    conversation = state["messages"]
    
    # 结合两者
    prompt = f"用户档案：{user_profile}\n对话历史：{conversation}"
    ...
```


### 💡 核心原则总结


1.  **职责分离**：`thread_id`管短期，`user_id`（命名空间）管长期。
2.  **按需检索**：长期记忆检索不是把整本“日记”塞给LLM，而是通过语义搜索找到最相关的几条记忆。
3.  **适时写入**：长期记忆的创建可以放在主流程（热路径）让LLM实时决策，也可以在后台异步处理以提升响应速度。








