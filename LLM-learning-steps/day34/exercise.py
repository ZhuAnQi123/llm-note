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
        # Lambda是python 中匿名函数的意思【问末有例子】
        func=lambda q: str(query_engine.query(q)),
        description="当你需要回答关于公司产品、技术细节或 Cursor 的相关问题时，使用此工具。"
    )
]

# 3. 初始化 LangChain Agent (作为对话大脑)
# 理解一下什么是agent
# Agent 不是 LLM 本身，而是"LLM + 工具 + 决策逻辑"的封装

# 错误的认知
#agent = qwen  # ❌ Agent不是模型

# 正确的理解
#agent = LLM + 工具集 + 决策策略
#       ↑      ↑        ↑
#     大脑    双手     思维方式


llm = ChatDashScope(model_name="qwen-turbo")
agent = initialize_agent(
    tools,
    llm,
    # Agent类型：决定如何思考（ReAct、OpenAI Functions等）
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True # 开启详细日志，看 AI 的思考过程 (CoT)
)

# --- Main ---
if __name__ == "__main__":
    print("🤖 Agent 已准备就绪，可以提问了！")
    
    # AI 应该会决定调用 KnowledgeBase 工具
    response = agent.run("请根据知识库告诉我，Cursor 是由哪家公司开发的？")
    print(f"\nFinal Answer: {response}")



# Lambda 匿名函数
# 传统的函数定义方式
#def my_function(q):
#    return str(query_engine.query(q))

# Lambda 方式（完全相同的作用）
#my_function = lambda q: str(query_engine.query(q))

# 两者的使用方式一样
#result = my_function("什么是AI？")