# Day 2：核心语法与 "Pythonic" 编程

## 目标
*   **🎯 今日目标**：掌握 Python 特有的优雅表达，避免写出“带括号和花括号的 TS 风格 Python”。
*   **💡 核心映射**：
    *   **数组/对象操作**：TS 的 `.map().filter()` ➡️ Python 的 **列表推导式 (List Comprehension)**，例如 `[x * 2 for x in items if x > 5]`。
    *   **对象/解构**：TS 的 `{ a, ...rest }` ➡️ Python 的 `a, *rest = tuple_data` 或 `**kwargs`（双星号解包）。
    *   **match 条件判断**：TS 的 `switch(val)` ➡️ Python 3.10+ 的强力模式匹配 `match val:`。
    *   元祖和列表的差别
*   **📚 学习资料**：
    *   [Real Python: Python List Comprehensions](https://realpython.com/list-comprehension-python/)
    *   [Python 3.10 Match-Case 模式匹配教程](https://learnpython.com/blog/python-match-case-statement/)


## 成果

### 列表推导式
对一个列表进行循环计算三种方法：for循环，map循环，列表推导式
```python
# 要求返回 squre_list 平方
list=[1,3,5,7,9,2]


# for 循环做法
squre_list=[]
for num in list:
    squre_list.append(num * num)

# map
def squreFun(num):
    return num*num
list.map(squreFun,list)

# 推导式列表
# [推导函数 for i in 列表] 全程没有逗号
squre=[num*num for num in list]

# 高级点，带有条件语句的列表推导式
squre_singular=[num*num for num in list if num%2!=0]

# 这个条件语句也可以放在前面的推导式那里,把条件作为推导函数一部份
squre_evenNum=[num*num if num%2==0 else num for num in list]
```

### 对象/解构 -- 星号 `*` 和双星号 `**`

在 Python 中，星号 `*` 和双星号 `**` 是处理容器（列表、元组、字典）的“手术刀”，它们能把数据拆解（Unpacking）**成单个元素，或者把多个元素**打包（Packing）在一起。

你可以把它们理解为“解压工具”。

---

### 1. 单星号 `*`：处理序列（列表、元组）

#### A. 打包（Packing）：把多个值归纳为一个变量

当你不知道函数会接收多少参数，或者想把列表剩余的部分存起来时，用 `*`。

```python
# 示例：变量赋值时的打包
a, *rest = [1, 2, 3, 4, 5]
print(a)     # 1
print(rest)  # [2, 3, 4, 5]  <-- 剩下的全被打包进列表了

```

#### B. 解包（Unpacking）：把列表/元组拆开填入函数

当你有一个列表，但函数要求传入一个个独立的参数时，用 `*`。

```python
def add(x, y, z):
    return x + y + z

nums = [1, 2, 3]
# 如果直接传 nums，函数会报错说缺少参数
# 使用 *nums，相当于把 nums 拆成了 add(1, 2, 3)
print(add(*nums)) 

```

---

### 2. 双星号 `**`：处理字典（键值对Dict）

#### A. 打包（Packing）：函数接收`key=value` 形式的参数

当你想让函数支持任意数量的 `key=value` 形式的参数时，用 `kwargs`。

```python
def print_user_info(**kwargs):
    # kwargs 在函数内部是一个字典
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_user_info(name="Sophie", age=25, city="Singapore")
# 输出:
# name: Sophie
# age: 25
# city: Singapore

```

#### B. 解包（Unpacking）：把字典变成函数的参数

如果你的字典键名正好和函数的参数名对应，可以直接用 `` 传递。

```python
def create_profile(name, age):
    print(f"Name: {name}, Age: {age}")

data = {"name": "Sophie", "age": 25}
# **data 相当于写了 create_profile(name="Sophie", age=25)
create_profile(**data)

```

---

### 元组 `( )`&列表 `[ ]` 

在 Python 中，圆括号 `()` 和中括号 `[]` 的最主要区别在于它们的**可变性（Mutability）**和**语义暗示**。

#### 1. 核心区别：可变性 (Mutability)


* **元组 `( )` 是不可变的 (Immutable)：**
一旦创建，里面的内容就不能修改、添加或删除。是**固定长度且具有特定意义**的组合（如坐标、RGB 颜色值、配置项）
```python
t = (1, 2)
# t[0] = 3  # 这会报错 TypeError!

```

* **列表 `[ ]` 是可变的 (Mutable)：**
你可以随时增加、删除或修改其中的元素。
```python
l = [1, 2]
l[0] = 3   # 成功！现在的列表是 [3, 2]

```

---

#### 2. 语义上的倾向

除了技术上的可变性，Python 开发者通常会根据用途选择不同的括号：

| 特性 | 圆括号 `( )` - 元组 | 中括号 `[ ]` - 列表 |
| --- | --- | --- |
| **存储内容** | 通常用于存储**不同类型**或**有特定结构**的数据（如坐标 `(x, y, z)`）。 | 通常用于存储**相同类型**或**动态增长**的数据（如 `[score1, score2, score3]`）。 |
| **性能** | 占内存略小，访问速度略快。 | 因为需要预留扩容空间，略重一些。 |
| **安全性** | 更加安全，可以作为字典的 Key（因为不可变）。 | 不可作为字典的 Key。 |

---

### match 条件判断
**适合**：case 后面接常量、序列、映射或类实例。不接表达式，只负责比较和解构
```py
string="i love you sophie"

match string:
    case 'i love you sophie':
        print("sophie")
    case 'i love you nicole':
        print("nicole")
    case other:
        print('other')
```