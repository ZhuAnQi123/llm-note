# Step 02：文档切片 (Chunking) (Day 6)

日期：2026-06-10  
阶段：阶段 3 - 个人知识库 RAG  
目标：把 Markdown 文档切成带 metadata 的小块（chunks），为 Embedding 入库做准备。

---

## 1. 今天的学习目标

【相关知识点】

- **Chunk 大小权衡**：太大 → 噪声多；太小 → 丢失上下文。入门推荐 **300-500 字符**，overlap **50-100 字符**（相邻块重叠，避免句子被切断）。
- **按标题切 vs 固定窗口切**：按 Markdown `##` 标题切（语义边界清晰）+ 超长段落再按窗口切，是 MVP 阶段的最佳实践。

---

## 2. 今天的实操任务

### 任务 1：创建 `server/rag/chunker.py`

实现一个函数，输入文件路径，输出 chunk 列表：

```python
# 目标接口（你自己实现，不要直接复制完整逻辑）
def chunk_markdown_file(file_path: str, persona: str) -> list[dict]:
    """
    返回格式：
    [
      {
        "text": "chunk 正文内容……",
        "metadata": {
          "persona": "sophie",
          "source": "resume.md",
          "title": "工作经历",
          "chunk_index": 0
        }
      },
      ...
    ]
    """
```

**实现提示：**

1. 用 `##` 分割 Markdown 得到 sections
2. 每个 section 的 `title` = 标题文字，`text` = 标题 + 正文
3. 如果 section 超过 500 字符，按固定窗口 + overlap 再切
4. `persona` 从目录名推断（`documents/sophie/` → `"sophie"`）

### 任务 2：创建 `server/rag/__init__.py`

### 任务 3：写一个简单的测试脚本

在 `server/rag/` 下或终端里手动验证：

```python
from rag.chunker import chunk_markdown_file

chunks = chunk_markdown_file("data/documents/sophie/resume.md", persona="sophie")
print(f"Total chunks: {len(chunks)}")
for c in chunks[:3]:
    print(c["metadata"], c["text"][:80], "...")
```

---

## 3. 目标架构（本 step 完成后）

```text
server/
  rag/
    __init__.py
    chunker.py       ← 今天新建
  data/
    documents/
      sophie/
      naval/
```

---

## 4. 验收方式

1. 对 `sophie/resume.md` 运行 chunker，输出 ≥ 3 个 chunk
2. 每个 chunk 的 `metadata` 包含 `persona`, `source`, `title`, `chunk_index`
3. 没有 chunk 超过 600 字符
4. 相邻 chunk 如有 overlap，重叠部分语义连贯（不切断半句话）

---

## 5. 常见错误排查

### chunk 切得太碎

**现象**：一句话一个 chunk，检索时缺乏上下文。  
**解决**：优先按 `##` 标题切，只在超长时才窗口切。

### metadata 缺失 persona

**现象**：后续无法按 Persona 过滤检索。  
**解决**：从文件路径或函数参数强制传入 persona，不要依赖文件名猜测。

---

## 6. 今日学习记录

```md
## 今日复盘

- 今天我理解了：
- 今天我亲手实现了：
- 今天我卡住了：
- 明天我要继续：Step 03 embedding + 向量库
```
