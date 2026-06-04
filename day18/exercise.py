
# 例子：專業代碼評審機器人
這是一個能夠記住上下文，並以專業架構師身份審核代碼的 CLI 工具。
import os
from dashscope import Generation
from http import HTTPStatus

def get_ai_response(messages):
    """
    Call Qwen API to get the response.
    """
    response = Generation.call(
        model="qwen-max", # Using Qwen-Max for high quality
        messages=messages,
        result_format='message', # Required to get standard message format
    )
    
    if response.status_code == HTTPStatus.OK:
        return response.output.choices[0]['message']
    else:
        print(f"Error: {response.code} - {response.message}")
    return None


def main():
    # 1. Initialize System Prompt
    #在这里定义他的身份比在userprompt更有效！！
    # 写 1.身份 2.目標 3.風格和语言 4.規則
    system_prompt=(
        '你是一个高级的python架构师，你的任务是做代码审查',
        'provided by the user. Focus on: readability, performance, and PEP 8 standards.',
        '你永远用简体中文来回答，但是技术条款使用英文'
    )

    chat_history=[
        {"role":system,'content':'system_prompt'}
    ]

    while True:
        user_input=input('\n 你：')

        if user_input.lower() in ['exit','quit','退出']:
            break;
        
        chat_history.append({"role": "user", "content": user_input})

        print("Thinking...")

        # 當 chat_history 超過 6 條時，自動刪除最早的兩條（保留 System Prompt 不動）。
        if len(chat_history) > 6:
            system_prompt=chat_history[0]
            others=chat_history[1:]
            chat_history=[
                system_prompt,
                *others[2:]
            ]

        # 注意这里把整个chat_history传给AI，而不是只传user_input
        # API 返回的ai_message 已经包含 role 字段
        ai_message=get_ai_response(chat_history)

        if ai_message:
            print(f"\n AI 評審: \n{ai_message['content']}")
            chat_history.append(ai_message)

if __name__ == "__main__":
    main()
