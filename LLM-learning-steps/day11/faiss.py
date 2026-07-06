"""
FAISS 完整示例 - 从零开始理解向量相似度搜索
场景：文档语义搜索系统
"""

import numpy as np
import faiss
import time

# 1.准备一些文档和对应向量
# 注意faiss不储存这些，要自己维护的
documents=[
    "Python 是很好用的编程语言",
    "明天可能会下雨，记得带伞",
    "向量数据库可以用于相似度搜索",
    "推荐系统会根据用户喜好推荐内容",
]

# 模拟生成向量（实际会用 embedding 模型）
# 注意：必须是 float32 类型
def generate_mock_embedding(text, dimension=8):
    """模拟 embedding 模型生成向量"""
    np.random.seed(hash(text) % 10000)
    return np.random.randn(dimension).astype('float32')

# 生成文档向量
vectors=[]
for doc in documents:
    vec=generate_mock_embedding(doc)
    vectors.append(vec)

# 使用np转化为 float32的numpy数组
verctors=np.array(vectors).astype('float32')

print(f"✅ 生成了 {len(vectors)} 个向量")
print(f"   向量维度: {vectors.shape[1]}")
print(f"   数据类型: {vectors.dtype}\n")


# 2.创建FAISS索引【这时候还没有关联添加向量的】
dimension=vectors.shape[1]

# 方式1：使用IndexFlatL2（暴力搜索，适合小数据集）
index=faiss.IndexFlatL2(dimension)
# 方式2：使用IndexIVFFlat（倒排文件，适合大数据集）
index_ip=faiss.IndexFlatIP(dimension)

# 3.添加向量索引
index.add(vectors)

# 4.查询相似向量
query="我想学习编程语言"
query_vector = generate_mock_embedding(query_text).reshape(1, -1)

print(f"查询文本: '{query_text}'")
print(f"查询向量形状: {query_vector.shape}\n")

# 搜索最相似的 k 个向量
k = 3
distances, indices = index_flat.search(query_vector, k)

print(f"搜索 Top-{k} 结果（L2距离，越小越相似）:")
print(f"索引位置: {indices[0]}")
print(f"距离值: {distances[0]}\n")

# 将索引映射回原始文档
print("对应的文档内容:")
for i, idx in enumerate(indices[0]):
    print(f"  {i+1}. [{distances[0][i]:.4f}] {documents[idx]}")

print("\n💡 说明: L2距离越小表示越相似\n")


# ============================================
# 5. 多查询示例：同时搜索多个问题
# ============================================
print("=" * 60)
print("🔍 第五步：批量查询（同时搜索多个问题）")
print("=" * 60)

queries = [
    "怎么做菜",
    "机器学习的知识",
    "明天的天气"
]

# 批量生成查询向量
query_vectors = np.array([generate_mock_embedding(q) for q in queries]).astype('float32')

# 批量搜索
k = 2
distances, indices = index_flat.search(query_vectors, k)

for i, query in enumerate(queries):
    print(f"\n查询: '{query}'")
    print(f"最相似的 {k} 个文档:")
    for j, idx in enumerate(indices[i]):
        print(f"  {j+1}. [{distances[i][j]:.4f}] {documents[idx]}")


# ============================================
# 6. 高级索引：IVF（加速搜索）
# ============================================
print("\n" + "=" * 60)
print("⚡ 第六步：高级索引 - IVF（加速大规模搜索）")
print("=" * 60)

# 当数据量很大时，暴力搜索会变慢
# IVF (Inverted File) 通过聚类来加速

# 创建 IVF 索引的参数
nlist = 2  # 聚类中心数量（通常设为 sqrt(向量数)）
quantizer = faiss.IndexFlatL2(dimension)  # 量化器
index_ivf = faiss.IndexIVFFlat(quantizer, dimension, nlist, faiss.METRIC_L2)

print(f"创建 IVF 索引（加速版）")
print(f"  聚类中心数: {nlist}")
print(f"  需要训练: {not index_ivf.is_trained}")

# IVF 索引需要训练
print("训练索引...")
index_ivf.train(vectors)
print(f"训练完成: {index_ivf.is_trained}")

# 添加向量
index_ivf.add(vectors)
print(f"已添加 {index_ivf.ntotal} 个向量")

# IVF 搜索时需要设置 nprobe（搜索多少个聚类）
index_ivf.nprobe = 1  # 搜索的聚类数，越大越精确但越慢

# 性能对比
print("\n性能对比测试:")
print("-" * 40)

# 测试数据
test_queries = np.random.randn(10, dimension).astype('float32')

# 暴力搜索时间
start = time.time()
for q in test_queries:
    index_flat.search(q.reshape(1, -1), 5)
flat_time = time.time() - start

# IVF 搜索时间
start = time.time()
for q in test_queries:
    index_ivf.search(q.reshape(1, -1), 5)
ivf_time = time.time() - start

print(f"暴力搜索总时间: {flat_time:.4f}秒")
print(f"IVF搜索总时间: {ivf_time:.4f}秒")
print(f"加速比: {flat_time/ivf_time:.2f}x\n")


# ============================================
# 7. 保存和加载索引
# ============================================
print("=" * 60)
print("💾 第七步：保存和加载索引")
print("=" * 60)

# 保存索引到文件
index_file = "my_faiss_index.bin"
faiss.write_index(index_flat, index_file)
print(f"✅ 索引已保存到: {index_file}")

