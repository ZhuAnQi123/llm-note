# Step 03：Embedding 入库与向量库 (Day 7)

日期：2026-06-11  
阶段：阶段 3 - 个人知识库 RAG  
目标：用 DashScope Embedding API 把 chunks 向量化，存入 ChromaDB，按 persona 分 collection。

---

## 1. 今天的学习目标

【相关知识点】

- **ChromaDB**：轻量本地向量数据库，支持持久化、collection 隔离、metadata filter。适合个人项目 MVP。
- **Collection vs Metadata Filter**：两种 namespace 隔离方式：
  - **方案 A（推荐）**：`sophie_kb` 和 `naval_kb` 两个 collection
  - **方案 B**：一个 collection，检索时 `where={"persona": "sophie"}`

---

## 2. 今天的实操任务

### 任务 1：安装依赖

在 `server/requirements.txt` 追加：

```text
chromadb>=0.4.0
```

DashScope Embedding 可继续用已有的 `openai` SDK（兼容接口），或直接用 `dashscope` SDK。

`.env` 追加（如尚未配置）：

```env
EMBEDDING_MODEL=text-embedding-v3
CHROMA_PERSIST_DIR=./data/chroma
```

### 任务 2：创建 `server/services/embedding_service.py`

封装 embedding 调用：

```python
# 目标接口
def embed_texts(texts: list[str]) -> list[list[float]]:
    """批量把文本列表转为向量列表"""
```

**提示**：DashScope embedding 接口与 OpenAI 兼容，可复用现有 `client` 实例，model 换为 `text-embedding-v3`。

### 任务 3：创建 `server/rag/ingest.py`

入库 CLI 脚本，逻辑：

```text
遍历 data/documents/{persona}/*.md
  → chunker 切片
  → embedding_service 向量化
  → 写入 ChromaDB collection（sophie_kb / naval_kb）
```

运行方式：

```bash
cd server
python -m rag.ingest
```

**提示**：

- 入库前先 `collection.delete()` 或检查是否已存在，避免重复
- 每个 chunk 的 `id` 可用 `{source}_{chunk_index}` 保证唯一

### 任务 4：创建 `server/services/rag_service.py`（检索函数骨架）

今天只写检索，不接 chat：

```python
def retrieve(query: str, persona: str, top_k: int = 3) -> list[dict]:
    """
    返回格式：
    [
      {"text": "...", "metadata": {"source": "resume.md", "title": "..."}, "score": 0.87},
      ...
    ]
    """
```

---

## 3. 目标架构（本 step 完成后）

```text
server/
  services/
    embedding_service.py   ← 今天新建
    rag_service.py         ← 今天新建（检索骨架）
  rag/
    chunker.py
    ingest.py              ← 今天新建
  data/
    documents/
    chroma/                ← 自动生成，已在 .gitignore
```

---

## 4. 验收方式

1. 运行 `python -m rag.ingest`，终端输出每个 persona 入库的 chunk 数量
2. 在 Python REPL 或临时脚本里调用 `retrieve("你的技术栈是什么", "sophie", top_k=3)`，返回的 chunk 内容与简历相关
3. 调用 `retrieve("什么是特殊知识", "naval", top_k=3)`，返回 Naval 文档内容，**不包含** Sophie 简历内容
4. `server/data/chroma/` 目录已生成且被 gitignore

---

## 5. 常见错误排查

### Embedding API 报错 dimension mismatch

**原因**：入库和检索用了不同的 embedding model。  
**解决**：`.env` 固定一个 model，ingest 和 retrieve 共用。

### ChromaDB 找不到 collection

**原因**：ingest 没跑完，或 `CHROMA_PERSIST_DIR` 路径不一致。  
**解决**：检查 `.env` 路径，确保 ingest 和 rag_service 读同一个目录。

### 检索结果不相关

**原因**：chunk 太大或文档内容太薄。  
**解决**：回到 Step 01/02 优化文档和切片粒度。

---

## 6. 今日学习记录

```md
## 今日复盘

- 今天我亲手实现了：把文档切片转化为向量 & 把搜索文字转化为向量在向量库中查找并返回匹配的前几条
- 今天我卡住了：
- 明天我要继续：Step 04 接入 /api/chat
```
