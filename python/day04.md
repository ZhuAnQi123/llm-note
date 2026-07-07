# Day 4：数据验证与实体类（TS `Zod` ➡️ Python `Pydantic`）

## 🎯 今日目标\*\*

使用 **Pydantic**在数据边界（如 API 输入、配置文件）进行类型安全的运行时数据校验。

- **💡 核心映射**：
  - 使用 Pydantic 定义 `BaseModel`，你可以自动实现输入数据验证、类型转换（如字符串转数字）、序列化。
  - 如果只需纯数据结构而无需校验，使用 Python 原生 `@dataclass`（类似于轻量 TS 接口）。
- **📚 学习资料**：
  - [Pydantic 官方快速开始指南](https://docs.pydantic.dev/latest/)
  - [Real Python: Python Dataclasses 详解](https://realpython.com/python-data-classes/)

## 学习笔记📒

### BaseModel & Field
```py
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class PersonalInfo(BaseModel):
    name: str
    gender: Literal["M","F"]

class Loan(BaseModel):
    #  forzen=true -- 固定值不允许修改
    loanId:str= Field(forzen=true) 
    # default_factory -- 动态默认值
    createTime = Field(default_factory=datetime.now)
    # alias -- 别名,限制最小值(greater then 0)
    loanTenor:int = Field(..., alias='tenor', gt=0)
    # 字符串长度限制
    phoneNmber:str = Field(max_length:12, min_length:8)
    # Optional -- 选填
    promotionCode: Optional[str] = None
    # 嵌套类型--【注意有前后顺序差别】
    personalInfo: PersonalInfo

    # field_validator 装饰器校验phoneNmber不能够包含字符'-'
    @field_validator("phoneNmber")
    @classmethod
    def PhoneNumberValidation(cls, v)-> str:
        if "-" in v:
            raise ValueError("phoneNmber包含有特殊字符")
        # 【‼️】这要把校验通过的字符串返回
        return v




try:
    p_loan=Loan(promotionCode='300129')
except ValidationError as e:
    print(e.json()) # ❌loanId，loanTenor必填字段没有传入
```

### `model_dump` <-> `model_dump_json` JSON & Dict相互 转换
```py
# 这个时候是普通的python字典
data = {"id": 1, "name": "sophie"}

# 1. model_validate 会做数据清洗和类型转换
user = User.model_validate(data)

# 2. 导出为 字典(Dict)
user_dict = user.model_dump()
# 导出时排除未设置的默认值（只导出用户手动填写的字段）
user_dict_exclude = user.model_dump(exclude_unset=True)

# 3. 导出为 JSON 字符串
user_json = user.model_dump_json()
```

### 配置项类 Settings
```py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 1. 定义你想读取的变量，与`.env`中的类型要对得上。
    # Pydantic 会自动去环境变量或 .env 里找不区分大小写的同名键
    # 在这里假设`.env`中有 `ENV` `API_KEY`
    env: str
    api_key: str

    # 2. 关键配置：告诉 Pydantic 去哪里读取文件
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# 3. 实际使用：直接实例化，不需要传任何参数！
settings = Settings()

# 4. 怎么取？直接像点属性一样取出来用：
print(settings.env)      # 输出: dev (自动变成小写属性，但对应 .env 里的 ENV)
print(settings.api_key)  # 输出: my_secret_key_123
```
