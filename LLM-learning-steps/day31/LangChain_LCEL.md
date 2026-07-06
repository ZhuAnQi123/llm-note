# Day 31：LangChain 核心组件 - LCEL (Runnable) 与 Chain

## 🎯 学习目标
*   理解什么是 **LangChain**：为什么我们需要一个大模型应用框架？
*   掌握 **LCEL (LangChain Expression Language)**：学习符号 `|` 的管道操作。
*   理解 **PromptTemplate**、**ChatModel** 和 **OutputParser** 的链式组合。
*   学会将 Day 21-30 的琐碎代码整合进一条简洁的“链”中。

---

## 📚 学习资源
*   **LangChain 官方文档 (必读)**: [LCEL Conceptual Guide](https://python.langchain.com/docs/concepts/#langchain-expression-language-lcel)
*   **LangChain Python SDK**: [GitHub Repository](https://github.com/langchain-ai/langchain)
*   **PromptTemplate 教程**: [How to use Prompt Templates](https://python.langchain.com/docs/how_to/#prompt-templates)

---

## 🛠️ 新手必会知识点 (附例子)

### 1. 为什么用 LangChain？
解决原生 LLM 调用的“胶水代码”问题（上下文管理、提示词硬编码、输出解析繁琐）。
### 原生 OpenAI 调用 vs LangChain 方式
| 特性 | 原生代码 (无框架) | LangChain + LCEL |
| :--- | :--- | :--- |
| 提示词修改 | 修改 f-string 或拼接字符串 | 声明 `PromptTemplate`，动态变量分离 |
| 模型切换 | 重写 API 调用 | 换一个 `ChatModel()` 对象即可 |
| 输出处理 | 手动 `.strip()` 或正则提取 | 用 `OutputParser` 自动转字典/Pydantic |
| 多步骤组合 | 嵌套函数，难以调试 | 一条 `\|` 链，可视化/流式输出开箱即用 |

### 2. PromptTemplate (提示词模板)
动态生成 Prompt，不再使用笨拙的字符串拼接。
```python
from langchain_core.prompts import ChatPromptTemplate

template = "你是一个专业的{topic}助手。请回答用户的问题：{question}"
prompt = ChatPromptTemplate.from_template(template)
# 渲染结果：prompt.format(topic="美食", question="怎么做红烧肉？")
```

---

## 🧠 逻辑架构说明 (Mermaid 图示)

```
输入变量 (例如 {"topic": "猫咪"})
    │
    ▼
┌─────────────────────────┐
│   PromptTemplate        │
│   "用中文写一首关于{topic}的诗" │
└─────────────────────────┘
    │
    ▼ (管道符 |)
┌─────────────────────────┐
│   ChatModel (如 GPT-4o) │
│   生成: "绒球轻跳跃..."     │
└─────────────────────────┘
    │
    ▼ (管道符 |)
┌─────────────────────────┐
│   OutputParser          │
│   去除多余空行，返回纯文本   │
└─────────────────────────┘
    │
    ▼
最终输出: str
```

---

## 💻 完整可运行范例：使用 LangChain 重构 AI 翻译助手
由于通义千问官方 SDK 和 LangChain 结合需要安装 `dashscope` 适配器，我们这里使用 LangChain 的通用接口。

```python
# 首先需要安装：pip install -U langchain-community dashscope
import os
from langchain_community.chat_models import ChatDashScope
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# 1. 初始化模型 (确保 DASHSCOPE_API_KEY 已设置)
model = ChatDashScope(model_name="qwen-turbo")

# 2. 定义 Prompt 模板
prompt = ChatPromptTemplate.from_template("你是一个精通{language}的翻译官。请将以下内容翻译成{language}：\n{text}")

# 3. 定义输出解析器
parser = StrOutputParser()

# 4. 构建 LCEL 链 (核心！)
chain = prompt | model | parser

# --- Main ---
if __name__ == "__main__":
    print("⏳ LangChain 正在启动...")
    result = chain.invoke({
        "language": "德语",
        "text": "大模型技术正在飞速发展。"
    })
    
    print(f"\n✨ 翻译结果: \n{result}")
```

---

## 💡 老师的建议 (必看)
1.  **不要过度依赖框架**：LangChain 的更新非常快，经常会有弃用警告（Deprecated Warning）。记住我们 Day 28 手写 RAG 的原理，框架只是为了加速开发。
2.  **LCEL 是灵魂**：`|` 符号让数据流变得透明。左边输出什么，右边就接收什么。只要一个对象有 invoke 方法，就能用 | 串联。LangChain 的所有核心组件都遵守这个约定。

### 📊 对照表：什么对象有 invoke 方法？

| 对象类型 | 是否可 invoke | 示例 |
|:---|:---|:---|
| `ChatPromptTemplate` | ✅ | `prompt.invoke({"key":"value"})` |
| `ChatOpenAI` (任何模型) | ✅ | `model.invoke("你好")` |
| `StrOutputParser` | ✅ | `parser.invoke(aimessage)` |
| `RunnableLambda` (函数包装) | ✅ | `RunnableLambda(len).invoke([1,2,3])` |
| 你自己写的类（有 `invoke` 方法） | ✅ | `MyClass().invoke(x)` |
| 普通 Python 函数 | ❌ | 需要先包装成 `RunnableLambda` |
| 字典 | ❌ | 但可以用 `RunnablePassthrough` 传递 |
| 字符串 | ❌ | 不能在链中直接用 |

3.  **调试工具**：如果链跑不通，可以安装 `langsmith` (LangChain 官方调试平台)，它能清晰展示每一步的输入输出。

---

## 📝 本日练习
1.  修改上面的代码，增加一个 `StructuredOutputParser`，让翻译结果以 JSON 格式返回：`{"original": "...", "translated": "..."}`。
2.  **思考题**：如果我想在翻译前先检查内容是否违规，应该如何在链中增加一个环节？
3.  尝试将两条链组合在一起：链 A 的输出作为链 B 的输入。
    