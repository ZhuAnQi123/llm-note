## OpenAI Structured Output 完全指南

### 一、什么是 Structured Output？

**Structured Output** 是 OpenAI 的一项功能，确保模型生成的输出**完全符合你提供的 JSON Schema**。这意味着你可以获得可预测、格式一致的结构化数据，而无需在后端进行复杂的解析和验证。

### 二、两种输出模式对比

| 特性 | Structured Output (推荐) | JSON Mode (旧版) |
| --- | --- | --- |
| **配置方式** | `{ "type": "json_schema", "json_schema": {...} }` | `{ "type": "json_object" }` |
| **是否遵循 Schema** | ✅ 严格匹配 | ❌ 只保证是合法 JSON |
| **是否需要提示词引导** | 不需要 | ✅ 必须在提示词中包含 "JSON" 关键词 |
| **推荐程度** | ⭐ 首选 | ⚠️ 仅在不支持 json_schema 的模型上使用 |

> **重要提示**：使用 JSON Mode 时，如果不在提示词中引导模型输出 JSON，模型可能会生成无休止的空格直到达到 token 限制。

### 三、核心参数详解

在 API 请求中使用 `response_format` 参数：

```python
response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "你是一个电影信息提取助手，严格按照要求的 JSON Schema 输出。"
        },
        {
            "role": "user",
            "content": "《盗梦空间》是克里斯托弗·诺兰执导的科幻动作片，2010年上映，豆瓣评分9.3。"
        }
    ],
    # 方式1  schema
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "movie_info",      # 给你的 schema 起个名字
            "schema": my_schema,       # 传入下面定义的 schema
            "strict": True  # 可选，默认 True，强制严格匹配
        }
    }
    # 方式2 Pydantic模型
    "json_schema": MovieDetails# 传入下面定义的模型
)

```

### 四、两种主流实现方式

#### 方式一：使用 Pydantic 模型（Python 推荐）

这是最优雅的方式，通过 Pydantic 定义数据结构，让 SDK 自动生成 Schema：

```python
from pydantic import BaseModel, Field
from typing import List, Optional

# 1. 定义你的数据模型
class Date(BaseModel):
    day: int = Field(ge=1, le=31)      # 1-31 的整数
    month: int = Field(ge=1, le=12)    # 1-12 的整数
    year: Optional[int] = Field(ge=1900)  # 可选字段

class MovieDetails(BaseModel):
    title: str
    release_date: Date
    genres: List[str]
    rating: Optional[float] = Field(ge=0, le=10)
```

#### 方式二：直接使用 JSON Schema

如果不想用 Pydantic，可以直接编写 JSON Schema：

根据 OpenAI 官方推荐，编写 Schema 时应注意：

| 配置项                 | 推荐设置 | 说明                           |
| ---------------------- | -------- | ------------------------------ |
| `additionalProperties` | `false`  | 禁止模型添加未定义的字段       |
| `required`             | 明确列出 | 标记所有必须字段               |
| `strict`               | `true`   | 启用严格模式，确保输出完全匹配 |
| `description`          | 添加说明 | 帮助模型理解每个字段的用途     |

```json
my_schema={
  "type": "object",
  "properties": {
    "title": { "type": "string" },
    "release_date": {
      "type": "object",
      "properties": {
        "day": { "type": "integer", "minimum": 1, "maximum": 31 },
        "month": { "type": "integer", "minimum": 1, "maximum": 12 },
        "year": { "type": "integer", "minimum": 1900 }
      },
      "required": ["day", "month"],
      "additionalProperties": false
    },
    "genres": { "type": "array", "items": { "type": "string" } },
    "rating": { "type": "number", "minimum": 0, "maximum": 10 }
  },
  "required": ["title", "release_date", "genres"],
  "additionalProperties": false
}
```

### 五、完整代码示例

```python
import os
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Optional

# 初始化客户端
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 定义数据结构
class MovieInfo(BaseModel):
    title: str = Field(description="电影的中文名称")
    original_title: str = Field(description="电影的原始名称")
    release_year: int = Field(ge=1900, le=2026, description="上映年份")
    director: str = Field(description="导演姓名")
    rating: Optional[float] = Field(ge=0, le=10, description="豆瓣评分，如果没有则为 None")
    genres: List[str] = Field(description="电影类型列表")

# 方法一：使用 parse 方法（推荐，新版 SDK）
response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",  # 需要使用支持 structured output 的模型
    messages=[
        {"role": "system", "content": "你是一个电影信息提取助手。请根据用户描述提取电影信息。"},
        {"role": "user", "content": "《肖申克的救赎》是弗兰克·德拉邦特执导的美国剧情片，1994年上映，豆瓣评分9.7。"}
    ],
    response_format=MovieInfo,
)

# 直接获取结构化对象
movie = response.choices[0].message.parsed
print(f"电影名称：{movie.title}")
print(f"导演：{movie.director}")
print(f"上映年份：{movie.release_year}")
print(f"类型：{movie.genres}")
```

### 七、常见错误处理

```python
from openai import OpenAI
import json

def safe_structured_call(prompt, response_format):
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format=response_format,
        )
        return response.choices[0].message.parsed
    except Exception as e:
        print(f"结构化输出失败：{e}")
        # 降级方案：使用普通 JSON 模式
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "以 JSON 格式输出。"},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
```

### 八、模型兼容性说明

| 模型系列              | 支持 Structured Output | 支持 JSON Mode |
| --------------------- | ---------------------- | -------------- |
| GPT-4o / GPT-4o-mini  | ✅ 完全支持            | ✅ 支持        |
| GPT-4 Turbo           | ✅ 支持                | ✅ 支持        |
| GPT-3.5 Turbo (1106+) | ⚠️ 部分支持            | ✅ 支持        |
| 更早的模型            | ❌ 不支持              | ❌ 不支持      |

> **建议**：使用 `gpt-4o-mini` 或更高版本以获得最佳的结构化输出体验。

### 总结

1. **优先使用 Structured Output** + Pydantic 模型
2. **设置 `additionalProperties: false`** 确保输出格式严格
3. **使用 `client.beta.chat.completions.parse()`** 方法自动解析
4. **添加 `description`** 帮助模型理解字段含义
5. **做好错误处理**，在必要时降级到 JSON Mode
