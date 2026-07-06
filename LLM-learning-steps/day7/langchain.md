# [LangChain](https://docs.langchain.com/oss/python/langchain/quickstart?utm_source=chatgpt.com) 
是一个用于开发由大语言模型（LLM）驱动的应用程序的开源框架。它提供了一系列模块化工具和组件，帮助开发者将大模型与外部数据、计算能力以及各种 API 连接起来，构建更复杂、更实用的应用。



| 步骤 | 框架/工具 | 做什么 |
|-----|----------|-------|
| 1 | LangChain的`ConversationChain` | 替代手动维护消息列表 |
| 2 | LangChain的`ConversationSummaryMemory` | 理解“自动总结” |
| 3 | LangGraph的简单线性图 | 理解“节点”和“边” |
| 4 | LangGraph + MemorySaver | 理解“checkpointer” |

```python
# 90%的Chatbot场景，这个就够了
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

memory = ConversationBufferMemory()
chain = ConversationChain(llm=llm, memory=memory)
chain.predict(input="你好，我叫小明")  # 自动记住
```


### 分层次理解框架

| 层次 | 理解程度 | 示例（LangGraph） |
|-----|---------|------------------|
| 用户层 | 知道什么时候用 | “需要多步推理的任务用LangGraph” |
| API层 | 知道怎么调 | `graph.add_node("name", func)` |
| 机制层 | 知道大致原理 | “节点返回的东西会被合并到state” |
| 源码层 | 不需要理解 | `operator.add`怎么实现的 |

**您现在卡在了“机制层”，但当前只需要“API层”**。

