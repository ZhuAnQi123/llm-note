# [Embedding](https://platform.openai.com/docs/guides/embeddings?utm_source=chatgpt.com)

## 📋 今日学习目标

**核心目标**：理解Embeddings是什么，能做什么，并且**亲手生成第一个向量**。

### 具体目标清单

| 目标 | 验收标准 | 预计时间 |
|------|---------|---------|
| 1. 理解什么是Embedding | 能用自己的话说清楚 | 15分钟 |
| 2. 生成第一个Embedding | 代码跑通，看到1536个数字 | 20分钟 |
| 3. 理解相似度计算 | 能比较两句话的相似度 | 20分钟 |
| 4. 做一个简单的语义搜索 | 从3句话中找到最相关的一句 | 30分钟 |
| 5. 理解实际应用场景 | 能说出3个应用场景 | 15分钟 |

**总预计时间**：1.5-2小时

---

## 📚 学习资料（按顺序阅读）

### 第一部分：理解概念（15分钟）

**什么是Embedding？**

想象您要把"苹果很好吃"这句话变成计算机能计算的数字：

```python
# 人看：苹果很好吃 → 计算机看：[0.23, -0.45, 0.67, ..., 0.12]（1536个数字）
```

**核心思想**：
- 把文字变成**数字列表**（向量）
- 语义相似的文字，向量也相似
- 向量之间的距离代表语义的差异

**类比理解**：
```
"苹果很好吃" → [0.1, 0.8, 0.3, ...]
"水果很美味" → [0.12, 0.79, 0.31, ...]  # 向量相近
"今天下雨了" → [-0.5, 0.2, -0.7, ...]    # 向量差异大
```

### 第二部分：动手实践（50分钟）

#### 任务1：生成第一个Embedding（20分钟）

```python
# 文件：01_first_embedding.py
from openai import OpenAI
import os

# 设置API Key
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 生成embedding
response = client.embeddings.create(
    # 注意，必须用embedding模型，不能用GPT对话模型。
    model="text-embedding-3-small",
    input="苹果很好吃"
)

# 提取向量
embedding = response.data[0].embedding

print(f"向量的长度：{len(embedding)}")  # 应该是1536
print(f"前10个数字：{embedding[:10]}")
print(f"向量的类型：{type(embedding)}")
```

**运行后您会看到**：
```
向量的长度：1536
前10个数字：[-0.006929283495992422, -0.005336422007530928, ...]
```

**理解要点**：
- 1536个数字，每个都在-1到1之间
- 这些数字编码了"苹果很好吃"的语义

#### 任务2：理解相似度（20分钟）

```python
# 文件：02_similarity.py
from openai import OpenAI
import numpy as np

client = OpenAI()

def get_embedding(text):
    """获取文本的embedding"""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def cosine_similarity(a, b):
    """计算两个向量的余弦相似度（越接近1越相似）"""
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# 三个句子
sentences = [
    "苹果很好吃",
    "水果很美味", 
    "今天天气真糟糕"
]

# 获取embeddings
embeddings = [get_embedding(s) for s in sentences]

# 比较相似度
sim_1_2 = cosine_similarity(embeddings[0], embeddings[1])
sim_1_3 = cosine_similarity(embeddings[0], embeddings[2])

print(f"『{sentences[0]}』和『{sentences[1]}』的相似度：{sim_1_2:.4f}")
print(f"『{sentences[0]}』和『{sentences[2]}』的相似度：{sim_1_3:.4f}")
```

**预期输出**：
```
『苹果很好吃』和『水果很美味』的相似度：0.8945  # 高相似度
『苹果很好吃』和『今天天气真糟糕』的相似度：0.1234  # 低相似度
```

#### 任务3：做一个语义搜索（30分钟）

这是Embeddings最实用的应用！

```python
# 文件：03_semantic_search.py
from openai import OpenAI
import numpy as np

client = OpenAI()

def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# 知识库：一堆文档
knowledge_base = [
    "Python是一种编程语言，由Guido van Rossum创建",
    "李白是唐代著名诗人，被称为诗仙",
    "咖啡因是一种中枢神经兴奋剂，存在于咖啡和茶中",
    "长城是中国古代军事防御工程，总长超过2万公里",
    "量子计算利用量子力学原理进行计算"
]

# 预计算所有文档的embeddings（实际应用中会保存下来）
doc_embeddings = [get_embedding(doc) for doc in knowledge_base]

def search(query, top_k=3):
    """搜索最相关的文档"""
    # 获取查询的embedding
    query_embedding = get_embedding(query)
    
    # 计算与所有文档的相似度
    similarities = [
        cosine_similarity(query_embedding, doc_emb)
        for doc_emb in doc_embeddings
    ]
    
    # 获取最相似的top_k个
    indices = np.argsort(similarities)[::-1][:top_k]
    
    print(f"\n查询：『{query}』")
    print(f"最相关的{top_k}个文档：")
    for idx in indices:
        print(f"  - {knowledge_base[idx]} (相似度: {similarities[idx]:.4f})")

# 测试搜索
search("哪种饮料能提神？")
search("中国古代有哪些伟大建筑？")
search("谁被称为诗仙？")

```

