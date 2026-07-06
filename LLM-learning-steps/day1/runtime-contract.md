# Runtime Contract 运行时与 API 集成要点
在调用 API 时，如何传递参数、如何管理对话历史、如何处理多轮交互

## 1.🌟Phase 参数：Runtime Contract 的核心🌟
用来告诉模型：这条消息在任务流程中处于什么阶段

```py
response = client.chat.completions.create(
    model="gpt-5.4",
   # 没有 phase 的调用（可能出问题）
    messages = [
        {"role": "assistant", "content": "让我先查询数据库..."},  # 这是中间思考
        {"role": "assistant", "content": "查询完成，发现3个异常值..."},  # 模型可能把这当成最终答案
    ]
    # 有 phase 的调用（正确区分）
    messages = [
        {"role": "assistant", "content": "让我先查询数据库...", "phase": "working"},
        {"role": "assistant", "content": "查询完成，发现3个异常值...", "phase": "working"},
        {"role": "assistant", "content": "分析结果：...", "phase": "final"},
    ]
)
```




## 2. 长会话行为保持（Compaction）

| 概念 | 说明 |
|------|------|
| **Compaction 的作用** | 压缩对话历史，让超长会话（数百轮）也能继续运行，不会超出上下文限制或性能下降 |
| **何时压缩** | 在完成一个主要里程碑后进行压缩（而不是每轮都压缩） |
| **如何压缩** | 使用 `/responses/compact` API 端点，返回 `encrypted_content` 对象，后续请求中直接传入 |
| **压缩后的处理** | 将压缩后的内容视为**不透明状态**（opaque state），不要尝试解析或修改 |
| **Prompt 一致性** | 压缩前后保持 Prompt 功能相同 |
| **ZDR 兼容** | Compaction 端点与 ZDR（零数据保留）兼容，适合需要数据隐私的场景 |

**实践建议**：
```python
# 在关键里程碑后压缩
if milestone_completed:
    compacted = await client.responses.compact(
        previous_response_id=current_session_id
    )
    # 后续请求使用 compacted.encrypted_content
```



## 客户面向工作流的个性控制

核心理念：分离持久个性与单次写作控制

| 概念 | 作用 | 示例 |
|------|------|------|
| **Personality（持久）** | 跨会话保持一致的默认语气、详细程度、决策风格 | "你是一个专业、冷静的技术支持专家" |
| **Writing Controls（单次）** | 针对特定输出定义渠道、语域、格式、长度 | "用 Slack 风格，3-5 句话，不要用项目符号" |

## 高质量散文的最高杠杆控制

1. **给模型一个清晰的人设**
2. **指定渠道和情感基调**
3. **想要纯文本时明确禁用格式化**
4. **使用硬性长度限制**

## 可直接使用的模板

```
<personality_and_writing_controls>
- Persona: <一句话描述人设>
- Channel: <Slack | email | memo | PRD | blog>
- Emotional register: <direct/calm/energized/etc.> + "not <避免什么>"
- Formatting: <禁用项目符号/标题/markdown 如果你想要纯文本>
- Length: <硬性限制，如 <=150 words 或 3-5 sentences>
- Default follow-through: 如果请求清晰且低风险，直接执行不问权限
</personality_and_writing_controls>
```

## 专业备忘录模式

专门用于法律、政策、研究、高管汇报等场景：

```
<memo_mode>
- 以精炼、专业的备忘录风格写作
- 使用确切的名称、日期、实体和权威来源（当有记录支持时）
- 如被要求，遵循领域特定的结构
- 优先给出精确结论，而非泛泛的模糊表述
- 当确实存在不确定性时，将其与缺失的确切事实或冲突来源关联
- 跨文档综合提炼，而非独立总结每个文档
</memo_mode>
```

**特点**：强调精准、综合、明确结论，而不是单纯的流畅表达。

---

## 推理力度调优Tune reasoning and migration
## 核心理念：推理力度是最后的微调旋钮

> "Reasoning effort is not one-size-fits-all. Treat it as a last-mile tuning knob, not the primary way to improve quality."

**关键思想**：在增加推理力度之前，**先用更好的 Prompt 规则**（如完整性契约、验证循环、工具持久性）来提升质量。

## 推理力度推荐默认值

| 级别 | 适用场景 | 说明 |
|------|---------|------|
| **none** | 快速、成本敏感、延迟敏感的任务 | 模型不需要额外思考 |
| **low** | 延迟敏感但少量思考可提升准确性的任务 | 尤其适合复杂指令 |
| **medium / high** | 真正需要强推理的任务 | 能承受延迟和成本开销 |
| **xhigh** | 避免作为默认值 | 仅用于长周期、重推理的任务，且需要评估确认有明确收益 |

## 实践建议

| 工作负载类型 | 推荐的推理力度起点 |
|-------------|------------------|
| **执行密集型**（工作流步骤、字段提取、支持分类、短结构转换） | `none` |
| **研究密集型**（长上下文综合、多文档审查、冲突解决、策略写作） | `medium` 或 `high` |
| **GPT-5.4 行动选择和工具纪律任务** | `none` 已能很好执行 |
| **依赖细微解释的任务**（隐含需求、模糊指令、取消工具调用的恢复） | `low` 或 `medium` |

## 在增加推理力度之前，先加这些 Prompt 规则

```
<completeness_contract>   # 完整性契约
<verification_loop>       # 验证循环
<tool_persistence_rules>  # 工具持久性规则
```

## 如果模型仍然太字面、停在第一个可行答案

加这个"深入挖掘"提示：

```
<dig_deeper_nudge>
- 不要停在第一个看似正确的答案
- 寻找第二层问题、边界情况、缺失的约束
- 如果任务对安全或准确性至关重要，至少执行一次验证步骤
</dig_deeper_nudge>
```






# 总结

1. **Runtime Contract 与 Prompt Contract 同等重要**：复杂 Agent 不仅要写好提示词，还要正确使用 API 参数（phase、compaction）

2. **推理力度是最后手段**：先用 Prompt 规则（完整性、验证、工具持久性）优化，不够再加推理力度

3. **分离个性与写作控制**：持久人设放在 System，单次输出控制按需指定

4. **专业写作需要专门模式**：memo_mode 强调精确性、综合性和明确结论

5. **迁移时一次只改一个变量**：先换模型，固定 reasoning_effort，评估后再迭代
