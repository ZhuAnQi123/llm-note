# Step 06：RAG 评估与防幻觉 (Day 10)

日期：2026-06-14  
阶段：阶段 3 - 个人知识库 RAG  
目标：用 10 个典型问题系统测试 RAG 质量，记录命中率，优化 prompt 和切片。

---

## 1. 今天的学习目标

【相关知识点】

- **RAG 评估三维度**：
  1. **召回率（Retrieval Recall）**：该检索到的 chunk 有没有被检索到？
  2. **忠实度（Faithfulness）**：LLM 回答是否基于检索内容，有没有编造？
  3. **可用性（Usefulness）**：回答是否清晰、对用户有帮助？
- **幻觉（Hallucination）**：LLM 在资料不足时「脑补」内容。RAG 的核心价值就是减少幻觉，但必须用测试验证。
- **迭代思维**：RAG 不是一次做完，而是「测试 → 发现问题 → 调 prompt / 调 chunk / 调 top-k → 再测试」的循环。

---

## 2. 今天的实操任务

### 任务 1：建立评估表

在本目录创建 `eval-questions.md`（你自己填写结果）：

```markdown
# RAG 评估表

| # | Persona | 问题 | 期望命中文档 | 实际来源 | 回答是否忠实 | 通过 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | sophie | 你的技术栈是什么？ | skills-and-stack.md | skills-and-stack.md | ✅ | 对 |
| 2 | sophie | 你做过哪些项目？ | projects.md | skills-and-stack.md | ✅ | ❌ |
| 3 | sophie | 你的教育背景？ | resume.md |  |  |  |
| 4 | sophie | 你得过图灵奖吗？ | （无） |  | 应说「不知道」 | ✅ |
| 5 | sophie | React 和 Vue 你更擅长哪个？ | skills-and-stack.md | skills-and-stack.md | ✅ | ✅ |
| 6 | naval | 什么是特殊知识？ | wealth.md | wealth.md& education_philosophy | ✅ | ✅ |
| 7 | naval | 如何获得财富？ | wealth.md | wealth.md | ✅ | ✅ |
| 8 | naval | 幸福的定义是什么？ | 03_happiness.md | happiness.md | ✅ | ✅ |
| 9 | naval | 那瓦尔推荐买什么股票？ | （无） |  | 应说「不知道」 | ✅ |
| 10 | naval | 杠杆有哪些类型？ | wealth.md | wealth.md | ✅ | ✅ |
```

### 任务 2：逐题测试并记录

对每题：

1. 在前端提问
2. 记录实际 sources chip
3. 判断回答是否忠实（有没有编造）
4. 打 ✅ / ❌

### 任务 3：根据结果迭代（至少修 1 个问题）

常见问题与修复方向：

| 问题 | 可能原因 | 修复方向 |
| --- | --- | --- |
| 检索不到正确 chunk | chunk 太大 / 关键词缺失 | 缩小 chunk 或补充文档关键词 |
| 检索到了但 LLM 忽略 | prompt 不够强 | 加强 system prompt 约束 |
| 不该编的时候编了 | top-k 太低或 prompt 弱 | 加「资料中没有则明确说不知道」 |
| Naval 混入 Sophie 内容 | collection 没隔离 | 检查 ingest 和 retrieve 的 persona 路由 |

### 任务 4：阶段 3 收尾检查

- [-] `server/data/documents/` 有完整文档
- [-] `python -m rag.ingest` 可重复运行
- [-] `/api/chat` 按 persona 检索不同知识库
- [-] 前端展示 sources chip
- [-] 评估表 ≥ 8/10 通过
- [ ] （Step 07）联网搜索 toggle + Web 引用展示

---

## 3. 阶段 3 完成标志

```text
访客在 Hero 区域：
  1. 切换 Sophie / Naval
  2. 提问
  3. 看到流式回答 + 引用来源
  4. 胡编乱造的问题得到「资料中没有提到」（或 Step 07 联网补充）
  5. （Step 07）可切换联网，Web 来源以链接形式展示
```

此时 Agent Flow 画布里的「RAG Store → VectorDB retrieved 3 chunks」节点叙事与真实代码一致。

---

## 4. 今日学习记录

```md
## 今日复盘

1. 为知识库增加metadata做为title优化检索结果
2. 一个简单的、一次性的数据导入脚本在真实场景中是远远不够的。知识库是活的，它会不断更新、修改、增删，而同步管线必须能优雅地处理这些变化。

### 遇到的核心问题 + +最初的 ingest.py 脚本虽然能将 .md 文件切片并向量化存入 ChromaDB，但在面对知识库的动态变化时，

### 考虑到项目当前的规模，我采用了最简单也最可靠的 “完全重建” (Full Re-ingestion) 策略
```
