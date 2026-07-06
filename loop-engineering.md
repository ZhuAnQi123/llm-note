# Loop Engineering（循环工程）

**Loop Engineering 的核心思想是：“你不应该再亲自给 AI Agent 写提示词了，你应当去设计那个让 Agent 替你写提示词的‘循环（Loop）’。”**

### 💡 核心演进：从 “敲回车” 到 “造流水线”

在过去两年的 AI 浪潮中，我们与 AI 协作的模式经历了四个阶段的演变：

```
1. Prompt Engineering (提示词工程) ───► 关注“你怎么写好一句话”（措辞、格式）
2. Context Engineering (上下文工程) ───► 关注“AI 这一单次推理能看到什么”（系统指令、记忆）
3. Harness Engineering (环境工程)   ───► 关注“给单次运行配齐装备”（运行规则、检查器、沙盒）
4. Loop Engineering (循环工程)      ───► 关注“自动化控制系统”（让 Agent 在闭环中自我迭代直至目标达成）
```

*   **传统方式**：你写提示词 $\rightarrow$ AI 运行 $\rightarrow$ 你看结果 $\rightarrow$ 你写下一句提示词。**你成了 AI 的“保姆”和调度员**。
*   **Loop 方式**：你定义一个**目标**和**停止条件** $\rightarrow$ 系统自动执行、观察结果、自我修正，不断循环，直到验证通过后自动停下。**你从“操作机器的工人”变成了“设计生产线的工程师”**。

正如 **Claude Code 之父 Boris Cherny** 极具代表性的一句话所说：“*我已经不给 Claude 写提示词了。我有一堆循环（Loops）在跑，它们负责写提示词并决定下一步干什么。我的工作是写循环。*”

---

### 🧱 Loop Engineering 的 “六块积木”

Google Cloud AI 总监 Addy Osmani 撰文系统地拆解了 Loop Engineering 的构成，指出它主要由以下六个核心组件（5个积木 + 1个记忆层）拼接而成：

1.  **Automations（自动化/触发器）**
    *   **循环的闹钟**。可以通过 cron 定时任务、或者特定事件（如 Git Push、Bug 提交）自动触发 Loop 运行。比如你可以在github配置一个文件：“一旦有人向这个项目提交了新的代码（`push` 事件），或者创建了一个新的任务（`issue` 事件），就请你自动运行我指定的这一套程序（也就是我们的 Loop）。
2.  **Worktrees（隔离工作树）**
    *   好几个机器人（AI Agent）同时在干活的时候为了防止多个 Agent 在同一个代码库里同时修改文件导致冲突（Step on each other），Loop 系统会为其创建独立的 Git Worktrees 隔离环境，支持并发作业。
3.  **Skills（技能库）**
    *  将项目特定的规范（比如比如代码风格、设计模式）、架构设计、踩坑记录（不要用某个过时的函数、处理某个问题要用特定的方法）写成一本清晰的手册，以显式规则（如 `.claudemd` 或自定义 Skills）写下来。这是防止 Agent 盲目瞎猜（幻觉）和重复犯错的关键。
4.  **Plugins & Connectors（插件与连接器）**
    *   让 Agent 能够调用真实世界的工具（运行测试、读写文件、搜索代码库、调用外部 Slack/Jira API 等），拓宽其能力边界。
5.  **Sub-agents（子智能体/多角色协同）**
    *   建立“**生成-审核（Maker-Checker）**”机制。例如：由一个 Agent 负责写代码，另一个独立的 Agent 负责运行测试和审查代码，避免自我包庇。
6.  **Memory / External State（外部状态与跨会话记忆）**
    *   Agent 的记忆力很短（就像金鱼一样，受限于 Token 窗口）。如果一个任务太复杂，需要好几个小时，或者中间断电了就会失去任务进度。在 Token 上下文窗口之外，用一个状态文件（比如 `state.md` 或 `state.json`）记录了解历史进度，确保 Loop 即使中断，第二天也能无缝继续。

---

### 🛠️ 现实中的落地：`/goal` 命令

目前，最前沿的 AI 命令行工具（如 **Claude Code** 和 **OpenAI Codex CLI**）已经直接内置了 Loop 相关的命令：

*   **`/goal` 命令**：这是 Loop Engineering 在终端里最典型的表现形式。
    *   你无需一步步指挥它，只需敲入：`$ /goal "让 test/auth 下的所有测试通过，并且 lint 检查无报错"`。
    *   Agent 就会自己去跑测试 $\rightarrow$ 报错 $\rightarrow$ 改代码 $\rightarrow$ 再跑测试，一遍一遍循环，直到验证成功才会停下。

---

### ⚠️ 爆火背后的“冷思考”与避坑指南

尽管 Loop Engineering 能够极大地释放生产力，但业内专家也指出了其可能带来的负面效应（也被称为 **“Loop 的三个大坑”**）：

*   **💸 恐怖的 Token 消耗**：由于 Agent 是在无人值守的闭环中不断自我尝试，如果遇到无法解决的“死循环”或逻辑死结，它可能会在一夜之间跑掉成百上千美元的 API Token 费用。
*   **📉 认知债务（Cognitive Debt）**：Loop 可能会在 3 分钟内自主生成、修改几千行代码并自动提了 PR。当第二天早上系统崩溃，而没有任何一个人类工程师真正读过和理解这些代码时，维护灾难就发生了。
*   **🧠 “降智”风险**：Addy Osmani 警告称，不要被 Loop 的高效所诱惑，变成只懂点“运行键”、失去深度思考能力的开发者。

> 📌 **Key Takeaway / 核心寄语**
> **“Build the loop. But build it like someone who intends to stay the engineer.”** （去构建循环，但要像一个打算继续当工程师的人那样去构建它。）
> 
> 循环放大的不是你的能力，而是你的习惯。它是一个极强大的生产力放大器，但方向盘和“最终审核权”依然需要紧紧握在人类手中。