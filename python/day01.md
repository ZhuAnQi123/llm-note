

# TS vs Python 核心数据结构对齐指南

### 🎯 今日目标
彻底理清 TypeScript 的 `Array/Object` 与 Python 的 `List/Dict/Set/Tuple` 之间的双向映射，掌握 Pythonic 的数据操作 API。

---

### 🧩 核心概念对齐图谱（一眼看懂）

| TypeScript 概念与写法 | Python 对应数据结构 | 核心特征与区别 |
| :--- | :--- | :--- |
| **Array** `[1, 2, 3]` | **List（列表）** `[1, 2, 3]` | **完全等价**。可变、有序，支持追加、删除和索引。 |
| **Object** `{ name: "Sophie" }` | **Dict（字典）** `{"name": "Sophie"}` | **基本等价**。键值对存储，但 Python 中**键（Key）必须是用引号包裹的字符串或可哈希对象**，且不能像 TS 那样用 `.name` 访问，必须用 `['name']`。 |
| **ReadOnly Array** `readonly number[]` | **Tuple（元组）** `(1, 2, 3)` | **Python 特有**。一旦创建**不可修改**（Immutable），通常用于函数返回多个值或表示固定的记录。 |
| **Set** `new Set([1, 2])` | **Set（集合）** `{1, 2}` | **完全等价**。无序、不重复。Python 提供了极强的集合交集 `&`、并集 `\|` 等数学运算符。 |

---

### 📘 核心对比与避坑指南

#### 1. Array ➡️ List（列表）
Python 的 List 就是 TS 的 Array。
*   **TS 写法**：
    ```typescript
    const list = [1, 2, 3];
    list.push(4);             // 尾部追加
    const length = list.length; // 获取长度
    ```
*   **Python 写法**：
    ```python
    my_list = [1, 2, 3]
    my_list.append(4)         # 尾部追加用 append，不是 push
    length = len(my_list)     # 获取长度用内置函数 len()
    ```
*   **💡 黄金特性（切片 Slice）**：Python 支持极其优雅的切片操作，比如 `my_list[1:3]` 获取子列表，`my_list[::-1]` 快速反转列表。这在 TS 中需要写复杂的 `.slice()`。

#### 2. Object ➡️ Dict（字典）
这是最容易混淆的地方。TS 的 Object 既是“键值对容器”，又是“类实例的基类”；而 Python 的 Dict **纯粹是键值对容器**。
*   **TS 写法**：
    ```typescript
    const user = { name: "Sophie", age: 25 };
    console.log(user.name); // 支持点号（.）访问
    ```
*   **Python 写法**：
    ```python
    user = {"name": "Sophie", "age": 25} # 注意：Key 必须加引号
    print(user["name"])      # 必须用中括号访问！
    # print(user.name)       # ❌ 报错！Dict 不支持点号访问（除非用 Pydantic 或 Class）
    ```
*   **⚠️ 避坑**：在 Python 中访问不存在的键（如 `user["gender"]`）会直接抛出 `KeyError` 导致程序崩溃。
    *   **安全取值**：使用 `user.get("gender", "default_value")`，如果不存在会返回默认值，不会崩溃（类似于 TS 的可选链 `user?.gender`）。

#### 3. 🚨 Python 特有：Tuple（元组） vs List
在 TS 中，元组只是数组的一种类型标注（如 `[string, number]`）。但在 Python 中，元组 `(a, b)` 是一个**独立的内置类型**。
*   **区别**：List 是可变的（Mutable），Tuple 是不可变的（Immutable）。
*   **TS 写法**：
    ```typescript
    function getCoords(): [number, number] { return [10, 20]; }
    const [x, y] = getCoords();
    ```
*   **Python 写法**：
    ```python
    def get_coords():
        return (10, 20) # 返回元组
    
    x, y = get_coords() # 自动解包（Unpacking）
    ```

---

### 🛠️ 今日练习任务（动手消除混淆）

请在你的 Python 开发环境中，尝试手写以下一段转换代码：

1.  **List 操作**：创建一个包含 1 到 10 的列表，使用切片获取后 3 个元素，再用 `len()` 打印列表长度。
    ```py
    list_10=range(1,11)
    print(len(list_10[-3:]))
    ```
2.  **Dict 安全操作**：创建一个字典存放你的个人配置，尝试使用 `.get()` 方法去读取一个不存在的配置项，并设置默认值为 `"Vibe-Motion"`。
    ```py
    config={}
    project=config.get("project","Vibe-Motion")
    ```

---

### 📚 学习资料
*   [Real Python: Python Lists and Tuples (基础与切片用法)](https://realpython.com/python-lists-tuples/)
*   [Real Python: Python Dictionaries (字典的核心 API 与安全取值)](https://realpython.com/python-dicts/)