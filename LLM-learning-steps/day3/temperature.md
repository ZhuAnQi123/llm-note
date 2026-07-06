
## 2. Temperature 和 Max Tokens 详解

### Temperature（温度：0~2）
控制**创造性 vs 确定性**

| Temperature | 效果 | 适用场景 |
|------------|------|---------|
| 0 | 最保守，每次都选概率最高的词 | 数学题、代码生成、事实问答 |
| 0.3-0.5 | 轻微随机，较稳定 | 客服、面试官（保持一致性） |
| 0.7-0.9 | 有创意，多样化 | 文案创作、头脑风暴 |
| 1.5+ | 很随机，可能逻辑混乱 | 诗歌、创意写作（慎用） |

**面试官建议：0.3-0.5**（既要专业，又不能太死板）

### Max Tokens（最大输出长度）
- **1 token ≈ 0.75 个英文单词 或 0.5 个中文字**
- 控制AI回答的最大长度
- 注意：是**输出**长度，不是输入

```python
# 示例
max_tokens=150  # 约75个中文字，适合简短回答
max_tokens=500  # 约250个中文字，适合详细评价
max_tokens=2000 # 长回答，但会消耗更多tokens（钱）
```

**面试官建议：300-500**（问题+追问+评分）

---



这是**有状态评估**问题，不能只靠单次API调用。需要**结构化输出 + 累积评分**。

### 方案架构

```python
import openai
import json

class AIInterviewer:
    def __init__(self):
        self.conversation_history = []
        self.scores = {
            "technical": [],      # 技术分列表
            "communication": [],  # 沟通分列表
            "problem_solving": [] # 解题分列表
        }
        
    def ask_question(self, question, expected_keywords=None):
        """提出问题，并记录期望答案关键词"""
        self.conversation_history.append({
            "role": "assistant",
            "content": question
        })
        # 保存这个问题期望的关键词
        self.current_expected = expected_keywords
        
    def evaluate_answer(self, user_answer):
        """评估用户回答，返回分数和理由"""
        
        evaluation_prompt = f"""
你是面试官，请评估候选人的回答。

【问题】：{self.conversation_history[-1]['content']}

【候选人的回答】：{user_answer}

【期望包含的关键词】：{self.current_expected}

请按以下JSON格式输出评估结果：
{{
    "score": 0-10的整数分数,
    "technical_accuracy": 1-5分（技术准确性）,
    "clarity": 1-5分（表达清晰度）,
    "depth": 1-5分（思考深度）,
    "feedback": "简短评语",
    "missing_points": ["缺失的关键点1", "缺失的关键点2"],
    "should_pass": true/false（这道题是否通过）
}}
"""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是严格的技术面试官，请客观评估。输出必须是JSON格式。"},
                {"role": "user", "content": evaluation_prompt}
            ],
            temperature=0.3,  # 低温度保证评分稳定
            max_tokens=500
        )
        
        result = json.loads(response.choices[0].message["content"])
        
        # 记录分数
        self.scores["technical"].append(result["technical_accuracy"])
        self.scores["clarity"].append(result["clarity"])
        self.scores["problem_solving"].append(result["depth"])
        
        return result
    
    def final_decision(self):
        """所有问题结束后，做出最终录取决定"""
        
        # 计算平均分
        avg_scores = {
            k: sum(v)/len(v) if v else 0 
            for k, v in self.scores.items()
        }
        total_avg = sum(avg_scores.values()) / 3 * 2  # 满分10分
        
        # 让AI做最终判断
        final_prompt = f"""
基于以下面试数据，决定是否录取候选人：

技术能力平均分：{avg_scores['technical']}/5
沟通能力平均分：{avg_scores['clarity']}/5
问题解决能力：{avg_scores['problem_solving']}/5
综合得分：{total_avg}/10

请输出JSON：
{{
    "hire": true/false,
    "confidence": 0-100,
    "reason": "详细理由",
    "strengths": ["优点1", "优点2"],
    "weaknesses": ["缺点1", "缺点2"],
    "suggestion": "给候选人的建议"
}}
"""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是HR总监，基于数据做招聘决策"},
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.2,
            max_tokens=500
        )
        
        return json.loads(response.choices[0].message["content"])

# 使用示例
interviewer = AIInterviewer()

# 第一轮面试
interviewer.ask_question(
    "解释一下Python的GIL是什么？有什么影响？",
    expected_keywords=["全局解释器锁", "多线程", "CPU密集型", "IO密集型"]
)
user_answer = "GIL是全局解释器锁，它导致Python多线程不能并行执行CPU任务..."
result = interviewer.evaluate_answer(user_answer)
print(f"这道题得分：{result['score']}/10")
print(f"是否通过：{result['should_pass']}")

# ... 继续3-5个问题 ...

# 最终决定
decision = interviewer.final_decision()
print(f"\n录取决定：{'✅ 录取' if decision['hire'] else '❌ 不录取'}")
print(f"理由：{decision['reason']}")
```

### 关键技巧

1. **分段评估**：每题独立评分，最后综合
2. **结构化输出**：用JSON让AI返回可计算的分数
3. **期望关键词**：帮助AI客观判断对错
4. **多维度打分**：不只对错，还有表达、深度
5. **低Temperature**：保证评分一致性

### 进阶：让AI自己生成问题并评分

```python
def generate_next_question(self, previous_performance):
    prompt = f"""
根据候选人之前的表现（正确率65%，薄弱点在并发编程），
生成下一道考察并发编程的面试题。
题目要有追问空间，难度中等。
输出JSON：{{"question": "问题", "expected": ["关键词1","关键词2"]}}
"""
    # ... 调用API ...
```

---

### 总结

| 需求 | 解决方案 |
|------|---------|
| 身份设定 | `system` message |
| 控制创造力 | temperature=0.3-0.5（面试官） |
| 控制长度 | max_tokens=300-500 |
| 判断录取 | 多轮累积评分 + 最终综合决策 |

需要我帮你写一个**完整的AI面试官**代码吗？可以支持动态出题、自动评分、最终录取建议。