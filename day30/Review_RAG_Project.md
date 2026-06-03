# Day 30：复习日 - 手动搭建一个本地知识库问答 (本地知识库核心复盘)

## 🎯 学习目标
*   复习 Day 26-29 的核心逻辑：Embedding -> Vector DB -> Chunking -> RAG。
*   通过一个小项目，综合运用所有学到的库：`dashscope` (Qwen API), `chromadb`, `numpy`, `uuid`。
*   掌握完整的“本地知识库问答” (Local Knowledge Q&A) 的代码架。
*   学会如何调试和优化 RAG 流程。

---

## 📚 学习资源
*   **RAG 最佳实践**: [OpenAI: Best Practices for Retrieval-Augmented Generation](https://help.openai.com/en/articles/8868588-how-to-improve-rag-performance)
*   **通义千问 API 文档**: [DashScope SDK 快速入门](https://help.aliyun.com/zh/dashscope/developer-reference/quick-start)

---

## 🛠️ 新手必会知识点 (附例子)

### 1. 为什么我们要“手工”搭建一次 RAG？
*   **LangChain / LlamaIndex**：这些框架太重，新手容易被“傻瓜式”函数蒙蔽双眼，不知道底层在发生什么。
*   **手工搭建**：你会清楚地知道：
    *   什么时候调了 Embedding 接口。
    *   向量是怎么存进 ChromaDB 的。
    *   Prompt 是怎么被拼起来的。
    *   AI 什么时候在“一本正经胡说八道”。

---

## 🧠 逻辑架构说明 (Mermaid 图示)

```mermaid
graph TD
    A[PDF/TXT 内容] --> B[分块 (Chunking)]
    B --> C[Qwen Embedding]
    C --> D[存入 ChromaDB]
    E[用户提问] --> F[Qwen Embedding]
    F --> G[向量检索 Top-3]
    G --> H[获取关联文本 Context]
    H --> I[构造高级 Prompt]
    I --> J[Qwen Chat API]
    J --> K[最终回答]
```

---

## 💻 完整可运行范例：Cursor 官方文档智能助手 (综合复刻)
这是一个完整的、可运行的、带错误处理的 RAG 核心代码框架。

```python
import os
import chromadb
import uuid
from dashscope import Generation, TextEmbedding
from http import HTTPStatus

# --- 配置区 ---
# 请确保环境变量 DASHSCOPE_API_KEY 已设置

# --- 工具函数区 ---
def get_embedding(text):
    """获取 Qwen 向量"""
    response = TextEmbedding.call(
        model=TextEmbedding.Models.text_embedding_v2,
        input=text
    )
    if response.status_code == HTTPStatus.OK:
        return response.output['embeddings'][0]['embedding']
    else:
        raise Exception(f"Embedding API Error: {response.message}")

def split_text(text, chunk_size=300):
    """简单的按长度切分，不带 Overlap (复习用)"""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# --- 核心流程区 ---
class KnowledgeBaseAssistant:
    def __init__(self, collection_name="local_kb"):
        # 1. 初始化本地持久化数据库
        self.client = chromadb.PersistentClient(path="./my_kb_storage")
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def ingest_data(self, raw_text):
        """将原始文本存入向量库"""
        print("⏳ 正在处理文档内容...")
        chunks = split_text(raw_text)
        
        for chunk in chunks:
            vec = get_embedding(chunk)
            self.collection.add(
                embeddings=[vec],
                documents=[chunk],
                ids=[str(uuid.uuid4())]
            )
        print(f"✅ 存入完成，共 {len(chunks)} 个分块。")

    def ask(self, query):
        """用户提问，返回回答"""
        # A. 检索
        query_vec = get_embedding(query)
        results = self.collection.query(
            query_embeddings=[query_vec],
            n_results=3
        )
        context = "\n".join(results['documents'][0])
        
        # B. 构造 Prompt
        prompt = f"""你是一个专业的 AI 知识助手。
        请根据以下参考内容回答用户问题。如果内容里没有提到相关信息，请回答“在目前的知识库中没找到相关说明”。

        【参考内容】：
        {context}

        【用户问题】：
        {query}
        """
        
        # C. 调用对话接口
        response = Generation.call(
            model="qwen-turbo",
            messages=[{'role': 'user', 'content': prompt}],
            result_format='message'
        )
        
        if response.status_code == HTTPStatus.OK:
            return response.output.choices[0]['message']['content']
        else:
            return f"❌ 对话 API 错误: {response.message}"

# --- 运行测试 ---
if __name__ == "__main__":
    # 模拟一段“Cursor 使用手册”的内容
    CURSOR_GUIDE = """
    Cursor 是一款强大的 AI 编辑器。它支持快捷键 Cmd+K 进行代码修改，Cmd+L 进行对话。
    Cursor 可以自动索引你的整个代码库，从而提供精准的代码建议。
    目前 Cursor 已经支持 GPT-4o、Claude 3.5 Sonnet 等多个顶级模型。
    你可以在设置中通过开启 'Composer' 模式来进行多文件协作开发。
    """

    kb = KnowledgeBaseAssistant()
    
    # 第一次运行需要 ingest 存入数据，后续可以注释掉
    kb.ingest_data(CURSOR_GUIDE)

    # 开始提问
    questions = [
        "Cursor 怎么修改代码？",
        "Composer 模式是干什么的？",
        "Cursor 的总部在哪？" # 这条文档里没写
    ]

    for q in questions:
        print(f"\n👤 问: {q}")
        ans = kb.ask(q)
        print(f"🤖 答: {ans}")
```

---

## 💡 老师的建议 (必看)
1.  **分块策略 (Chunking)**：在 Day 29 我们学了高级分块，但在 Day 30 的复习里我们用了简单的切分。在真实项目中，请务必使用**带重叠 (Overlap)** 的切分方法。
2.  **数据去重**：上面的代码每次运行 `ingest_data` 都会往数据库里塞重复内容。在实际开发中，需要先根据文件名或 ID 检查是否已经存过。
3.  **调试技巧**：如果 AI 答错了，请先通过 `print(context)` 查看检索环节是否出了问题。**RAG 的核心就在于检索质量**。

---

## 📝 本日练习
1.  运行上面的完整代码。
2.  修改 `KnowledgeBaseAssistant` 类，增加一个 `clear_all()` 函数，清空整个集合 (Collection)。
3.  **挑战**：尝试将 `ingest_data` 里的循环改为 **批处理 (Batch Add)**。一次性提交所有向量，提高效率（提示：ChromaDB 的 `add` 函数支持传入向量列表）。
    