**运行效果**：
```
查询：『哪种饮料能提神？』
最相关的3个文档：
  - 咖啡因是一种中枢神经兴奋剂，存在于咖啡和茶中 (相似度: 0.8234)
  - Python是一种编程语言... (相似度: 0.1234)
  - 李白是唐代著名诗人... (相似度: 0.0891)
```

### 第三部分：理解应用场景（15分钟）

您刚才已经实现了一个核心应用：**语义搜索**。以下是其他主要应用：

| 应用 | 原理 | 您能做什么 |
|------|------|-----------|
| **语义搜索** | 查询与文档的向量相似度 | 智能客服、文档检索 |
| **推荐系统** | 用户向量与物品向量的相似度 | 推荐相似商品、文章 |
| **聚类** | 相似文本自动分组 | 新闻分类、用户分群 |
| **异常检测** | 找偏离群体的文本 | 垃圾评论检测 |
| **零样本分类** | 比较文本与类别描述 | 无需训练的文本分类 |

---

## ✅ 今日任务清单

完成以下任务，打勾确认：

### 必做任务
- [ ] 成功运行`01_first_embedding.py`，看到1536个数字
- [ ] 成功运行`02_similarity.py`，理解相似度计算
- [ ] 成功运行`03_semantic_search.py`，能搜索到正确文档
- [ ] 修改`03_semantic_search.py`，加入您自己的5个文档，测试搜索

### 理解检查（能回答出来）
- [ ] Embedding是什么？（用自己的话说）
- [ ] 为什么1536个数字能代表文字的意思？
- [ ] 余弦相似度有什么用？
- [ ] 语义搜索和关键词搜索有什么区别？

### 可选挑战
- [ ] 把知识库保存到JSON文件，实现持久化
- [ ] 添加一个简单的命令行交互界面

---

## 📝 今日总结模板

完成学习后，填写这个总结：

```markdown
## 2024-XX-XX Embeddings学习总结

### 核心概念（用自己的话）
- Embedding本质是：_________________
- 1536这个数字代表：_________________
- 余弦相似度的作用：_________________

### 今天实现了什么
- [ ] 生成了第一个embedding向量
- [ ] 计算了两个句子的相似度
- [ ] 做了一个简单的语义搜索引擎

### 最大的收获
1. _________________
2. _________________

### 遇到的困难及解决
- 困难：_________________
- 解决：_________________

### 明天的学习计划
- [ ] 学习如何使用向量数据库（Chroma/FAISS）
- [ ] 或者：学习如何做RAG（检索增强生成）

### 代码保存位置
- `~/code/embeddings/01_first_embedding.py`
- `~/code/embeddings/02_similarity.py`
- `~/code/embeddings/03_semantic_search.py`
```

---

## 💡 常见问题速查

**Q: 为什么要用cosine similarity而不是欧氏距离？**
A: 对于归一化的向量（OpenAI的embedding就是），两者结果一样。cosine只关心方向不关心长度，更适合文本相似度。

**Q: 每次搜索都要重新计算所有相似度，太慢了怎么办？**
A: 生产环境会用向量数据库（Chroma、FAISS、Pinecone等），它们做了索引优化。

**Q: token数怎么算？**
A: 中文一般1个字符≈1-2个token。用tiktoken库精确计算。

**Q: 什么时候用text-embedding-3-small vs large？**
A: small更快更便宜，large更准。先试small，不够再用large。

---

## 🎯 成功标准

今天学习成功的标志：
1. ✅ 您写的代码都能跑通
2. ✅ 您能解释为什么"苹果很好吃"和"水果很美味"的向量很接近
3. ✅ 您能用embedding实现一个简单的"找相似句子"功能

如果都完成了，恭喜您已经掌握了Embeddings的核心！

**记住**：今天的目标是"理解并会用"，不是"精通所有细节"。明天我们会在此基础上学习如何存储和检索大量向量。