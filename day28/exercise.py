# rag 
# 建立向量数据库 --> 用户输入转为向量 --> 在数据库中搜索 --> AI回答

import os
import chromadb
from dashcope import Generation,TextEmbedding
from http import HTTPStatus

dashscope.api_key = 'sk-59c5b66dbe244feaaa26dabb23c5616b'

# qwen embedding函数，把一段文字转为为embeding向量
def get_qwen_embedding(text):
    response = TextEmbedding.call(
        model=TextEmbedding.Models.text_embedding_v2,
        inpu=text
    )

    return response.output['embeddings'][0]['embedding']

# 2.模拟知识库数据（这块通常是从pdf/txt取读）
PRIVATE_KNOWLEDGE = [
    "Cursor 公司成立于 2022 年，总部位于旧金山。",
    "Cursor 的首席执行官是 Michael Truell。",
    "Cursor 的核心产品是基于 AI 的代码编辑器，集成了 Claude 和 GPT 模型。",
    "Cursor 的口号是：让编程更简单。"
]

def main_rag():
    # --- 步骤 A: 准备向量数据库 ---
    client=chromadb.Client() #内存模式
    collection=client.create_collection(name='mock_cursor_wiki')
    print("⏳ 正在为知识库建立索引...")
    # --- 步骤 B: 将模拟知识库插入到向量数据库 ---

    for i,text in enumerate(PRIVATE_KNOWLEDGE):
        # 文字转化为向量储存到chromadb
        vec = get_qwen_embedding(text)
        # 注意collection.add是添加一条数据到collection，
        # 它接受列表的形式。所以要放在[]里
        collection.add(
            embeddings=[vec],
            documents=[text],
            ids=[f'id_{i}']
        )

        print('知识库准备就绪')

    # --- 步骤 C: 用户提问 ,开始检索(Retrieval) ---
    user_query='cursor的公司创始人是谁？总部在哪？'
    query_vec=get_qwen_embedding(user_query)
    search_results=collection.query(
        query_embeddings=[query_vec],
        n_results=2
    )
    context='\n'.join(search_results['documents'][0])
    print(f'检索到的背景：\n{context}')


    # --- 步骤 D: 注入并生成 (Augmentation & Generation) ---
    system_prompt= f"你是一个专业的 Cursor 知识助手。请根据以下资料回答用户问题：\n\n资料内容：\n{context}"

    messages=[
        {'role':'system','content':system_prompt},
        {'role':'user','content':user_query}
    ]

    response=Generation.call(
        model='qwen-turbo',
        messages=messages,
        result_format='message'
    )

    if response.status_code == HTTPStatus.OK:
        print(f"\n🤖 AI 回答: \n{response.output.choices[0]['message']['content']}")
    else:
        print(f"❌ 出错了: {response.message}")

if __name__ == "__main__":
    main_rag()