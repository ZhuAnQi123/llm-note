import os 
from langchain_community.chat_models import ChatDashScope
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import initialize_agent,AgentType

#设置api_key
os.environ["TAVILY_API_KEY"] = "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"
os.environ["DASHSCOPE_API_KEY"] = "sk-59c5b66dbe244feaaa26dabb23c5616b"

# 调用搜索工具Tavily
search = TavilySearchResults(k=3)

tools=[search]


# 2.准备Qwen LLM
llm =ChatDashScope(model_name="qwen-max",temperature=0)

# 3.初始化agent
agent=initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Main
if __name__=="__main__":
    try:
        response=agent.run('帮我查一下最近全球股市的涨跌')
    except Exception as e:
        print('出现了错误 {e}')