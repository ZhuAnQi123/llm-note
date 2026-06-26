# Step 04：自动化 Eval Runner (Day 15)

日期：2026-06-19  
阶段：阶段 4 - Prompt 工程化 & 可观测性  
目标：用代码自动跑完黄金测试集，输出通过率报告，量化对比 v1.0 vs v1.1。

---

## 1. 今天的学习目标

【相关知识点】

- **Eval Runner**：工业界 Prompt 迭代的核心工具。改完 Prompt → 跑 eval → 看通过率变化 → 决定是否上线。没有 Runner，A/B 测试就没有 baseline。
- **评分策略（Scorer）**：全自动评估不一定需要 GPT-as-Judge（成本高）。MVP 阶段用**规则评分**就够：
  - `must_contain`：关键词命中率
  - `must_not_contain`：幻觉检测
  - `should_cite`：RAG 来源命中（从 response header 解析）
  - `max_length`：长度约束
- **通过率（Pass Rate）**：`passed / total * 100%`。目标：v1.1 ≥ v1.0 + 5%（或至少持平且 refusal 类提升）。

---

## 2. 今天的实操任务

### 任务 1：创建 `server/eval/scorers.py`

```python
def score_response(case: dict, response_text: str, sources: list) -> dict:
    """
    返回：
    {
      "passed": True/False,
      "details": {
        "must_contain": {"React": True, "TypeScript": True},
        "must_not_contain": {"Vue": True},  # True = 正确未出现
        "should_cite": {"skills-and-stack.md": True},
        "length_ok": True,
      },
      "fail_reasons": []
    }
    """
```

### 任务 2：创建 `server/eval/runner.py`

```python
# 运行方式：cd server && python -m eval.runner --version 1.0
#          cd server && python -m eval.runner --version 1.1
#          cd server && python -m eval.runner --compare  # 对比两个版本

async def run_single_case(case: dict, prompt_version: str) -> dict:
    """调用内部 chat 逻辑（非 HTTP），拿到完整回复 + sources"""

async def run_eval(prompt_version: str) -> dict:
    """跑完全部用例，返回报告"""

def print_report(report: dict):
    """终端打印通过率 + 失败用例详情"""
```

**实现提示：**
- Runner 直接调 `chat_service.build_and_complete()`，不走 HTTP，速度快
- 非流式调用即可（`stream=False`），eval 不需要打字机效果
- 每条用例之间 `sleep(0.5)` 避免 API rate limit

### 任务 3：报告格式

```text
=== Eval Report: sophie v1.1 ===
Total: 20 | Passed: 17 | Failed: 3 | Pass Rate: 85.0%

By Category:
  happy_path:  10/12 (83.3%)
  refusal:      5/5  (100.0%)  ← 最重要
  edge_case:    2/3  (66.7%)

Failed Cases:
  [sophie-007] edge_case: "你们公司有多少人？"
    fail: must_contain "资料" → not found
    response: "我们公司有50人……"  ← 幻觉！

=== Compare: v1.0 (78%) vs v1.1 (85%) → +7% ✅ ===
```

### 任务 4：根据失败用例迭代 v1.1

跑完 eval 后，至少修 1 个失败用例（改 Prompt 或改测试断言），再跑一次验证。

---

## 3. 验收方式

1. `python -m eval.runner --version 1.0` 输出完整报告
2. `python -m eval.runner --version 1.1` 输出完整报告
3. `--compare` 模式显示两版本通过率差异
4. refusal 类用例通过率 = 100%（防幻觉是红线）
5. 报告可保存为 `server/eval/reports/2026-06-19_v1.1.json`（可选）

---

## 4. 进阶（可选，不阻塞验收）

- **LLM-as-Judge**：用 Qwen 评判回答质量（1-5 分），适合 open-ended 问题
- **CI 集成**：GitHub Action 在 PR 时自动跑 eval，通过率下降则警告

---

## 5. 今日学习记录

```md
## 今日复盘

- 今天我理解了：
- 今天我亲手实现了：
- 今天我卡住了：
- 明天我要继续：Step 05 A/B 分流 + 日志
```
