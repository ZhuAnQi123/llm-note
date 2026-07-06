# 练习内容：用python调用openai接口，生成一段鼓励我的正念早安语句，并打印出来。
from openai import OpenAI
client =OpenAI(
    api_key="sk-59c5b66dbe244feaaa26dabb23c5616b",
     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

def main():
    try:
        response=client.chat.completions.create(
            model='qwen-vl-plus-2025-05-07',
            messages=[
                {
                    "role":"user",
                    "content":'写一段鼓励我的正念早安语句'
                }
            ]
        )
        sentence=response.choices[0].message.content
        print(sentence)
    except Exception as e:
        print(f"发生错误: {e}")
    
#用于区分文件是直接运行还是被导入。
# 当是在本文件中直接被引入的话就会返回__main__，
# 如果是被其他文件引入的话就会返回文件名。
# 被其他文件引入的时候，我们会希望main函数在被调用的时候才执行1，而不是主动执行！
if __name__ == "__main__":
    main()
                