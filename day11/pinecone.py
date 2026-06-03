"""
Pinecone 完整示例 - 一个简单的文档问答系统
场景：搜索公司内部的 FAQ 文档
"""



from pinecone import Pinecone, ServerlessSpec
import numpy as np
from typing import List, Dict
import time
import os


PINECONE_API_KEY = 'pcsk_4KSEvS_BeXgFWgmPThzaVTias1auv3sBvsuMXb553mBN9kPppUR9YybPZtdAVMeXJw5cmW'
INDEX_NAME = 'excercise'
CLOUD = "aws"  
REGION = "us-east-1" 


# 模拟一个embedding函数(这里我们mock的dimension是8)
def get_mock_embedding(text:str,dimension:int=8) -> List[float]:
    """
    这是一个模拟的 embedding 函数
    实际使用时应该用：openai.Embedding.create() 或 sentence-transformers
    """
    np.random.seed(hash(text) % 1000)  # 保持同一文本的embedding一致
    return np.random.rand(dimension).tolist()

# 初始化pinecone
pc=Pinecone(api_key=PINECONE_API_KEY)

# 4. 创建索引[pc.create_index语法]
existing_indexes = [index.name for index in pc.list_indexes()]
print(f"当前的索引列表：{existing_indexes}\n")

if INDEX_NAME not in existing_indexes:
    print(f"索引 '{INDEX_NAME}' 不存在，正在创建...")
    pc.create_index(
        name=INDEX_NAME,
        dimension=8,
        metric='cosine',
        spec=ServerlessSpec(
            cloud=CLOUD,
            region=REGION
        )
    )

    print("⏳ 等待索引初始化...")
    
    while True:
       index_description = pc.describe_index(INDEX_NAME)
       if index_description.status['ready']:
           print("✅ 索引已准备好！\n")
           break
       else:
           print("⏳ 索引正在初始化中...")
           time.sleep(2)

index=pc.Index(INDEX_NAME)
print(f"🔗 已连接到索引: {INDEX_NAME}\n")

# 准备一些数据，假设为公司的已有数据
faq_documents=[
    {
        "id": "faq-001",
        "text": "如何申请年假？员工需要提前3天在OA系统提交申请，经部门主管审批后生效。",
        "category": "hr",
        "author": "hr_dept",
        "priority": 1
    },
    # ...
]

# 生成向量并插入到Pinecone:[index.upsert语法]
vectors_to_upsert = []
for doc in faq_documents:
    # 生成向量
    vector = get_mock_embedding(doc["text"])
    
    # 准备 metadata
    metadata = {
        "text": doc["text"],
        "category": doc["category"],
        "author": doc["author"],
        "priority": doc["priority"]
    }
    
    vectors_to_upsert.append((doc["id"], vector, metadata))

# 批量插入（新版 API 保持相同）
index.upsert(vectors=vectors_to_upsert, namespace="company_faq")
print(f"✅ 成功插入 {len(vectors_to_upsert)} 个文档\n")


# 查看统计信息[ index.describe_index_stat语法]
stats = index.describe_index_stats()
print(f"📊 当前索引统计: {stats['total_vector_count']} 个向量\n")


# 相似度查询 [index.query语法]并且使用filter查询特定条件
query_text = "我想请假，应该怎么做？"
query_vector = get_mock_embedding(query_text)
results=index.query(
    vector=query_vector,
    top_k=3,
    filter={"category": {"$eq": "hr"}},  # 只返回 category = "hr" 的文档
    include_metadata=True,
    namespace="company_faq"
)
print("🔍 查询结果:")
# enumerate是 Python 内置函数，用于同时获取索引和值：
for i, match in enumerate(results['matches'], start=1):
    # .3f 表示保留三位小数，metadata['text'][:50] 表示只显示文本的前50个字符
    print(f"  {i}. [相似度: {match['score']:.3f}] {match['metadata']['text'][:50]}...")


# 更新和删除操作 index.upsert  index.delete 语法
updated_vector=get_mock_embedding("如何申请年假？员工需要提前5天在OA系统提交申请，经部门主管审批后生效。")
index.upsert(
    vectors=[("faq-001", updated_vector, {"text": "更新后的年假申请流程", "category": "hr", "updated": True})],
    namespace="company_faq"
)
print("\n✅ 已更新 faq-001 的内容\n")

index.delete(ids=["faq-001"], namespace="company_faq")


# Namespace 示例：多租户隔离
