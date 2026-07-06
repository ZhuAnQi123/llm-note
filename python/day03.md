# Day 3：类型系统（TS `interface` ➡️ Python `typing`）
## 学习计划
*   **🎯 今日目标**：利用 PEP 484 类型提示（Type Hints）写出高维护性的强类型 Python。
*   **💡 核心映射**：
    *   **静态类型**：Python 的类型提示完全是**静态的**（仅供 IDE 在开发的时候类型检查），运行时会被解释器忽略。
    *   **鸭子类型（Duck-typing）**：TS 开发者最爱的隐式接口（只要结构对就契合）在 Python 中通过 `typing.Protocol` (PEP 544) 完美对应。
*   **📚 学习资料**：
    *   [Type-Safe Python for TypeScript Developers (Atomic Spin)](https://spin.atomicobject.com/type-safe-python/)
    *   [mypy 官方类型提示速查表](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)

## 学习成果
几种常用的python type

### 固定类型Final--意义相当于ts的const
```py
from typing import Final
ENV_VAR:Final = 'sit-ww111'
ENV_VAR='aaa' #"ENV_VAR" is declared as Final and cannot be reassigned
```

### 联合类型Literal--相当于ts的 ｜
```py
from typing import Literal

LoanStatus=Literal["penging","disbursed","doc_uploaded"]
```

### Never
* 如果一个函数的返回值类型是 `Never`，意味着这个函数永远不会正常返回（比如它总是抛出异常，或者是个死循环）。

* 如果一个变量的类型变成了 `Never`，意味着在正常的逻辑下，绝对没有任何值能走到这一步。

### NamedTuple 用于一个函数以元祖的形式返回多个值
```py
from typing import NameTuple
class Student(NameTuple):
    name: str
    age:int
    gender:str

def getStudentById(id:int)->Student:
    # ....
    return Student(
        name: 'mock',
        age:1,
        gender:"F"
    )
```


### TypeDict 定义**字典**键值对类型[👀常见👀]
```py
from typing import TypeDict
class LoanInfo(TypeDict):
    loanId:str
    curstomerId:str
    loanAmount:int
    address:NotRequired[str]

# 构造函数调用
loan=LoanInfo(
    loanId='Pf100'
    loanAmount=1000
    # ❌ 类型检查器报错: 缺少必需的键 "curstomerId"
)

# 字面量调用
loan:LoanInfo= {
    loanId:'Pf100'
    loanAmount:1000
    curstomerId:'c10999'
}

print(loan["loanId"]) # ✅ 中括号语法取值
applicationId=loan.loanId # ❌ # ❌ 错误！字典没有这个属性
```

### Protocol 定义对象（Object/Class 实例）的类型
与`TypeDict`的区别：
1. `TypeDict`定义的对象用中括号拿值
2. `Protocol`定义的实例用点语法拿值
```py
from typing import Protocol

class LoanInfo(Protocol):
    loanId:num
    applicationId:string

class Loan():
    def __init__(self,loanId,applicationId):
        self.loanId = loanId
        self.applicationId = applicationId


loan:LoanInfo=Loan(1,'001')
print(loan.loanId) # 调用正确
```

### Pydantic BaseModal
上面我们的Protocol是在写代码的时候进行静态检查，而Pydantic中的BaseModal是强约束的。 
也就是说数据类型不符合的时候会先尝试转换（比如说期待收到的是number，传入的是string）。 
数据规则不匹配的时候会直接报typeerror（比如说限制max_length为4而收到的长度5位）    
适合用在api的入参出参

```py
from typing import Literal
from pydantic import BaseModel, Field

class CreditCardPayment(BaseModel):
    type: Literal['creditCard']
    merchant: Literal["VISA", "PAYPAL", "MASTER"]
    #参数用等号 =
    cardNum: str = Field(..., max_length=10, min_length=5) 

class CashPayment(BaseModel):
    type: Literal['cash']

# 使用 | 符号定义联合类型（辨识联合）
PaymentMethod = CreditCardPayment | CashPayment

class PaymentRequest(BaseModel):
    amount: int
    # 嵌套模型，并使用 discriminator 智能分流不同类型的子模型。
    method: PaymentMethod = Field(discriminator="type")
```