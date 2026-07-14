# Day 7：实战项目 —— 
*   **🛠️ 今日任务** 编写一个 AI 辅助结构化 API
    1.  用 `poetry init` 新建项目。并通过 `poetry add <package_name>` 安装 `fastapi`, `uvicorn`, `pydantic`。
    2.  编写一个 FastAPI 异步接口，接收用户请求。
    3.  利用 **Pydantic** 对输入的数据结构进行严格校验。
    4.  通过 **asyncio** 异步调用 Gemini API 或其他大模型 API，并将大模型的非结构化文本通过 Pydantic 强制解析成结构化的 JSON 响应。
    5.  用 `uvicorn main:app --reload` 启动，并在浏览器中调试生成的 Swagger 页面。


## 遇到的问题
### 依赖安装

**问题 1：`poetry init` 报错 `returned non-zero exit status 2`**
*   **报错信息**：`Command '['/usr/local/bin/python', '-Ic', '...']' returned non-zero exit status 2.`
*   **原因**：Poetry 尝试调用默认路径下的 Python（例如 `/usr/local/bin/python`）来检测环境，但该路径的 Python 不存在或者是损坏的软链接（在 macOS 上通过 Homebrew 更新 Python 后常遇到）。
*   **解决办法**：在运行 `poetry init` 之前，先手动创建并激活虚拟环境，让 Poetry 直接接管当前正常的 Python 解释器。
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    poetry init
    ```
`poetry init`会生成一个`pyproject.toml`文件相当于fe的 `package.json`


## 产出
```py
import asyncio

from fastapi import FastAPI
from pydantic import BaseModel, Field

# 初始化 FastAPI示例，传入标题、描述和版本信息
app = FastAPI(
    title="AI 结构化解析 API",
    description="Day 7 任务：基于 FastAPI 和 Gemini 的接口",
    version="0.1.0",
)


# ChatRequest 和ChatResponse的Pydantic模型
class ChatRequest(BaseModel):
    """接收用户请求的结构体"""

    message: str = Field(..., description="用户输入的自然语言请求文本", min_length=1)
    session_id: str | None = Field(default=None, description="可选的会话ID")
    user_id: str | None = Field(default=None, description="可选的用户ID")
    web_search: bool = Field(default=False, description="是否启用网络搜索功能")
    use_rag: bool = Field(default=True, description="是否启用RAG功能")


class ChatResponse(BaseModel):
    status: str = Field(default="success", description="接口状态")
    structured_output: dict = Field(..., description="AI 解析后的结构化 JSON 数据")
    raw_output: str = Field(..., description="大模型的原始回复")
    tag: list[str] = Field(default=[], description="大模型回复的标签列表")


# 注册接口，传入response_modal & tags
@app.post("chat", response_model=ChatResponse, tags=["AI 对话与解析"])
async def process_user_message(request: ChatRequest):
    """
    接收用户文本，异步调用大模型进行结构化处理 (Day 7 任务目标)
    """
    # 模拟异步调用大模型 API 耗时
    await asyncio.sleep(1)

    # 构造并返回符合 Pydantic 校验的响应数据
    return ChatResponse(
        status="success",
        structured_output={"message": request.message},
        raw_output=f"（模拟结果）已收到消息：'{request.message}'",
        tag=["模拟标签1", "模拟标签2"],
    )

```
