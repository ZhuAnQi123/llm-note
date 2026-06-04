# Day 22：Function Calling (工具调用) - 让 AI 具备执行力

## 🎯 学习目标

- 理解 Function Calling 的核心原理：AI 不会真正运行代码，它只是告诉你“该运行哪个函数”。
- 学会向通义千问模型描述你的工具 (Tools/Functions)。
- 实现一个可以查询实时天气的 AI 助手 (模拟)。
- 掌握 Function Calling 的三步走流程。

---

## 📚 学习资源

- **通义千问 Function Calling 文档 (必读)**: [阿里 DashScope 工具调用](https://help.aliyun.com/zh/dashscope/developer-reference/function-call)
- **OpenAI Function Calling Guide**: [Function Calling 基础概念](https://platform.openai.com/docs/guides/function-calling)

---

## 🛠️ 新手必会知识点 (附例子)

### 1. Function Calling 的三个步骤 (必背)

1.  **用户提问**：将用户问题 + 你的函数定义列表一起发给 AI。
2.  **模型决定**：AI 返回“建议调用的函数名”和“参数”。
3.  **本地运行**：在你的 Python 代码中运行该函数，并将结果返回给 AI。
4.  **模型汇总**：AI 根据运行结果，给用户最终回复。

```js
    // ai运行结果response.output.choices[0] 类型
    //拿到返回之后去循环tool_calls看一下有没有我们传在tools里面的工具
{
    "role": "assistant",           # 角色固定为 assistant
    "content": "...",              # 如果没有调用工具，这里是文本回复；如果调用了工具，通常为 None
    "tool_calls": [                # 当模型决定调用工具时存在此字段
        {
            "id": "call_xxx",      # 工具调用的唯一ID
            "type": "function",    # 类型固定为 function
            "function": {
                "name": "get_weather",           # 要调用的函数名
                "arguments": "{\"city\": \"北京\"}"  # 参数的JSON字符串
            }
        }
    ]
}
```

### 2. 函数定义 (Tool Definition)

把fucntion参数传到tools，并且向模型详细描述函数的入参和作用，描述越清晰，AI 调用越准确。

```python
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
```

---

### lmm message的返回类型（用于判断是否需要调用工具）

```py
# 这是一个response.output.choices[0]['message']返回示例
{
  "role": "assistant",
  "content": "上海今天多云，22°C",
  # 当ai判断需要调用工具就会返回tool_calls
  # 此时就map这个数组， 看看他想要那个function.name
  "tool_calls": [
    {
      "id": "call_123456",
      "type": "function",
      "function": {
        "name": "get_weather",
        "arguments": "{\"city\": \"上海\"}"
      }
    }
  ]
}
```

## 💻 完整可运行范例：实时天气查询助手

这个代码通过 Function Calling 模拟了查询实时天气的完整流程。

```python
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
```

---

## 💡 老师的建议 (必看)

1. **AI 并不直接运行函数**：记住，AI 只是“大脑”，它负责出主意。真正干活的是你的 Python 运行环境（也就是你本地的 App）。
2. **Qwen-Max vs Qwen-Turbo**：在进行工具调用时，推荐使用 `qwen-max`，因为它对复杂指令和多层级 JSON 的理解能力更强。
3. **安全提醒**：永远不要让 AI 直接执行类似 `rm -rf /` 的毁灭性系统指令，即使它想调用，你作为代码编写者也要在本地函数里加上严格的校验。

---

## 📝 本日练习

1. 修改 `get_weather` 函数，加入一个新的城市并指定其天气，运行代码看 AI 能否正确识别。
2. 挑战：增加一个名为 `get_stock_price` (获取股票价格) 的新工具，并让 AI 既能回答天气问题，也能回答股票问题。
