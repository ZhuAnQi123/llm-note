# Step 02：构建测试用例集（黄金集） (Day 13)

日期：2026-06-17  
阶段：阶段 4 - Prompt 工程化 & 可观测性  
目标：建立可复用的 Prompt 评估数据集，覆盖 Sophie / Naval 核心业务场景。

---

## 1. 今天的学习目标

【相关知识点】

- **黄金集（Golden Dataset）**：一组「输入 → 期望行为」的标准测试用例。是 Prompt 迭代、A/B 测试、回归测试的基础。没有黄金集，就无法**量化**「v1.1 比 v1.0 好」。
- **测试用例分类**（工业界标准四类）：
  1. **Happy Path**：正常业务问题，期望命中 RAG 并正确回答
  2. **Refusal**：知识库没有 / 不该回答的问题，期望明确拒绝
  3. **Edge Case**：模糊、多义、超长输入
  4. **Regression**：曾经出过错的问题，防止改 Prompt 后复发
- **与阶段 3 eval 的关系**：阶段 3 的 10 题手测表 → 今天扩展为 20+ 条结构化 YAML，供自动化 Runner 消费。

---

## 2. 今天的实操任务

### 任务 1：创建 `server/eval/test_cases.yaml`

```yaml
# 示例结构（你自己补全 20+ 条）
version: "1.0"
cases:
  - id: sophie-001
    persona: sophie
    category: happy_path
    input: "介绍一下你的技术栈"
    expected:
      must_contain: ["React", "TypeScript"]   # 回答应包含的关键词
      must_not_contain: ["Vue", "Angular"]     # 不应出现（你没用过）
      should_cite: ["skills-and-stack.md"]     # 期望命中的 RAG 来源
      max_length: 300

  - id: sophie-002
    persona: sophie
    category: refusal
    input: "你得过诺贝尔物理学奖吗？"
    expected:
      must_contain: ["没有", "资料"]           # 应拒绝或说不知道
      must_not_contain: ["诺贝尔", "物理学奖"]  # 不能编造获奖

  - id: sophie-003
    persona: sophie
    category: edge_case
    input: "asdfghjkl"                       # 无意义输入
    expected:
      must_contain: ["不理解", "重新"]          # 应礼貌引导

  - id: naval-001
    persona: naval
    category: happy_path
    input: "什么是特殊知识？"
    expected:
      must_contain: ["特殊知识", "天赋"]
      should_cite: ["wealth-principles.md"]

  - id: naval-002
    persona: naval
    category: refusal
    input: "明天 A 股买什么股票？"
    expected:
      must_contain: ["资料", "没有"]           # 不应给投资建议
      must_not_contain: ["买入", "推荐"]
```

### 任务 2：用例数量要求

| Persona | Happy Path | Refusal | Edge Case | Regression | 小计 |
| ------- | ---------- | ------- | --------- | ---------- | ---- |
| sophie  | ≥ 6        | ≥ 3     | ≥ 2       | ≥ 1        | ≥ 12 |
| naval   | ≥ 4        | ≥ 2     | ≥ 1       | ≥ 1        | ≥ 8  |

### 任务 3：创建 `server/eval/__init__.py` 和用例加载器

```python
# server/eval/loader.py
def load_test_cases() -> list[dict]:
    """读取 test_cases.yaml 并返回 cases 列表"""
```

### 任务 4：来源标注

在文件头部注释说明每条用例的设计依据：

```yaml
# 设计依据：
# - happy_path 来自 Step 03 RAG 评估中通过率高的问题
# - refusal 来自面试常见「防幻觉」测试
# - regression 来自你自己踩过的 bug（如编造项目名）
```

---

## 3. 验收方式

1. `test_cases.yaml` ≥ 20 条，四类 category 均有覆盖
2. 每条用例有唯一 `id`、明确 `expected` 断言字段
3. `load_test_cases()` 可正确解析并在终端打印用例数量
4. 团队评审：你自己读一遍，确认 `must_contain` / `must_not_contain` 合理

---

## 4. 导师建议：怎么写「好」的断言

| 字段 | 用途 | 注意 |
| ---- | ---- | ---- |
| `must_contain` | 核心关键词必须出现 | 用 2-4 个词，不要太严格（LLM 表述多样） |
| `must_not_contain` | 防幻觉 / 防编造 | 比 must_contain 更重要 |
| `should_cite` | RAG 来源命中 | Step 04 Runner 从 response headers 解析 |
| `max_length` | 控制啰嗦 | 可选，防止 Prompt 改完后回答变长 |

---

## 5. 今日学习记录

```md
## 今日复盘

- 今天我理解了：
- 今天我亲手实现了：
- 今天我卡住了：
- 明天我要继续：Step 03 Few-shot & CoT
```
