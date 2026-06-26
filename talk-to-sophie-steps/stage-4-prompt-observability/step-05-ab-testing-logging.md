# Step 05：A/B 分流 & 调用日志 (Day 16)

日期：2026-06-20  
阶段：阶段 4 - Prompt 工程化 & 可观测性  
目标：线上自动分流 v1.0 / v1.1 Prompt，记录每次调用的完整上下文，为数据驱动迭代提供基础。

---

## 1. 今天的学习目标

【相关知识点】

- **A/B Testing（Prompt 版）**：不是前端 UI 的 A/B，而是**同一 persona 下随机分配不同 Prompt 版本**，对比真实用户场景下的表现。
- **分流策略 MVP**：
  ```python
  def assign_prompt_version(persona: str) -> str:
      # 50/50 随机分流
      return "1.1" if random.random() < 0.5 else "1.0"
  ```
- **调用日志（Observability）**：每次 chat 必须记录的最小字段集：
  ```json
  {
    "timestamp": "2026-06-20T10:30:00",
    "message_id": "uuid",
    "persona": "sophie",
    "prompt_version": "1.1",
    "user_message": "你的技术栈？",
    "response_length": 156,
    "latency_ms": 1200,
    "model": "qwen-turbo",
    "rag_hit": true,
    "rag_sources": ["skills-and-stack.md"],
    "web_search_used": false
  }
  ```

---

## 2. 今天的实操任务

### 任务 1：升级 `prompt_registry.py` 加入 A/B 分流

```python
def assign_prompt_version(persona: str) -> str:
    """
    从环境变量读取分流比例：
    AB_TEST_ENABLED=true
    AB_TEST_V1_1_RATIO=0.5  # 50% 流量给 v1.1
    """
```

### 任务 2：创建 `server/middleware/chat_logger.py`

每次 `/api/chat` 完成后，追加一行 JSON 到 `server/data/chat_logs.jsonl`：

```python
def log_chat_event(event: dict):
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
```

**MVP 存储**：JSONL 文件足够。量大了再换 SQLite。

### 任务 3：在 `chat_service.py` 中串联

```python
def handle_chat(request):
    prompt_version = assign_prompt_version(request.persona)
    start = time.time()

    # ... RAG + LLM 流式生成 ...

    log_chat_event({
        "message_id": str(uuid4()),
        "prompt_version": prompt_version,
        "latency_ms": int((time.time() - start) * 1000),
        # ...
    })
```

### 任务 4：响应 Header 暴露实验信息（调试用）

```python
headers={
    "X-Prompt-Version": prompt_version,
    "X-RAG-Sources": json.dumps(sources),
}
```

前端 DevTools 可看到当前用户命中了哪个版本。

### 任务 5：A/B 分析脚本（简单版）

```python
# server/eval/ab_analysis.py
# 读取 chat_logs.jsonl，按 prompt_version 分组统计：
# - 平均 latency
# - 平均 response_length
# - rag_hit 比例
```

---

## 3. 验收方式

1. 连续发 10 条消息，日志中 v1.0 和 v1.1 均出现（约 50/50）
2. 每条日志有完整字段：`prompt_version`, `latency_ms`, `persona`, `rag_hit`
3. `X-Prompt-Version` Header 与日志一致
4. `python -m eval.ab_analysis` 输出两版本对比表
5. 设置 `AB_TEST_ENABLED=false` 时，全部走 `DEFAULT_PROMPT_VERSION`

---

## 4. 常见错误排查

### 日志文件越来越大

**解决**：按日期轮转 `chat_logs_2026-06-20.jsonl`，或定期清理 dev 日志。

### A/B 分流不均匀

**原因**：样本量太小（< 20 条）。  
**解决**：至少 50 条后再看分布；或用 user_id hash 分流（同一用户始终同一版本，体验更一致）。

---

## 5. 今日学习记录

```md
## 今日复盘

- 今天我理解了：
- 今天我亲手实现了：
- 今天我卡住了：
- 明天我要继续：Step 06 用户反馈
```
