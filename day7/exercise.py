from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool, ToolRuntime
from langgraph.checkpoint.memory import InMemorySaver

# ToolStrategy 是一种强制Agent按照指定格式输出的策略，
# 它把Agent的输出格式化为我们定义的ResponseFormat类，
# 这样我们就可以更方便地解析和使用Agent的输出。
from langchain.agents.structured_output import ToolStrategy


# Define system prompt
# 因为是全局常量，比如配置，固定值，就可以定义为大写的变量，方便识别和维护。
SYSTEM_PROMPT = """You are an expert weather forecaster, who speaks in puns.

You have access to two tools:

- get_weather_for_location: use this to get the weather for a specific location
- get_user_location: use this to get the user's location

If a user asks you for the weather, make sure you know the location. 
If you can tell from the question that they mean wherever they are, use the get_user_location tool to find their location."""


#Define context schema
# dataclass是一个装饰器，可以将普通函数转换为LangChain的Tool对象，让Agent能够识别和调用它。
# Context是纯数据容器，不需要方法，只需要存储数据。我们把经常使用的数据放在这里
# 用于存储数据的类我们就使用@dataclass装饰器
@dataclass
class Context:
    """Custom runtime context schema."""
    user_id: str

# Define tools
# @tool装饰器将普通函数转换为LangChain的Tool对象，让Agent能够识别和调用它。
@tool
def get_weather_for_location(city: str) -> str:
# 下面 “”“ 符号包起来的是文档字符串，存储在对象的__doc__属性中，swagger文档有的会显示
    """Get the weather for a given city."""
    # For simplicity, we'll just return a dummy weather report.
    return f"The weather in {city} is sunny with a chance of puns."


@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """Get the user's location based on their user ID."""
    user_id = runtime.context.user_id
    return "Florida" if user_id == "1" else "SF"

# configure model
model = init_chat_model(
    "claude-sonnet-4-6",
    temperature=0
)


# Define response format
@dataclass
class ResponseFormat:
    """Custom response format schema."""
    # 返回一个轻松语句的response，必须返回
    punny_response: str
    weather_confitions: str|None = None



# 设置记忆
checkpointer=InMemorySaver()


# Create agent
agent = create_agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_weather_for_location,get_user_location],
    # 工具调用时需要的上下文，之后我们可以通过Context调用下上下文变量
    context_schema=Context,
    # response_format有好几种类型接受；ToolStrategy是其中一种方式
    # 比如传Pydantic 类型；字符串格式指令； dataclass等等都可以
    response_format=ToolStrategy(ResponseFormat),
    checkpointer=checkpointer
)


# 开始运行
# `thread_id` is a unique identifier 用来保留对话记忆
#这里也可以传user_id等你需要自定义的字段。
#比如说现在设置的model是"claude-sonnet-4-6"，如果你想每次切换模型可以在config里传入模型的名字，然后在agent里根据config里的模型名字来切换模型，这样就不需要每次都重新创建agent了。
config = {"configurable": {"thread_id": "1"}}
response=agent.invoke(
    {'message':[
        {
            'role': 'user',
            'content': 'What is the weather like in New York?'
        }
    ]},
    config=config,
    context=Context(user_id="1")
)


print(response['structured_response'])

