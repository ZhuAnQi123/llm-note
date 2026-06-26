# Step 01：Prompt 模块化 & 版本管理 (Day 12)

日期：2026-06-16  
阶段：阶段 4 - Prompt 工程化 & 可观测性  
目标：把硬编码的 system prompt 抽离为可版本化的模板文件，建立 `prompt_registry` 加载机制。

---

## 1. 今天的学习目标

【相关知识点】

- **Prompt 即代码（Prompt as Code）**：和生产代码一样，Prompt 需要版本控制、Code Review、可回滚。硬编码在 `main.py` 里是原型做法，不是工程做法。
- **系统提示（System Prompt）结构**：工业界常用分层：
  ```text
  [角色定义] → [能力边界] → [输出格式] → [安全规则] → [RAG 上下文占位符]
  ```
- **版本管理**：`v1.0`（基线）、`v1.1`（加 Few-shot）、`v2.0`（加 CoT）—— semver 简化版，便于 A/B 对比和回滚。

---

## 2. 今天的实操任务

### 任务 1：创建 `server/prompts/` 目录结构

```text
server/prompts/
  sophie/
    v1.0.yaml      # 从现有 main.py 迁移的基线
  naval/
    v1.0.yaml
  rag_context.j2   # RAG 上下文注入（Jinja2 模板，Step 03 完善）
```

### 任务 2：定义 YAML Prompt 格式

```yaml
# server/prompts/sophie/v1.0.yaml
version: "1.0"
persona: sophie
description: "基线版 - 角色定义 + 安全边界"

system: |
  你是 Sophie Zhu（朱安琪）个人网站中的 AI 交互分身。
  你精通前端开发和 LLM 工程。

  ## 回答规则
  - 专业、诚实、简洁
  - 对不了解的内容直接说「我的资料中没有提到这一点」
  - 不要编造经历、项目或技能

  ## 输出风格
  - 中文提问用中文答，英文提问用英文答
  - 每次回答 2-4 段，不超过 200 字（除非用户要求详细）

# few_shot 和 cot 字段 Step 03 再加，今天留空或注释
# few_shot: []
# cot_instruction: ""
```

### 任务 3：创建 `server/services/prompt_registry.py`

```python
# 目标接口（你自己实现）
def load_prompt(persona: str, version: str = "1.0") -> dict:
    """从 YAML 加载指定 persona + version 的 prompt 配置"""

def build_system_message(
    persona: str,
    version: str,
    rag_context: str = "",
) -> str:
    """组装最终 system message：base system + RAG context"""
```

**实现提示：**
- 用 `PyYAML` 读 YAML（加入 `requirements.txt`）
- `rag_context.j2` 用 Jinja2 渲染（`pip install jinja2`）
- 默认 version 从环境变量 `DEFAULT_PROMPT_VERSION=1.0` 读取

### 任务 4：重构 `chat_service.py`

把 `main.py` / `chat_service.py` 里的硬编码 `system_prompt = """..."""` 替换为：

```python
from services.prompt_registry import build_system_message

system_msg = build_system_message(
    persona=request.persona,
    version=os.getenv("DEFAULT_PROMPT_VERSION", "1.0"),
    rag_context=formatted_rag_context,
)
```

### 任务 5：`.env` 追加

```env
DEFAULT_PROMPT_VERSION=1.0
```

---

## 3. 验收方式

1. `server/prompts/sophie/v1.0.yaml` 和 `naval/v1.0.yaml` 存在且内容完整
2. 聊天功能与迁移前**行为一致**（回归测试 Stage 3 的 3 个问题）
3. `main.py` 中无硬编码 system prompt 字符串
4. 修改 YAML 后重启后端，回答风格随之改变（证明模板生效）

---

## 4. 常见错误排查

### YAML 加载失败

**原因**：缩进错误或 `|` 多行字符串格式不对。  
**解决**：用在线 YAML validator 检查。

### 改 YAML 没生效

**原因**：uvicorn `--reload` 不一定监视 YAML 文件变化。  
**解决**：改 prompt 后手动重启，或配置 reload 包含 `prompts/` 目录。

---

## 5. 今日学习记录

```md
## 今日复盘

- 今天我理解了：
- 今天我亲手实现了：
- 今天我卡住了：
- 明天我要继续：Step 02 测试用例集
```
