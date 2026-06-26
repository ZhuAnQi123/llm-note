# Step 06：用户反馈闭环 (Day 17)

日期：2026-06-21  
阶段：阶段 4 - Prompt 工程化 & 可观测性  
目标：在 AI 气泡旁加 👍/👎，把用户反馈关联到 `message_id` 和 `prompt_version`，形成迭代闭环。

---

## 1. 今天的学习目标

【相关知识点】

- **Human Feedback Loop**：自动化 eval 覆盖不了所有真实场景。用户 👎 是最宝贵的「回归测试用例」来源——每次 👎 都应考虑加入 `test_cases.yaml` 的 regression 类。
- **反馈与 A/B 的关系**：
  ```text
  v1.0 好评率 72%  vs  v1.1 好评率 85%  → v1.1 胜出，设为默认版本
  ```
- **轻量 MVP**：不需要复杂的 RLHF，只需 👍/👎 + 可选文本备注。

---

## 2. 今天的实操任务

### 任务 1：扩展 API

`server/schemas.py`：

```python
class FeedbackRequest(BaseModel):
    message_id: str
    rating: Literal["up", "down"]
    comment: str = ""  # 可选
```

`main.py` 新增：

```python
@app.post("/api/feedback")
async def submit_feedback(request: FeedbackRequest):
    # 写入 feedback_logs.jsonl，关联 message_id
```

### 任务 2：后端关联 prompt_version

`chat_logs.jsonl` 中已有 `message_id`。反馈日志写入：

```json
{
  "message_id": "abc-123",
  "rating": "down",
  "comment": "编造了没做过的项目",
  "timestamp": "..."
}
```

分析时 join 两张日志，得到「v1.1 的 👎 率」。

### 任务 3：前端 UI

在 `HeroSection.tsx` AI 气泡下方（流式结束后）：

```text
┌─────────────────────────────────┐
│ AI 回复正文……                    │
│ 📎 resume.md · 工作经历          │
│                          👍  👎 │  ← 轻量反馈按钮
└─────────────────────────────────┘
```

**设计提示：**
- 只在 `isStreaming: false` 时显示
- 点击后按钮变色（已反馈），不可重复点
- 👎 可弹出一个极简 textarea「哪里不对？」（可选）

### 任务 4：👎 → 回归用例工作流

建立习惯（写进 OVERVIEW）：

```text
收到 👎 → 查 chat_logs 找到 user_message + prompt_version + response
       → 分析原因（幻觉？风格？漏检索？）
       → 加入 test_cases.yaml regression 类
       → 改 Prompt → 跑 eval → 确认修复
```

### 任务 5：反馈率分析脚本

```python
# server/eval/feedback_analysis.py
# 输出：v1.0 好评率 vs v1.1 好评率
```

---

## 3. 验收方式

1. AI 回复完成后可见 👍/👎 按钮
2. 点击 👍 后 `POST /api/feedback` 成功，按钮变为已选状态
3. `feedback_logs.jsonl` 有记录且 `message_id` 可关联到 `chat_logs.jsonl`
4. `feedback_analysis.py` 输出各 prompt_version 好评率
5. 手动模拟 1 次 👎 → 将其转化为 `test_cases.yaml` 的 regression 用例

---

## 4. 今日学习记录

```md
## 今日复盘

- 今天我理解了：
- 今天我亲手实现了：
- 今天我卡住了：
- 明天我要继续：Step 07 Dashboard
```
