from openai import OpenAI
import sys
import os

# === 强制设置编码（解决阿里云百炼的 ASCII bug）===
os.environ['PYTHONIOENCODING'] = 'utf-8'
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# 今日计划
# 写一个AI 情感咨询师
# 理解：`temperature``max_tokens`
# 比较不同参数效果
# 写一个AI 面试官

# 初始化客户端，传baseurl，apikey给openai
client=OpenAI(
    api_key="sk-59c5b66dbe244feaaa26dabb23c5616b",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 写情感咨询师函数 client.chat.completions.creat 
# 最终返回 response.choices[0].message.content

def ai_emotional_counselor(user_input):
    response=client.chat.completions.create(
        model='qwen-vl-plus-2025-05-07',
        messages=[
            {"role": "system", "content": (
                "你是一个温暖且富有同理心的资深情感咨询师，帮助用户倾诉和提供情感支持。"
                "你不会批判来犯者，而是帮助他们探索内你真正的需求，梳理好情绪"
                "你擅长倾听共情，并会提供心理视角的专业建议"
                "你的回答应该温和治愈，并适当提出反思性问题"
                "而不是直接给命令式解决方案。"
                "始终以促进来访者的情感成长和自我理解为目标。"
             )},
            {"role": "user", "content": user_input}
        ],
        temperature=0.8,
        max_tokens=200
    )

    return response.choices[0].message.content


# 对话循环

if __name__ =="__main__":
    print('我是你的资讯老师志伟老师，有什么和老公难以解决的问题，都可以跟我说～')
    while True:
        user_input = input("👩：")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("👩：谢谢你，志伟老师，再见！")
            break
        reply=ai_emotional_counselor(user_input)
        print(f"\n志伟老师：{reply}")




