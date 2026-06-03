import os
import chromadb
import uuid

# 1. 简单的分块工具函数 (模拟 LangChain 的切分逻辑)
def chunk_text(text, chunk_size=100, overlap=20):
    """
    带重叠的文本切分
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        # 下一区块的起点 = 当前区块终点 - 重叠度
        start = end - overlap
        if start >= len(text): break
    return chunks

# 2. 准备一段长文本 (模拟长文档)
LONG_DOC = """
这是关于人工智能历史的长篇文章。1956年，达特茅斯会议标志着 AI 的诞生。
随后在 1970 年代经历了第一个寒冬。到了 1990 年代，深蓝击败国际象棋冠军。
进入 21 世纪，深度学习开始爆发。2022 年 OpenAI 发布了 ChatGPT，震惊全球。
"""

def test_chunking_and_search():
    client = chromadb.Client()
    collection = client.create_collection(name="history_doc")

    # --- 步骤 A: 分块处理 ---
    print(f"📄 原始文档长度: {len(LONG_DOC)}")
    chunks = chunk_text(LONG_DOC, chunk_size=50, overlap=10) # 故意设小点方便演示
    print(f"📦 分块完成，共 {len(chunks)} 块。")

    # --- 步骤 B: 存入向量库，附带 Metadata ---
    ids = [str(uuid.uuid4()) for _ in chunks]
    metadatas = [{"source": "history_article", "page": i} for i in range(len(chunks))]
    
    collection.add(
        documents=chunks,
        ids=ids,
        metadatas=metadatas
    )

    # --- 步骤 C: 带过滤条件的搜索 ---
    user_query = "1956年发生了什么？"
    print(f"\n🔍 搜索问题: {user_query}")
    
    results = collection.query(
        query_texts=[user_query],
        n_results=2,
        # 只搜索来自 history_article 的内容 (元数据过滤)
        where={"source": "history_article"} 
    )

    print("✨ 匹配到的最相关内容分块：")
    for i, doc in enumerate(results['documents'][0]):
        # 注意：Chroma 的距离越小表示越接近
        distance = results['distances'][0][i]
        page = results['metadatas'][0][i]['page']
        print(f" - [Page {page}] (Score: {distance:.4f}): {doc}")

if __name__ == "__main__":
    test_chunking_and_search()


###
#📄 原始文档长度: 159
#📦 分块完成，共 6 块。

#🔍 搜索问题: 1956年发生了什么？
#✨ 匹配到的最相关内容分块：
 #- [Page 0] (Score: 0.2847): 这是关于人工智能历史的长篇文章。1956年，达特茅斯会议标志着 AI 的诞生。

 #- [Page 1] (Score: 0.4152): 诞生。随后在 1970 年代经历了第一个寒冬。到了 1990 年代，深蓝击败国际象棋冠军。
###