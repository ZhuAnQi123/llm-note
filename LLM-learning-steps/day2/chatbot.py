from openai import OpenAI
import sys
import os

# === 强制设置编码（解决阿里云百炼的 ASCII bug）===
os.environ['PYTHONIOENCODING'] = 'utf-8'
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# 初始化客户端
client = OpenAI(
    api_key="sk-59c5b66dbe244feaaa26dabb23c5616b",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

#先写一个回复函数
def chat(messages):
    try:
        response=client.chat.completions.create(
            model='qwen-vl-plus-2025-05-07',
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"发生错误: {e}")
        return "抱歉，发生了错误。"
    


#主函数，负责和用户交互
def main():
    print('欢迎来到Chatbot！')
    print("💡 提示：输入 'quit' 或 'exit' 退出，输入 'clear' 清空对话历史")
    print("-" * 50)

    messages = [
        #system是专门用来设定AI人设的
        {'role': "system", 'content': "你是一个友好且乐于助人的聊天机器人，帮助用户解答问题和提供建议。"}
    ]

    while True:
        user_input=input('\n💁你: ').strip()

        if not user_input:
            continue

        if user_input.lower() in ['quit', 'exit']:
            print("\n👋 再见！")
            break

        if user_input.lower() == 'clear':
            messages = [
                {'role': "system", 'content': "你是一个友好且乐于助人的聊天机器人，帮助用户解答问题和提供建议。"}
            ]
            print("\n🧹 对话历史已清空！")
            continue

        messages.append({"role": "user", "content": user_input})

#flush=True可以强制立即输出，而不是等待缓冲区满了才输出。这在需要实时反馈的场景下非常有用，比如在命令行界面中显示进度或状态信息。
        print("🤖 很好的问题！Chatbot正在思考...",end="",flush=True)

        reply = chat(messages)

        print(reply)

        messages.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    main()




