
# Day 6：Web 生态与 AI 接入（TS `NestJS` ➡️ Python `FastAPI`）
##   🎯 目标：学习现代 Python 最流行的 Web 框架，接入大模型或外部 API 生态。
*   **📚 学习资料**：
    *   [FastAPI 官方基础教程](https://fastapi.tiangolo.com/tutorial/)
    *   [Google GenAI SDK (Python) 接入指南](https://github.com/google/generative-ai-python) —— 目前主流的 AI SDK 都是将 Python 作为一等公民。

## 学习笔记


FastAPI 的核心哲学是：**利用 Python 的 Type Hints（类型提示）+ Pydantic，同时实现「类型安全」、「数据校验」和「自动文档生成」**。

---

### 1. 基础架构与核心概念映射

| 概念 | NestJS 对应 | FastAPI 实现方式 |
| --- | --- | --- |
| **应用实例** | `NestFactory.create(AppModule)` | `app = FastAPI()` |
| **控制器/路由** | `@Controller('users')`, `@Get(':id')` | `@app.get("/users/{id}")` (装饰器) |
| **DTO (数据传输对象)** | `class CreateUserDto` (+ `class-validator`) | `class UserCreate(BaseModel)` (Pydantic 模型的子类) |
| **依赖注入 (DI)** | `@Injectable()`, `constructor(private service)` | `Depends(dependency_function)` |
| **异步处理** | `async/await` (基于 RxJS 或 Promise) | `async def` (基于 Python 原生 asyncio) |

---

### 2. 必须掌握的 5 大核心知识点

#### 知识点 ①：基础路由与异步请求

FastAPI 原生支持异步。如果你的接口需要调用外部 AI API 或读写数据库，建议使用 `async def`。

```python
from fastapi import FastAPI

app = FastAPI()

# 根路由
@app.get("/")
async def read_root():
    return {"message": "Hello FastAPI from NestJS developer!"}

```

💡 **提示**：启动服务器使用 `uvicorn main:app --reload`（类似于 `npm run start:dev`）。

#### 知识点 ②：路径参数与查询参数 (Path & Query Parameters)

FastAPI 会自动根据函数参数的类型限制输入，并生成文档。

```python
from typing import Optional

@app.get("/items/{item_id}")  # item_id 是路径参数
async def read_item(item_id: int, q: Optional[str] = None):  # q 没有在路径中，自动识别为查询参数
    return {"item_id": item_id, "query_param": q}

```

* 如果访问 `/items/abc`，由于 `item_id` 限制了 `int`，FastAPI 会自动返回 `422 Unprocessable Entity` 错误，无需手动校验。

#### 知识点 ③：使用 Pydantic 进行数据校验 (类似于 NestJS DTO)

这是 FastAPI 的灵魂。通过定义一个继承自 `BaseModel` 的类，你就可以定义请求体的结构。

```python
from pydantic import BaseModel, Field

# 定义 DTO
class ChatRequest(BaseModel):
    model: str = Field(default="gemini-1.5-flash", description="使用的模型名称")
    prompt: str = Field(..., min_length=1, description="用户输入的提示词")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

@app.post("/v1/chat")
async def create_chat_completion(request: ChatRequest):
    # 此时 request 已经是解析并校验完毕的 Python 对象，支持 IDE 智能提示
    return {"status": "success", "received_model": request.model}

```

#### 知识点 ④：依赖注入 (Dependency Injection)

NestJS 的依赖注入非常强大，而 FastAPI 的依赖注入则极其简洁，使用 `Depends` 函数实现。常用于：数据库连接、认证、获取 AI SDK 客户端。

```python
from fastapi import Depends

# 1. 定义一个依赖项（可以是普通函数或类）
async def get_api_key():
    # 这里可以写从 Header 获取 Token 或验证的逻辑
    return "secret_gemini_api_key"

# 2. 在路由中注入
@app.post("/ai/generate")
async def generate_text(prompt: str, api_key: str = Depends(get_api_key)):
    return {"prompt": prompt, "used_key": api_key}

```

#### 知识点 ⑤：自动文档 (Swagger UI)

你不需要像 NestJS 那样配置 `@nestjs/swagger` 模块。

* 只要启动服务，访问 **`/docs`** 即可看到自动生成的交互式 Swagger UI。
* 访问 **`/redoc`** 可以看到 ReDoc 格式的文档。
你在 Pydantic 中写的 `Field(description="...")` 会直接变成文档里的字段说明。

---

### 3. 今日实战：接入 Google GenAI SDK (Gemini)

结合今日目标，这是一个将 FastAPI 与 Google GenAI SDK 结合的完整精简示例：

#### 1. 安装依赖

```bash
pip install fastapi uvicorn google-genai pydantic-settings

```

#### 2. 代码实现 (`main.py`)

```python
import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(title="AI API 网关")

# 模拟 NestJS 中的 Service 初始化（这里通过依赖注入提供客户端）
def get_ai_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY 未配置")
    return genai.Client(api_key=api_key)

# 定义输入 DTO
class GenerationPayload(BaseModel):
    prompt: str
    model_name: str = "gemini-2.5-flash"

@app.post("/api/v1/generate")
async def generate_content(
    payload: GenerationPayload, 
    client: genai.Client = Depends(get_ai_client)  # 注入 AI 客户端
):
    try:
        # 调用 Google GenAI SDK (支持异步操作，建议在生产中使用 client.aio)
        response = client.models.generate_content(
            model=payload.model_name,
            contents=payload.prompt,
        )
        return {
            "success": True,
            "text": response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

```

---

### 💡 过来人小贴士（给 NestJS 开发者的建议）

1. **没有强制的目录结构**：FastAPI 不像 NestJS 那样强制你用 `*.module.ts`, `*.controller.ts`。你可以把所有东西写在一个 `main.py` 里。但在大项目中，通常会使用 `APIRouter`（类似于 NestJS 的路由模块化）来拆分文件。
2. **中间件 (Middleware)**：FastAPI 的中间件和 NestJS / Express 中间件极其类似，处理跨域（CORS）时非常方便：
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)

```


3. **全局异常处理**：NestJS 使用 `Exception Filters`，FastAPI 使用 `@app.exception_handler(HTTPException)` 装饰器来捕获并格式化全局错误。
