import os
import json
from dashscope import Generation
from http import HTTPStatus

# 1. 准备本地工具函数
def get_weather(city):
    """
    模拟一个天气查询 API (实际可对接和风天气或高德地图 API)
    """
    mock_weather_data = {
        "北京": "☀️ 晴, 25°C",
        "上海": "☁️ 多云, 22°C",
        "广州": "🌧️ 雨, 28°C"
    }
    return mock_weather_data.get(city, f"暂未收录 {city} 的天气数据")

# 2. 定义工具描述列表
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的实时天气情况",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称，如北京、上海"}
                },
                "required": ["city"]
            }
        }
    }
]

def chat_with_tools(user_query):
    messages = [
        {'role': 'system', 'content': '你是一个贴心的天气助手。'},
        {'role': 'user', 'content': user_query}
    ]

    # 第一步：发送用户问题 + 工具定义给 Qwen
    print(f"🚀 用户问：{user_query}")
    response = Generation.call(
        model="qwen-max", # 使用更智能的 Qwen-Max 处理工具调用
        messages=messages,
        tools=tools,
        result_format='message'
    )

    if response.status_code == HTTPStatus.OK:
        assistant_message = response.output.choices[0]['message']
        messages.append(assistant_message) # 把 AI 的回复存入上下文

        # 第二步：检查 AI 是否想调用工具
        if assistant_message.get("tool_calls"):
            for tool_call in assistant_message["tool_calls"]:
                function_name = tool_call['function']['name']
                arguments = json.loads(tool_call['function']['arguments'])
                
                if function_name == "get_weather":
                    print(f"🛠️  AI 请求调用函数: {function_name}, 参数: {arguments}")
                    # 第三步：运行本地函数
                    result = get_weather(arguments['city'])
                    print(f"✅ 函数返回结果: {result}")

                    # 第四步：将结果反馈给 AI，让它最终回复用户
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call['id'],
                        "name": function_name,
                        "content": result
                    })
            
            # 再次调用模型
            final_response = Generation.call(
                model="qwen-max",
                messages=messages,
                result_format='message'
            )
            return final_response.output.choices[0]['message']['content']
        else:
            return assistant_message['content']
    else:
        return f"Error: {response.message}"

# --- Main ---
if __name__ == "__main__":
    query = "上海今天天气如何？"
    answer = chat_with_tools(query)
    print(f"\n🤖 AI 最终回复: \n{answer}")
