# Day 33：LlamaIndex 入门 - 更简单、更专业的 RAG 框架

## 🎯 学习目标
*   理解什么是 **LlamaIndex (原 GPT Index)**：为什么它比 LangChain 更适合做知识库 (RAG)？
*   掌握 LlamaIndex 的核心：**Data Connectors (Loaders)**、**Indices** 和 **Query Engines**。
*   学会一行代码加载本地 PDF/TXT 并建立索引。
*   理解 **Node**、**Document** 和 **Vector Store Index** 的关系。

---

## 📚 学习资源
*   **LlamaIndex 官方文档 (必读)**: [LlamaIndex Getting Started](https://docs.llamaindex.ai/en/stable/getting_started/concepts/)
*   **LlamaHub (Loader 市场)**: [LlamaHub.ai](https://llamahub.ai/) (各种各样的 Loaders，如 PDF, Google Drive, Slack 等)
*   **LlamaIndex Examples**: [GitHub Examples](https://github.com/run-llama/llama_index/tree/main/examples)

---

## 🛠️ 新手必会知识点 (附例子)

### 1. 为什么用 LlamaIndex？
*   **LangChain**: 像“乐高积木”，你可以搭任何东西。
*   **LlamaIndex**: 像“高级电饭煲”，专攻数据索引和检索。
*   **对比**: Day 28 手写的 50 行 RAG 代码，在 LlamaIndex 只需要 3-5 行。

### 2. 核心三步走 (The Basic Flow)
1.  **Load**: 把数据加载进来 (`SimpleDirectoryReader`)。
2.  **Index**: 把数据变成向量索引 (`VectorStoreIndex`)。
3.  **Query**: 对索引进行提问 (`query_engine`)。

---

## 🧠 逻辑架构说明 (Mermaid 图示)

```mermaid
graph TD
    A[Data Source: PDF/TXT/Web] --> B[Data Connectors/Loaders]
    B --> C[Documents]
    C --> D[Nodes (Chunking)]
    D --> E[VectorStoreIndex (Embedding)]
    E --> F[Query Engine]
    G[User Query] --> F
    F --> H[Final Response]
```

---

## 💻 完整可运行范例：三行代码实现本地 PDF 问答
在使用 LlamaIndex 时，它默认使用 OpenAI。我们要将其配置为 Qwen。

```python
# 安装：pip install llama-index llama-index-llms-dashscope llama-index-embeddings-dashscope
import os
from llama_index.llms.dashscope import DashScope
from llama_index.embeddings.dashscope import DashScopeEmbedding
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings

# 1. 全局配置 (Settings) - 换成通义千问 Qwen
Settings.llm = DashScope(model_name="qwen-turbo")
Settings.embed_model = DashScopeEmbedding(model_name="text-embedding-v2")

def quick_start_rag():
    # 2. 加载当前文件夹下的 'data' 目录 (请确保你创建了一个 data 文件夹并放了 txt)
    if not os.path.exists("./data"):
        os.makedirs("./data")
        with open("./data/test.txt", "w") as f:
            f.write("Cursor 是一款由 Anysphere 公司开发的 AI 代码编辑器。")

    print("⏳ 正在读取文档并建立索引...")
    documents = SimpleDirectoryReader("./data").load_data()
    
    # 3. 核心：建立向量索引 (自动处理分块、Embedding、存库)
    index = VectorStoreIndex.from_documents(documents)
    
    # 4. 创建查询引擎
    query_engine = index.as_query_engine()
    
    # 5. 提问
    response = query_engine.query("Cursor 是谁开发的？")
    print(f"\n🤖 AI 回答: \n{response}")

if __name__ == "__main__":
    quick_start_rag()
```

---

## 💡 老师的建议 (必看)
1.  **LlamaIndex 的强项**：它对各种数据源的支持非常完善。你可以通过 `SimpleDirectoryReader` 轻松读取 PDF, Word, Excel, PPT 甚至本地的 Markdown。
2.  **默认值坑点**：LlamaIndex 默认会消耗 OpenAI API。所以一定要像上面代码那样配置 `Settings.llm` 和 `Settings.embed_model` 为 Qwen。
3.  **从原理中来**：虽然框架很方便，但请回想起 Day 29 学的 **Chunking**。在 LlamaIndex 中，你可以通过 `node_parser` 来精细调整分块大小，这和 Day 29 的原理是一模一样的。

---

## 📝 本日练习
1.  创建一个 `./data` 文件夹，并放入一个你喜欢的 `.pdf` 文件（如公司手册或学习资料），运行上面的代码看它能否回答。
2.  **思考题**：如果我有 100 万份文档，`VectorStoreIndex.from_documents` 会产生大量的 Embedding 费用，且内存可能存不下，我该怎么办？（提示：查找 **Storage Context** 与 **ChromaDB** 的集成用法）。
3.  挑战：尝试在 `query_engine.query()` 中加入不同的 Prompt 模板（提示：查找 `text_qa_template`）。
    