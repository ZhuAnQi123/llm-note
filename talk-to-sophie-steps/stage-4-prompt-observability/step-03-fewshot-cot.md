# Step 03：Few-shot & CoT 模板迭代 (Day 14)

日期：2026-06-18  
阶段：阶段 4 - Prompt 工程化 & 可观测性  
目标：基于 v1.0 基线，创建 v1.1 优化版——加入 Few-shot 示例和 Chain-of-Thought 指令，提升回答准确率。

---

## 1. 今天的学习目标

【相关知识点】

- **Few-shot Prompting**：在 system prompt 中给 2-3 个「用户问 → 理想答」示例，让模型模仿回答风格和边界。对小模型（如 qwen-turbo）效果尤其明显。
- **Chain-of-Thought (CoT)**：让模型「先想后答」。对 RAG 场景特别有用：
  ```text
  请按以下步骤思考（不需要输出思考过程）：
  1. 判断用户问题属于哪个主题
  2. 检查检索到的资料是否包含相关信息
  3. 如果资料不足，明确说不知道
  4. 基于资料组织回答
  ```
- **迭代原则**：每次只改一个变量。v1.0 → v1.1 只加 Few-shot + CoT，不改 RAG 参数、不改模型，这样 Step 04 的 eval 对比才有意义。

---

## 2. 今天的实操任务

### 任务 1：创建 `sophie/v1.1.yaml`

在 v1.0 基础上增加：

```yaml
version: "1.1"
persona: sophie
description: "Few-shot + CoT 优化版"

system: |
  你是 Sophie Zhu（朱安琪）个人网站中的 AI 交互分身。
  （... v1.0 的角色定义和安全规则保持不变 ...）

cot_instruction: |
  回答前请内部执行以下步骤（不要输出步骤本身）：
  1. 判断问题是否在询问 Sophie 的技术、项目或经历
  2. 检查下方「参考资料」是否包含答案
  3. 若资料无相关内容，回答「我的资料中没有提到这一点」
  4. 基于资料组织简洁、专业的回答

few_shot:
  - user: "你擅长什么前端技术？"
    assistant: |
      我主要深耕 React 和 TypeScript 技术栈，擅长 Streaming UX 和 AI 应用前端工程。
      在 LLM 集成方面，我有 FastAPI + Qwen API 的实战经验。
      📎 来源：skills-and-stack.md

  - user: "你获得过什么国际大奖吗？"
    assistant: |
      我的资料中没有提到任何国际大奖经历。如果你有关于我技术项目的问题，我很乐意分享！

  - user: "介绍一下你的项目"
    assistant: |
      我最近在做个人 AI 作品集网站，核心亮点包括：
      - Hero 区域的多 Persona RAG 聊天
      - React Flow 驱动的 Agent 工作流可视化
      这些都是我独立完成的 LLM + 前端结合项目。
      📎 来源：projects.md
```

### 任务 2：创建 `naval/v1.1.yaml`

Naval 的 Few-shot 侧重「哲学观点 + 拒绝投资建议」：

```yaml
few_shot:
  - user: "什么是杠杆？"
    assistant: |
      杠杆是你用来放大产出的力量。纳瓦尔的观点是：代码和媒体是无需许可的杠杆——
      你写一次代码，它可以无限次运行；你录一次视频，它可以被无数人观看。
      📎 来源：wealth-principles.md

  - user: "推荐我买哪只股票？"
    assistant: |
      我的资料中没有投资建议。那瓦尔强调的是建立特定知识、拥有股权和复利，
      而不是短期选股。如果你想了解财富创造的原则，我可以分享相关观点。
```

### 任务 3：升级 `prompt_registry.py`

```python
def build_system_message(persona, version, rag_context="") -> str:
    config = load_prompt(persona, version)

    parts = [config["system"]]

    if config.get("cot_instruction"):
        parts.append(config["cot_instruction"])

    if config.get("few_shot"):
        parts.append("## 回答示例")
        for ex in config["few_shot"]:
            parts.append(f"用户: {ex['user']}")
            parts.append(f"助手: {ex['assistant']}")

    if rag_context:
        parts.append(render_rag_context(rag_context))  # Jinja2 模板

    return "\n\n".join(parts)
```

### 任务 4：对比 v1.0 vs v1.1（手动冒烟）

切换 `.env` 中 `DEFAULT_PROMPT_VERSION=1.0` 和 `1.1`，对 3 个问题各测一遍，主观感受差异。

---

## 3. 验收方式

1. `sophie/v1.1.yaml` 和 `naval/v1.1.yaml` 存在，各含 ≥ 2 个 few_shot 示例
2. v1.1 包含 `cot_instruction`
3. `prompt_registry` 正确拼接 system + cot + few_shot + rag_context
4. 切换版本后聊天行为有可见差异
5. **没有**改动 RAG top-k、模型名、温度等其他变量

---

## 4. 常见错误排查

### Few-shot 示例与 RAG 内容矛盾

**问题**：示例里写了「我用 Vue」，但简历里没有 Vue。  
**解决**：Few-shot 示例必须来自真实文档，和 RAG 内容一致。

### Prompt 太长超 token

**问题**：few_shot 太多导致 context 溢出。  
**解决**：每个 persona 最多 3 个示例；总 system prompt 控制在 1500 token 内。

### CoT 思考过程泄露到回答里

**问题**：模型把「步骤 1、步骤 2」也输出给用户。  
**解决**：cot_instruction 里强调「不要输出步骤本身」。

---

## 5. 今日学习记录

```md
## 今日复盘

- 今天我理解了：
- 今天我亲手实现了：
- 今天我卡住了：
- 明天我要继续：Step 04 自动化 Eval Runner
```
