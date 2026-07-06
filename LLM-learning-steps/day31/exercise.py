import os
from langchain_community.chat_models import ChatDashScope
from langchanin_core.output_parsers import StrOutputParser
from langchanin_core.prompts import ChatPromptTemplate
dashscope.api_key = 'sk-59c5b66dbe244feaaa26dabb23c5616b'

#1.初始化模型
model=ChatDashScope(model_name='qwen-turbo')

#2.定义prompt模版
prompt = ChatPromptTemplate.from_template("你是一个精通{language}的翻译官。请将以下内容翻译成{language}:\n{text}")

#3.定义输出解析器
parser=StrOutputParser()

# 构建LCEL链
chain = prompt|model|parser

# main
if __name__ =="__main__":
result=chain.invoke({
    "language":"德语",
    "text":'大模型技术正在飞速发展'
})

print(f"\n 翻译结果：{result}")