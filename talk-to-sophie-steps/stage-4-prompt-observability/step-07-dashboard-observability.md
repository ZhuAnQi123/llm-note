# Step 07：Dashboard 可观测性 (Day 18)

日期：2026-06-22  
阶段：阶段 4 - Prompt 工程化 & 可观测性  
目标：让 Dashboard 展示真实工程指标——LLM 调用、Prompt 版本分布、Eval 通过率、RAG 规模。

---

## 1. 今天的学习目标

【相关知识点】

- **可观测性三板斧**：Logs（日志）→ Metrics（指标）→ Dashboards（看板）。阶段 4 的 Step 05–06 产生了 Logs，今天聚合为 Metrics 并可视化。
- **Prompt 工程师最关心的 Dashboard 指标**：
  1. 各 `prompt_version` 调用占比
  2. 各版本平均 latency / response_length
  3. 各版本 👍 率（来自 feedback 日志）
  4. 最近一次 eval 通过率
  5. RAG chunk 数 / 文档数

---

## 2. 今天的实操任务

### 任务 1：创建 `server/services/stats_service.py`

```python
def get_stats() -> dict:
    """
    聚合返回：
    {
      "llm_calls": {
        "total": 156,
        "by_model": {"qwen-turbo": 156},
        "by_persona": {"sophie": 98, "naval": 58},
        "avg_latency_ms": 1100,
        "last_updated": "2026-06-22T10:00:00"
      },
      "prompt_versions": {
        "1.0": {"calls": 78, "thumbs_up_rate": 0.72},
        "1.1": {"calls": 78, "thumbs_up_rate": 0.85}
      },
      "eval": {
        "last_run": "2026-06-19",
        "v1.0_pass_rate": 0.78,
        "v1.1_pass_rate": 0.85
      },
      "rag": {
        "sophie_chunks": 24,
        "naval_chunks": 18,
        "documents": 5
      },
      "github": {
        "commits_30d": 42,
        "last_updated": "..."
      }
    }
    """
```

### 任务 2：`GET /api/stats` 路由

```python
@app.get("/api/stats")
async def stats():
    return stats_service.get_stats()
```

### 任务 3：GitHub 数据接入（轻量）

```python
# stats_service.py 内
def fetch_github_commits(owner, repo, days=30) -> int:
    # GET https://api.github.com/repos/{owner}/{repo}/commits?since=...
    # GITHUB_TOKEN 可选，放 .env
    # 结果缓存 1 小时
```

### 任务 4：前端 `DashboardSection.tsx`

从 `App.tsx` 抽离 Dashboard 区域为独立组件：

```typescript
// src/services/statsService.ts
export async function fetchStats() { ... }

// src/components/DashboardSection.tsx
// 替换 mock 数据，展示真实指标
```

**展示建议（对应 requirement.md 数据墙）：**

| 卡片 | 数据来源 | 展示 |
| ---- | -------- | ---- |
| LLM 调用 | chat_logs | 总次数 + 近 7 天趋势 |
| Prompt 版本 | chat_logs | v1.0 vs v1.1 饼图 |
| Eval 通过率 | eval reports | v1.1: 85% ✅ |
| RAG 规模 | ChromaDB | chunk 数 + 文档数 |
| GitHub | GitHub API | 30 天 commit 数 |
| 好评率 | feedback_logs | v1.1: 85% 👍 |

### 任务 5：图表库（可选）

引入 `recharts` 画一个简单的 7 天调用趋势折线图。不引入也可以先用数字 + 进度条。

---

## 3. 验收方式

1. `GET /api/stats` 返回真实数据，不是 mock
2. Dashboard 页面数字与 API 一致
3. Prompt 版本分布反映 A/B 分流结果
4. Eval 通过率来自最近一次 `eval.runner` 报告
5. 每个指标区域显示「最后更新于 HH:MM」

---

## 4. 阶段 4 完成检查清单

全部勾选后，阶段 4 验收通过：

- [ ] Prompt 模板化 + 版本管理（Step 01）
- [ ] 黄金测试集 ≥ 20 条（Step 02）
- [ ] Few-shot + CoT v1.1（Step 03）
- [ ] 自动化 Eval Runner（Step 04）
- [ ] A/B 分流 + 调用日志（Step 05）
- [ ] 用户反馈 👍/👎（Step 06）
- [ ] Dashboard 真实指标（Step 07）

---

## 5. 今日学习记录

```md
## 今日复盘

- 今天我理解了：
- 今天我亲手实现了：
- 今天我卡住了：
- 明天我要继续：阶段 5 部署 & 上线
```
