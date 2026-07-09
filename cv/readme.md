这份大纲专为 **LLM 应用程序开发 / Prompt 工程师** 岗位量身定制。它不仅涵盖了传统算法面试中不常考但 LLM 时代必备的“新八股”，还结合了工程落地中的实际痛点。

这里先为你梳理出核心的 **6 大知识模块**。由于我无法直接生成图片格式的脑图，我为你转换成了极其清晰的 **Markdown 树状脑图结构**。你可以直接将下方代码复制到任何支持 Markdown 的脑图工具（如 XMind、Notion、幕布、Markmap 等）中，一键生成视觉脑图。

---

# 🧠 LLM / Prompt 工程师面试大纲（脑图版）

```text
# LLM & Prompt 工程师面试核心大纲
## 1. Prompt 工程核心理论与高级技巧 (Core Prompt Engineering)
### 1.1 基础提示词要素
#### 1.1.1 角色 (Role) / 任务 (Task) / 上下文 (Context) / 约束 (Constraints) / 输出格式 (Format)
### 1.2 高级提示策略 (Advanced Strategies)
#### 1.2.1 Zero-shot / Few-shot (样本选择与顺序对结果的影响)
#### 1.2.2 思维链 (CoT, Chain of Thought) 及其变体 (ToT, GoT)
#### 1.2.3 自洽性采样 (Self-Consistency)
#### 1.2.4 方向性刺激提示 (Directional Stimulus Prompting)
### 1.3 提示词防攻击与安全 (Prompt Security)
#### 1.3.1 提示词注入 (Prompt Injection) 及其防御
#### 1.3.2 越狱攻击 (Jailbreaking) 攻防
#### 1.3.3 敏感信息防泄露 (PII Protection)
### 1.4 提示词自动化与工程化
#### 1.4.1 自动提示词优化 (APE, DSPy)
#### 1.4.2 提示词版本控制与管理

## 2. 大模型基础底层原理 (LLM Fundamentals)
### 2.1 Transformer 架构核心 (高频必问)
#### 2.1.1 自注意力机制 (Self-Attention) 计算原理
#### 2.1.2 位置编码 (RoPE 等) 的作用
#### 2.1.3 Encoder-only, Decoder-only, Encoder-Decoder 的区别与代表模型
### 2.2 LLM 核心参数调节 (Decoding Parameters)
#### 2.2.1 Temperature (温度) 的数学原理与业务场景选择
#### 2.2.2 Top-p (Nucleus Sampling) vs Top-k
#### 2.2.3 Repetition Penalty (重复惩罚)
### 2.3 上下文窗口与 Token
#### 2.3.1 Tokenizer 原理 (BPE 等) 及 BPE 带来的常见坑 (如长文本算力、特殊字符)
#### 2.3.2 长文本处理方案 (针锋相对的“大海捞针”测试 Needle in a Haystack)

## 3. RAG (检索增强生成) 核心技术 (RAG Stack)
### 3.1 数据准备与预处理 (Data Ingestion)
#### 3.1.1 文档解析 (PDF, Word, 表格处理的坑)
#### 3.1.2 文本分块策略 (Chunking: Fixed-size, Semantic, Recursive)
### 3.2 向量检索 (Vector Search)
#### 3.2.1 Embedding 模型的选择与微调
#### 3.2.2 向量数据库原理与选型 (Milvus, Pinecone, Chroma 等)
#### 3.2.3 相似度度量 (余弦相似度, 内积, 欧氏距离) 的区别
### 3.3 高级 RAG 优化策略 (Advanced RAG)
#### 3.3.1 查询重写与扩展 (Query Rewriting / Expansion)
#### 3.3.2 重排机制 (Reranking: Cross-Encoder 模型)
#### 3.3.3 混合检索 (Hybrid Search: 向量检索 + 传统 BM25 关键词检索)
#### 3.3.4 父子分块 (Parent-Child Chunking) / 句子窗口检索

## 4. LLM 交互框架与 Agent 开发 (Frameworks & Agents)
### 4.1 主流开发框架
#### 4.1.1 LangChain / LlamaIndex 的核心抽象与优缺点
#### 4.1.2 为什么大厂现在倾向于原生开发或轻量级框架？
### 4.2 Agent (智能体) 架构
#### 4.2.1 Agent 的四大要素：规划 (Planning)、记忆 (Memory)、工具 (Tools)、执行 (Action)
#### 4.2.2 经典推理架构：ReAct (Reason + Action) 原理
#### 4.2.3 记忆机制：短期记忆 (Buffer) vs 长期记忆 (Vector/Summary)
### 4.3 多 Agent 协同 (Multi-Agent Systems)
#### 4.3.1 SOP (标准作业程序) 在多 Agent 中的应用
#### 4.3.2 常见多 Agent 框架 (AutoGen, CrewAI 等) 概念

## 5. 模型评估与评测 (LLM Evaluation)
### 5.1 提示词与效果评估 (Prompt Eval)
#### 5.1.1 为什么 LLM 评估很难？(主观性、随机性)
#### 5.1.2 基于规则的评估 (ROUGE, BLEU) 及其局限性
#### 5.1.3 LLM-as-a-Judge (大模型作为裁判) 的偏见与消除方法
### 5.2 RAG 系统专项评估
#### 5.2.1 Ragas 评估框架的四大核心指标：忠实度 (Faithfulness)、答案相关性、上下文召回率、上下文精确度
### 5.3 线上监控与可观测性 (LLMOps)
#### 5.3.1 监控指标：Latency (延迟), Token 吞吐量, Cost (成本), 幻觉率
#### 5.3.2 工具链：LangSmith, Phoenix 等

## 6. 工程落地与成本、性能优化 (Engineering & Optimization)
### 6.1 幻觉 (Hallucination) 治理
#### 6.1.1 幻觉产生的原因 (数据源、模型本身、Prompt 不当)
#### 6.1.2 业务落地中减少幻觉的工程手段
### 6.2 性能与延迟优化 (Latency Optimization)
#### 6.2.1 流式传输 (Streaming) 的前端配合
#### 6.2.2 提示词缓存 (Prompt Caching) 的原理与省钱技巧
#### 6.2.3 语义缓存 (Semantic Cache) 降本增效
### 6.3 业务场景微调 vs RAG vs Prompt
#### 6.3.1 面对一个业务需求，如何技术选型？(什么时候该微调，什么时候该用 RAG/Prompt？)

```

---

## 💡 后续复习与细节展开建议

这份大纲切中了目前大厂（如字节、阿里、腾讯、百度以及各 AI 独角兽）在招募 **AI 应用开发 / 提示词工程师** 时的核心高频考点。

我们接下来的“细节知识点总结”可以按照以下节奏逐块攻克：

1. **第一步：攻克第 1 块（Prompt 高级技巧）和第 3 块（RAG 核心）** —— 这是目前面试中占比最高（约 50%）的工程实践部分。
2. **第二步：攻克第 2 块（LLM 原理）** —— 用于应对面试中的“硬核技术深度”考察，防止被面试官“问倒”。
3. **第三步：攻克第 4、5、6 块（Agent、评测、优化）** —— 展现你具备带项目落地、解决复杂工程痛点的高阶能力。

