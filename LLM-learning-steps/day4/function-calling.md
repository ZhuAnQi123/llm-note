## 一、什么是 Function Calling（函数调用）

> **一句话**：让AI模型自己判断“什么时候该调用哪个函数、传什么参数”，然后你根据AI的输出去真正执行函数，再把结果返回给AI，让它生成最终回答。

流程：

1. 你告诉AI：“我有这些函数（名称、描述、参数结构）”
2. 用户问问题（比如“北京天气怎么样”）
3. AI判断 → 返回一个**函数调用请求**（不是最终答案）
4. 你本地执行真正的函数（查天气）
5. 把结果发给AI → AI生成自然语言回答

---

## API 调用时的关键参数

在请求 OpenAI API（或兼容接口）时，额外加上：

```python
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "北京天气如何"},
        {"role": "assistant", "content": None, "function_call": {...}},
        {
            "role": "function",
            "name": func_name,
            "content": result
        }
    ],
    functions=functions,           # 你定义好的函数列表
    function_call="auto"           # auto让AI自己决定，也可以强制指定函数
)
```

- `function_call="auto"`（推荐）
- 或 `function_call={"name": "get_current_weather"}` 强制调用

---

## 核心数据格式（JSON Schema）

你需要定义函数描述，传给AI的API：

```python
functions = [
    {
        "name": "get_current_weather",
        "description": "获取指定城市的当前天气",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，例如：北京"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "温度单位"
                }
            },
            "required": ["city"]
        }
    }
]
```

---

## 四、AI 返回的响应结构（重点）

**finish_reason** 的几种值

| finish_reason | 含义 | 你需要做什么 |
| :-- | :-- | :-- |
| `stop` | AI 回答完了，不需要你帮忙 | 直接把 AI 的 `content` 给用户 |
| `function_call` | AI 想让你帮忙执行一个函数 | 调用真正的函数 |
| `length` | 回答被截断了（内容太长） | 增加 `max_tokens` 或分多次请求 |
| `content_filter` | 内容违规被过滤 | 提醒用户换个问法 |

**情况1：AI想调用函数**

```json
{
  "finish_reason": "function_call",
  "message": {
    "role": "assistant",
    "content": null,
    "function_call": {
      "name": "get_current_weather",
      "arguments": "{\"city\": \"北京\", \"unit\": \"celsius\"}"
    }
  }
}
```

**情况2：直接回答（不需要函数）**

- `finish_reason = "stop"`

---

## 五、你必须做的“三个步骤”代码模板

```python
# 第1步：定义真实函数
def get_current_weather(city, unit="celsius"):
    # mock天气数据
    mock_weather = {
        "北京": "25°C",
        "上海": "28°C"
    }
    return f"{city}天气：{mock_weather.get(city, '未知')}"

# 第2步：ai想要让你帮忙调用function
if response.choices[0].finish_reason == "function_call":
    func_name = response.choices[0].message.function_call.name
    arguments = json.loads(response.choices[0].message.function_call.arguments)

    # 调用真正的函数
    if func_name == "get_current_weather":
        result = get_current_weather(**arguments)

    # 第3步：把函数结果发回给AI
    second_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            # 第1条：用户最初的问题
            {"role": "user", "content": "北京天气如何"},
            # 第2条：AI 说“我需要调用函数”（这就是 response.choices[0].message）
            response.choices[0].message,  # 等同于 {"role": "assistant", "content": None, "function_call": {...}},
            {
                "role": "function",
                "name": func_name,
                "content": result
            }
        ],
        functions=functions  # 依然要传
    )
    # 最终回答
    final_answer = second_response.choices[0].message.content

else
    final_answer = response.choices[0].message.content
```

## 七、重点

- [x] function_call 字段的作用 --> 提供字段让ai决定是否要call function
- [x] finish_reason = "function_call" 的含义 --> 判断是否要继续调用一次ai还是直接返回
- [x] 如何解析 arguments（JSON字符串） --> json插件
- [ ] role = "function" 的消息类型

---

## 八、常见错误 & 避坑

| 错误              | 原因             | 解决                        |
| ----------------- | ---------------- | --------------------------- |
| AI不调用函数      | 参数描述不清晰   | 加强description，给例子     |
| arguments解析失败 | JSON格式错误     | 用 `json.loads()` 包一层try |
| 第二次请求报错    | 没传functions    | 第二次也必须传functions     |
| 多轮对话乱掉      | 没有保存历史消息 | 保留完整的messages数组      |

---

## 九、今天的学习路线（按顺序做）

1. **理解流程**（10分钟）  
   → 反复看“三步骤代码模板”

2. **手写函数描述**（15分钟）  
   → 自己定义3个不同功能的函数（查天气、算时间、翻译）

3. **跑通Mock版**（30分钟）  
   → 用我给你的mock代码，改造成支持多个城市

4. **如果真有API Key**（可选）  
   → 替换成真实OpenAI调用（注意国内网络）

5. **扩展成命令行工具**（30分钟）  
   → 让用户循环输入问题，自动判断是否调用天气函数

---

## 十、进阶一点（今天有余力再看）

- **同时调用多个函数**（parallel function calling）
- **强制调用函数**：`function_call={"name": "xxx"}`
- **函数返回结果太长** → 用向量数据库或摘要
