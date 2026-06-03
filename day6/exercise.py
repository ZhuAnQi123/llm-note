# AI 自动：查资料+总结
# ⚠️多函数调用需要 gpt-3.5-turbo-1106 或 gpt-4-1106-preview 及更新版本
# functions 和 function_call 已被 tools 和 tool_choice 取代
# 联网搜索时推荐使用Responses API 而非 Chat Completions API [区别详见](https://developers.openai.com/api/docs/guides/migrate-to-responses#messages-vs-items)

from openai import OpenAI
import json
client=OpenAI()

# 1.定义查资料 & 总结两个工具函数
def search(key:str)->str:
    """模拟联网搜索工具函数，返回搜索结果"""
    # 这里我们直接返回一个固定的搜索结果，实际应用中可以调用搜索引擎API
    return f"搜索得到100条：关于'{key}'的相关信息..."


def summarize(text:str)->str:
    """模拟总结工具函数，返回总结结果"""
    # 这里我们直接返回一个固定的总结结果，实际应用中可以调用文本摘要API
    return f"总结：'{text}'的核心内容是..."

# 2.定义工具列表
tools = [
    {
        'type':'function',
        'function': {
            'name':'search',
            'description':'根据关键词进行联网搜索，返回搜索结果',
            'parameters':{
                'type':'object',
                'properties':{
                    'key':{
                        'type':'string',
                        'description':'搜索关键词'
                    }
                },
            },
            'required':['key'],
            'additionalProperties':False
        }
         "strict": True  # 开启严格模式，保证输出符合schema
    },
    {
        type':'function',
        'function':{
            'name':'summarize',
            'description':'对输入文本进行总结，返回总结结果',
            'parameters':{
                'type':'object',    
                'properties':{
                    'text':{
                        'type':'string',
                        'description':'需要总结的文本'
                    }
                },
                'required':['text'],
                'additionalProperties':False
            }
        }
    }
]

function_mapping={
    'search':search,
    'summarize':summarize
}


# 3.调用模型进行对话，使用工具函数
def main(keyword:str):
    messages=[
        {
            'role':'user',
            'content':f"帮我搜索一下'{keyword}'的资料并且将搜索结果总结一下"
        }
    ]

    response=client.chat.completions.create(
        model='gpt-3.5-turbo-1106',
        messages=messages,
        tools=tools,
        tool_choice='auto'  # 让模型自动选择使用哪个工具
    )


    response_message=response.choices[0].message
    tool_calls=response_message.tool_calls

    if tool_calls:
        for tool_call in tool_calls:
            function_name=tool_call.function.name
            function_to_call=function_mapping.get(function_name)
            function_args=json.loads(tool_call.function.arguments)

            # 真正执行函数
            function_response=function_to_call(**function_args)

            #将执行结果以tool角色加入对话

            messages.append({
                'role':'tool',
                'tool_call_id':tool_call.id,
                'name':function_name,
                'content':function_response
            })

            # 把tools调用结果传给ai
            final_response=client.chat.completions.create(
                model='gpt-3.5-turbo-1106',
                messages=messages
            )

            return final_response.choices[0].message.content
        return response_message.content

# 调用
if __name__=="__main__":
    keyword="人工智能"
    result=main(keyword)
    print(result)

