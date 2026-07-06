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

class TextProcessor:
    def __init__(self):
        #添加基础指令块，永远适用
        self.base_prompt="""
        <output_contract>
            - 只输出处理后的结果，不要添加任何解释
            - 不要加"好的，这是改写后的内容"这类开场白
        </output_contract>

        <verbosity_controls>
            - 保持简洁，不重复用户原文
            - 直接输出结果
        </verbosity_controls>
        """
        

    def rewirte(self,text:str,style:str='更专业')->str:
        """改写文本"""
        prompt=f"""
        {self.base_prompt}
        任务：改写下面文本，风格要求：{style}
        文本：{text}
        改写后的文本：
        """
        response=client.chat.completions.create(
            model='qwen-vl-plus-2025-05-07',
            #chatgpt使用的是input参数，而qwen使用的是messages参数，且需要指定role为user
            messages=[{'role':'user', 'content':   prompt}],
            reasoning_effort='low'
        )

        return response.choices[0].message.content.strip()
    
    def translate(self,text:str,target_language:str='英文')->str:
        """翻译文本"""
        prompt=f"""
        {self.base_prompt}
        任务：将下面文本翻译为{target_language}
        <grpunding_rules>
        - 保持原意的准确性
        - 专有名词保持原样不翻译
        </grpunding_rules>
        文本：{text}
        翻译后的文本:
        """

        response=client.chat.completions.create(
            model='qwen-vl-plus-2025-05-07',
            messages=[{'role':'user', 'content':   prompt}],
            reasoning_effort='low'
        )

        return response.choices[0].message.content.strip()
    
    def summarize(self,text:str,max_length:int=100)->str:
        """总结文本"""
        prompt=f"""
        {self.base_prompt}
        <verbosity_controls>
        - 总结不超过{max_length}字
        </verbosity_controls>
        任务：总结下面文本,保留核心信息
        文本:{text}
        总结:
        """

        response=client.chat.completions.create(
            model='qwen-vl-plus-2025-05-07',
            messages=[{'role':'user', 'content':   prompt}],
            reasoning_effort='low'
        )

        return response.choices[0].message.content.strip()
    

processor=TextProcessor()

orginal_text="""
人工智能技术的发展速度非常快，尤其是在自然语言处理领域。
GPT系列模型的出现彻底改变了人们与机器交互的方式。
从GPT-1到GPT-5，模型能力有了质的飞跃，能够完成各种复杂的任务。
"""

print('='*20)
print('[原文]'+orginal_text)
print('\n'+'='*20)
print('[改写]更简洁的风格')
rewiten_text=processor.rewirte(orginal_text,style="更简洁")
print(rewiten_text)
print('\n'+'='*20)
print('[改写]改写为更专业的风格')
print(processor.rewirte(orginal_text,style="更专业"))
print('\n'+'='*20)
print('[翻译]翻译为英文')
print(processor.translate(orginal_text,target_language="英文"))
print('\n'+'='*20)
print('[总结]总结为不超过50字')
print(processor.summarize(orginal_text,max_length=50))
