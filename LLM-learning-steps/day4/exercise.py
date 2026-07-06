import json
import openai

client=openai.OpenAI(
    api_key='',
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1" 
)


def get_current_weather(city):
    mock_db_data={"深圳": "30°C 晴", "北京": "18°C 多云"}
    return mock_db_data.get(city,'天气数据位置')


user_input = input("请输入问题：")
messages = [{"role": "user", "content": user_input}]

# 定义工具
tools=[
    {
        'type':'function',
        'function':{
            'name':'get_current_weather',
            'description':'获取天气',
            'parameters':{
                "city": {"type": "string", "description": "城市名"}
            },
            'required':['city']
        }
    }
]


# 首次调用
response=client.chat.completions.create(
    model='qwen-plus',
    messages=messages,
    tools=tools,
    # 千问用 tool_choice，OpenAI 用 function_call
    tool_choice='auto',
    result_format='message'
)

# 获取ai返回的函数嗲用 append到messages 里
assistant_msg = response.output.choices[0].message

# 如果调用了tools函数的话要再问一次
if assistant_msg.get('tool_calls'):
    messages.append(assistant_msg)

    # 原本数据是string的，要处理成为json的给函数调用
    args=json.loads(assistant_msg['tool_calls'][0]['function']['arguments'])
    result=get_current_weather(**args)
    
    #把函数结果添加到messages之后第二次问ai
    messages.append({
        'role': 'tool',
        'tool_call_id': assistant_msg['tool_calls'][0]['id'],
        'content': result
    })

    final_response=client.chat.completions.create(
        model='qwen-plus',
        messages=messages,
        tools=tools,
        tool_choice='auto',
        result_format='message'
    )

    ## 输出最终答案
    print(final_response.output.choices[0].message['content'])

else:
    print(assistant_msg['content'])  # 直接输出