# 从文件加载索引
loaded_index = faiss.read_index(index_file)
print(f"✅ 索引已加载，包含 {loaded_index.ntotal} 个向量")

# 验证加载的索引可用
test_query = generate_mock_embedding("测试").reshape(1, -1)
distances, indices = loaded_index.search(test_query, 2)
print(f"✅ 加载的索引工作正常\n")


# ============================================
# 8. 实用功能：删除和更新
# ============================================
print("=" * 60)
print("🔄 第八步：删除和更新向量")
print("=" * 60)

print("注意: FAISS 不支持直接删除，需要重建索引")

# 方法：创建新索引，只添加需要的向量
# 假设要删除索引 2 的文档（"如何做红烧肉？"）
indices_to_keep = [0, 1, 3, 4, 5, 6, 7]  # 保留的索引
new_vectors = vectors[indices_to_keep]
new_documents = [documents[i] for i in indices_to_keep]

# 创建新索引
new_index = faiss.IndexFlatL2(dimension)
new_index.add(new_vectors)

print(f"原始文档数: {len(documents)}")
print(f"删除后文档数: {len(new_documents)}")
print(f"✅ 新索引已创建，包含 {new_index.ntotal} 个向量\n")


# ============================================
# 9. 实际应用：完整的文档搜索系统
# ============================================
print("=" * 60)
print("🎯 第九步：完整的文档搜索系统示例")
print("=" * 60)

class SimpleVectorSearch:
    """一个简单的向量搜索系统"""
    
    def __init__(self, dimension):
        self.index = None
        self.documents = []
        self.dimension = dimension
    
    def add_documents(self, documents, vectors):
        """添加文档和对应的向量"""
        self.documents = documents
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(vectors)
        print(f"✅ 已添加 {len(documents)} 个文档")
    
    def search(self, query_vector, k=3):
        """搜索最相似的文档"""
        if self.index is None:
            raise ValueError("请先添加文档")
        
        distances, indices = self.index.search(query_vector, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            results.append({
                'score': distances[0][i],  # 距离越小越相似
                'document': self.documents[idx],
                'index': idx
            })
        return results
    
    def save(self, filepath):
        """保存索引"""
        faiss.write_index(self.index, filepath)
        print(f"✅ 索引已保存到: {filepath}")
    
    def load(self, filepath, documents):
        """加载索引"""
        self.index = faiss.read_index(filepath)
        self.documents = documents
        print(f"✅ 已加载索引，包含 {self.index.ntotal} 个文档")

# 使用示例
print("创建搜索系统...")
search_system = SimpleVectorSearch(dimension=8)

# 添加文档
search_system.add_documents(documents, vectors)

# 执行搜索
query = "学习编程语言"
query_vec = generate_mock_embedding(query).reshape(1, -1)
results = search_system.search(query_vec, k=3)

print(f"\n搜索: '{query}'")
print("结果:")
for i, result in enumerate(results, 1):
    print(f"  {i}. [距离: {result['score']:.4f}] {result['document']}")


# ============================================
# 10. 不同距离度量的对比
# ============================================
print("\n" + "=" * 60)
print("📐 第十步：不同距离度量对比")
print("=" * 60)

# 创建不同的索引
index_l2 = faiss.IndexFlatL2(dimension)
index_ip = faiss.IndexFlatIP(dimension)  # 内积

# 添加相同的向量
index_l2.add(vectors)
index_ip.add(vectors)

# 测试查询
test_vec = generate_mock_embedding("Python").reshape(1, -1)

# L2 距离搜索
distances_l2, indices_l2 = index_l2.search(test_vec, 3)

# 内积搜索（需要归一化才能等价于余弦相似度）
distances_ip, indices_ip = index_ip.search(test_vec, 3)

print("L2 距离结果（越小越相似）:")
for i, idx in enumerate(indices_l2[0]):
    print(f"  {i+1}. 距离={distances_l2[0][i]:.4f} - {documents[idx]}")

print("\n内积结果（越大越相似）:")
for i, idx in enumerate(indices_ip[0]):
    print(f"  {i+1}. 内积={distances_ip[0][i]:.4f} - {documents[idx]}")

print("\n💡 提示:")
print("  - L2距离: 欧氏距离，越小越相似")
print("  - 内积: 向量点积，越大越相似")
print("  - 余弦相似度: 需要先归一化向量，再用内积")


# ============================================
# 11. 性能统计
# ============================================
print("\n" + "=" * 60)
print("📊 第十一步：索引统计信息")
print("=" * 60)

print(f"索引类型: {type(index_flat).__name__}")
print(f"向量维度: {index_flat.d}")
print(f"向量总数: {index_flat.ntotal}")
print(f"是否训练: {getattr(index_flat, 'is_trained', True)}")

# 检查向量数据
print(f"\n向量数据统计:")
print(f"  形状: {vectors.shape}")
print(f"  均值: {vectors.mean():.4f}")
print(f"  标准差: {vectors.std():.4f}")
print(f"  最小值: {vectors.min():.4f}")
print(f"  最大值: {vectors.max():.4f}")

print("\n🎉 所有示例运行完成！")


# ============================================
# 补充：清理文件
# ============================================
import os
if os.path.exists("my_faiss_index.bin"):
    os.remove("my_faiss_index.bin")
    print("\n🧹 已清理临时文件")
