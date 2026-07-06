# Step 01：整理 RAG 数据源 (Day 5)

日期：2026-06-09  
阶段：阶段 3 - 个人知识库 RAG  
目标：为 Sophie 和 Naval 两个 Persona 准备结构化文档，建立项目级数据目录规范。

---

## 1. 今天的学习目标

【相关知识点】

- **RAG 的第一步永远是数据，不是模型**：Garbage in, garbage out。向量检索的质量 80% 取决于你喂了什么文档、文档结构是否清晰。
- **Metadata 设计**：每个文档切片需要携带 `persona`、`source`（文件名）、`title`（章节标题）等 metadata，后续检索过滤和前端引用展示都依赖它。
- **Namespace 隔离**：Sophie 和 Naval 是两个独立的「知识空间」。用 ChromaDB 的 **Collection**（或 metadata filter）隔离，避免 Sophie 的回答混入 Naval 的内容。

---

## 2. 对应 requirement.md 的哪一块？

> 「你可以用简历喂给"自己"，用《那瓦尔宝典》喂给"那瓦尔"，展示多 Agent 路由或多知识库检索能力。」

今天不做代码检索，先把「饲料」准备好。

---

## 3. 今天的实操任务

### 任务 1：创建数据目录

在 `server/` 下建立：

```text
server/data/documents/
  sophie/
    01-profile.md          # 个人信息 + 一句话定位（对外）
    02-skills.md           # 纯技能清单（对外）
    03-experience-summary.md # 经历摘要（对外，或直接由 projects/ 替代）
    04-projects/           # 详细项目文档
      Project_A.md
      Project_B.md
  naval/
    ├── 00_index.md
    ├── 01_wealth.md              ← 合并：卡片 S1、S2（成功、十年投入）
    ├── 02_judgment.md            ← 合并：卡片 D1-D4、C1-C2、V2（决策、信任、认知）
    ├── 03_happiness.md           ← 合并：卡片 F1-F5、H5-H6、V1、V3（幸福、价值观）
    ├── 04_reading_list.md        ← 合并：卡片 L1-L5（阅读习惯与方法）
    ├── 05_habits_self_improvement.md  ← 建议新建：卡片 H1-H4（习惯、健康、自律）
    ├── 06_education_philosophy.md     ← 建议新建：卡片 E1-E2、F5（教育、生命意义）
    └── /raw_interviews/
        └── the_knowledge_project_naval_2020_raw.md  ← 完整转录稿（清洗后）
```

### 任务 2：文档规范 (Markdown Document Convention)

为了能够使得 `chunker.py` 准确高效地切片并提取 metadata，所有的文档（特别是 `projects/` 下的项目文件）必须遵循以下严格的规范：

1. **一级标题 (H1)**：只能有一个，作为文档/项目的全名（`doc_title`）。
2. **Metadata 行**：紧跟在一级标题下，使用 `> metadata: ` 开头，以逗号分隔键值对。
   - `persona` 是必须的。
   - 其他建议的元数据如 `type`（如 `project`, `resume`），`updated`，`role`。
3. **二级标题 (H2)**：文档的主体内容必须分到不同的 `## ` 二级标题下。`chunker.py` 会按二级标题切片。如果不分二级标题，切片结果可能会混乱。
4. **内容长度**：二级标题下的正文段落尽量简练（每个二级章节 100-500 字最佳），确保内容高信息密度。

**项目文件模板示例：**

```markdown
# [Project Name: 比如 FXMarketingAgent]

> metadata: persona=sophie, type=project, updated=2026-06-23, role=Lead Frontend

## 1. Project Overview (项目概览)

正文内容……（是什么，解决了什么问题）

## 2. Technical Stack (技术栈)

正文内容……（用到的框架、大模型等）

## 3. Key Contributions (核心贡献)

正文内容……（你负责了什么，难点在哪里）
```

### 任务 3：编写 Sophie 文档（至少 3 份）

编写 `resume.md`，`skills-and-stack.md` 以及 `projects/` 文件夹下的独立项目文档。

**内容要求：**

- 只写**真实**经历，不夸大
- 每段 100-300 字，便于后续切片
- 包含可被问到的关键词：React、TypeScript、Streaming UX、Qwen、FastAPI 等

### 任务 3：编写 Naval 文档（至少 2 份）

- 从《那瓦尔宝典》或公开播客摘录，**注明来源**
- 主题覆盖：特殊知识、杠杆、财富、幸福
- 同样用 `##` 标题分节

### 任务 4：更新 `.gitignore`

```gitignore
# 向量库持久化目录（Step 03 会生成）
server/data/chroma/
```

文档本身（`documents/`）**可以提交 git**，向量库数据不要提交。

---

## 4. 验收方式

3. 每个文件有清晰的 `##` 标题层级
4. 人工阅读：随便问「Sophie 用过什么框架？」能在文档里找到答案

---

## 5. 常见错误排查

### 文档太长不分节

**问题**：一个 5000 字的 `resume.md` 没有 `##` 标题。  
**解决**：按「教育 / 工作经历 / 技能 / 项目」分节，便于 chunker 按语义切。

### Naval 内容侵权风险

**问题**：整本《那瓦尔宝典》复制粘贴。  
**解决**：只摘录核心观点 + 注明出处，够 RAG demo 即可。

### Naval 资料：PDF 还是 Markdown？

**问：我已经下载了《那瓦尔宝典》整本 PDF，可以直接用吗？**

**导师建议：先用 Markdown 摘录，不要整本 PDF 直接入库。**

| 方式 | 是否推荐 | 原因 |
| --- | --- | --- |
| **自己整理成 2-3 份 `.md`** | ✅ 强烈推荐 | Step 02 的 chunker 按 Markdown 标题切；metadata 清晰；引用展示友好 |
| **整本 PDF 直接入库** | ❌ 不推荐 | 需额外写 PDF 解析（页眉页脚、断行、双栏）；切片质量差；版权风险 |
| **PDF → 转 MD 再入库** | ⚠️ 进阶可选 | 若坚持，用 `pdfplumber` 提取文字后**人工校对**再存 `.md`，不要跳过校对 |

**为什么不需要整本书？**

- Naval Persona 的目标是展示「专属知识库路由」，不是做电子书全文检索
- 10-20 条高质量摘录 + 正确引用，比 200 页乱序 PDF chunks 效果更好
- 你的 Agent Flow 画布写的是 `top-k=3 chunks`，小库精准比大库粗糙更有说服力

> 若将来确实要支持 PDF，可在 Step 02 之后加「进阶：PDF ingest 管道」——但那不是 Day 5 的路径。

---

## 6. 今日学习记录

```md
## 今日复盘

- 今天我理解了：知识库的要求不需要全文，而是提炼总结
- 今天我亲手实现了：把那瓦尔宝典整理提炼成知识库。获取知识库(那瓦尔宝典 & Youtube那瓦尔访谈)--数据清洗--提炼
- 今天我卡住了：[undo]resume暂时没有准备好，later
- 明天我要继续：Step 02 chunking
```
