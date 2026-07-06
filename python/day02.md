
# Day 2：核心语法与 "Pythonic" 编程
## 目标
*   **🎯 今日目标**：掌握 Python 特有的优雅表达，避免写出“带括号和花括号的 TS 风格 Python”。
*   **💡 核心映射**：
    *   **数组/对象操作**：TS 的 `.map().filter()` ➡️ Python 的 **列表推导式 (List Comprehension)**，例如 `[x * 2 for x in items if x > 5]`。
    *   **对象/解构**：TS 的 `{ a, ...rest }` ➡️ Python 的 `a, *rest = tuple_data` 或 `**kwargs`（双星号解包）。
    *   **分支控制**：TS 的 `switch(val)` ➡️ Python 3.10+ 的强力模式匹配 `match val:`。
*   **📚 学习资料**：
    *   [Real Python: Python List Comprehensions](https://realpython.com/list-comprehension-python/)
    *   [Python 3.10 Match-Case 模式匹配教程](https://learnpython.com/blog/python-match-case-statement/)

## 已完成 
