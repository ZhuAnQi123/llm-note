from openai import OpenAI
import sys
import os

# === 强制设置编码（解决阿里云百炼的 ASCII bug）===
os.environ['PYTHONIOENCODING'] = 'utf-8'
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# 今日计划
# 写一个AI 面试官
# 理解：`temperature``max_tokens`
# 比较不同参数效果

# 初始化客户端，传baseurl，apikey给openai
client=OpenAI(
    api_key="sk-59c5b66dbe244feaaa26dabb23c5616b",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 写面试函数 client.chat.completions.creat 

def ai_interviewer(user_input):
    response=client.chat.completions.create(
        model:'qwen-vl-plus-2025-05-07',
        messages=[
            {role:"system", content:(
                "你是一个专业且严格的面试官，负责面试一位应聘者，职位是LMM工程师。"
                "你会根据用户的回答，提出有针对性的技术问题。"
                "你会根据用户的回答，评估他们的技术能力和问题解决能力，并提供建设性的反馈。"
                "你的回答应该直接且专业，帮助用户了解他们在面试中的表现，并指出他们的优点和需要改进的地方。"
            )},
            {role:"user", content:user_input}
        ],
        temperature=0.5,
        max_tokens=300
    )


    return response.choices[0].message.content

if __name__ =="__main__":
    print('欢迎来到LMM工程师面试，请准备好回答我的问题。')
while True:
    user_input = input("👩：")
    if user_input.lower() in ['exit', 'quit', 'bye']:
        print("👩：谢谢你，面试官，再见！")
        break
    reply=ai_interviewer(user_input)
    print(f"\n面试官：{reply}")

