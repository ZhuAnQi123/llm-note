# Day 24：实战项目 - AI 自动简历解析与打分系统 (综合练习)

## 🎯 学习目标
*   整合 **Pydantic**、**Structured Output**、**Prompt Engineering (CoT)** 和 **Qwen API**。
*   实现一个完整的、具有现实业务逻辑的小型应用。
*   掌握如何通过 Prompt 给 AI 提供“打分准则 (Rubrics)”。
*   学会如何处理复杂、不规则的长文本。

---

## 📚 学习资源
*   **DashScope 文档 (必读)**: [通义千问 API 快速入门](https://help.aliyun.com/zh/dashscope/developer-reference/quick-start)
*   **Pydantic 校验技巧**: [Pydantic Validators](https://docs.pydantic.dev/latest/concepts/validators/)

---

## 🛠️ 新手必会知识点 (附例子)

### 1. 处理长文本的策略 (The Context Strategy)
*   不要把整个 PDF 塞进 Prompt（Token 可能溢出且昂贵）。
*   通常先通过 Python 去掉换行符、多余空格，或截取关键信息。

### 2. 打分逻辑 (Scoring Rubric)
在 Prompt 里明确告诉 AI 评分的标准：
*   **10分**：完全匹配，5年及以上 Python 经验。
*   **5分**：基本匹配，有 Java 经验但 Python 较弱。
*   **0分**：完全不匹配。

---

## 🧠 逻辑架构说明 (Mermaid 图示)

```mermaid
graph TD
    A[Upload Raw Resume Text] --> B[Structured Extraction]
    B --> C[Job Description Matching]
    C --> D[AI Multi-dimension Scoring]
    D --> E[Final Result (JSON)]
    E --> F[Display Result UI/Console]
```

---

## 💻 完整可运行范例：简历智能评分助手
输入简历内容和职位要求，AI 给出结构化的解析和评分报告。

```python
import os
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from dashscope import Generation
from http import HTTPStatus

# --- 1. 定义输出模型 ---
class SkillMatch(BaseModel):
    skill_name: str = Field(..., description="技能名称")
    matched: bool = Field(..., description="是否匹配简历")
    comments: str = Field(..., description="匹配详情或缺失描述")

class ResumeEvaluation(BaseModel):
    candidate_name: str = Field(..., description="候选人姓名")
    total_score: int = Field(..., description="匹配总评分 (0-100)")
    skill_analysis: List[SkillMatch] = Field(..., description="技能点对点分析")
    summary: str = Field(..., description="AI 核心评估结论")

# --- 2. 简历分析逻辑 ---
def evaluate_resume(resume_text, job_description):
    system_prompt = (
        "你是一个资深的技术面试官。你需要根据用户的简历和职位要求进行精准匹配。"
        "请严格遵守评分标准：工作年限、技能栈对标。最后必须返回符合 JSON 结构的评估报告。"
    )
    
    user_prompt = f"""
    【职位要求】：
    {job_description}

    【候选人简历】：
    {resume_text}

    请分析简历，并根据要求生成 JSON 报告。JSON 结构示例：
    {ResumeEvaluation.schema_json()}
    """

    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ]

    print("⏳ AI 专家正在分析简历中...")
    response = Generation.call(
        model="qwen-max", # 复杂任务建议用 max
        messages=messages,
        result_format='message'
    )

    if response.status_code == HTTPStatus.OK:
        raw_content = response.output.choices[0]['message']['content']
        # 清洗 JSON 标记
        clean_json = raw_content.replace("```json", "").replace("```", "").strip()
        try:
            return ResumeEvaluation.parse_raw(clean_json)
        except Exception as e:
            return f"❌ 解析 JSON 失败: {e}\n原文: {raw_content}"
    else:
        return f"❌ API 调用失败: {response.message}"

# --- Main ---
if __name__ == "__main__":
    job_req = "Python 开发工程师：3年以上经验，熟悉 Django/FastAPI，了解大模型。本科以上学历。"
    
    candidate_resume = """
    王小明，拥有 4 年 Python 工作经验。曾在某大厂负责后台开发，精通 FastAPI 和 PostgreSQL。
    最近一年在自研大模型 RAG 应用，对 Prompt Engineering 有深入理解。大专毕业。
    """
    
    report = evaluate_resume(candidate_resume, job_req)
    
    if isinstance(report, ResumeEvaluation):
        print("\n" + "="*40)
        print(f"📄 候选人评估报告：{report.candidate_name}")
        print(f"💯 总评分: {report.total_score}")
        print("-" * 20)
        print("🛠️ 技能对标分析：")
        for match in report.skill_analysis:
            status = "✅" if match.matched else "❌"
            print(f"  {status} {match.skill_name}: {match.comments}")
        print("-" * 20)
        print(f"📝 总结报告: \n{report.summary}")
        print("="*40)
    else:
        print(report)
```

---

## 💡 老师的建议 (必看)
1. **真实场景优化**：真实的简历往往很乱，有很多特殊字符。建议在解析前使用 Python 的 `strip()` 和 `replace('\n', ' ')` 进行简单的预处理。
2. **处理“大专” vs “本科”**：AI 有时会根据具体情况调整评分，例如虽然学历不符但经验非常匹配。你可以在 Prompt 中加入强制规则：`"如果学历不符合职位要求的本科，总评分必须扣除 20 分。"`
3. **安全隐私**：不要直接将包含真实身份证号或手机号的简历发给公网 API，实际开发中需要进行脱敏处理。

---

## 📝 本日练习
1. 修改 `ResumeEvaluation` 模型，增加一个 `expected_salary_assessment` (薪资预期评估) 字段。
2. 尝试输入一份完全不匹配的简历（比如厨师），看看 AI 的打分和分析是否准确。
3. 思考：如果这个系统要同时处理 100 份简历，你应该如何利用 Day 19 学过的 **asyncio** 来加速？
    