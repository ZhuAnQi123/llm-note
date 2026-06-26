# Step 01：用 Python 创建 Qwen 后端 API（Day 1）

日期：2026-06-05  
阶段：阶段 2 - 接入真实大模型  
模型供应商：Qwen  
后端语言：Python  
目标：先让后端在本地打通 Qwen API，不接前端、不做 streaming。

---

## 1. 今天的学习目标

【相关知识点】

- **前后端分离与 Monorepo（单体仓库）**：在真实公司中，前端和后端通常是分离的。大公司可能会把它们放在不同的代码仓库（Polyrepo），但现在非常流行 **Monorepo（单体仓库）**，即前端 `src/` 和后端 `server/` 放在同一个项目里。这样做的好处是：接口定义可以共享，全栈开发体验极佳。
- **为什么 LLM 后端首选 Python**：在工业界，90% 以上的 AI/LLM 后端都是用 Python 写的。因为 OpenAI SDK、LangChain、向量数据库客户端、数据清洗工具等最完善的生态都在 Python 里。前端用 TypeScript/React，后端用 Python/FastAPI，是目前 AI 应用最标准的“黄金搭档”。
- **API 接口与数据模型（Schemas）**：在公司开发中，我们不会随便传 JSON，而是会先定义“数据模型”。在 Python (FastAPI) 中，我们使用 `Pydantic` 库来约束入参和出参的类型。

---

## 2. 工业级项目架构设计（Day 1 简化版）

为了贴近真实开发，我们不在 `main.py` 里写几千行代码，而是做一点基础的分层。你的 `server/` 目录接下来会按这个结构演进：

```text
server/
  main.py          # 程序的入口，只负责启动和注册路由
  schemas.py       # 数据模型（Pydantic Models），定义入参和出参的格式
  requirements.txt # 依赖包清单
```

在更复杂的公司项目中，还会拆分出 `routes/` (路由层)、`services/` (业务逻辑层)、`core/` (配置层)。但对于 Day 1，`main.py` + `schemas.py` 是最完美的平衡：既规范，又不至于过度设计。

---

## 3. 今天的实操任务

今天只理解并实现一件事：

```text
curl / Postman
  -> 你的 Python 后端 /api/chat
  -> Qwen API
  -> Python 后端返回模型回答
```

今天先不要改 `HeroSection.tsx`，也不要做 streaming。  
原因：新手最容易在“前端状态 + 后端请求 + 模型 API + 流式输出”里同时卡住。Day 1 先把后端链路跑通。

你今天要能解释清楚：

- 为什么 Qwen API Key 不能放到 React 里
- Python 后端在这里承担什么角色
- 什么是 `messages`
- `system` 和 `user` 分别是什么
- 为什么要先用 curl 测试后端

---

## 5. Day 1 建议创建的文件

今天你可以创建这些文件：

```text
server/
  main.py
  schemas.py
  requirements.txt

.env
.env.example
```

说明：

- `server/main.py`：Python 后端入口
- `server/schemas.py`：定义 API 的入参和出参类型
- `server/requirements.txt`：Python 依赖列表
- `.env`：真实 Qwen API Key，只放本地
- `.env.example`：示例环境变量，可以提交，不放真实 key

注意：你的 `.gitignore` 已经忽略 `.env` 和 `.env.*`，但保留 `!.env.example`，所以真实 key 不会被提交。

---

## 6. 你应该先安装什么

建议 Day 1 使用 FastAPI，因为它写 API 清晰，后续升级 streaming 也方便。

`server/requirements.txt` 里先考虑这些依赖：

```txt
fastapi
uvicorn
pydantic
python-dotenv
openai
```

为什么使用 `openai` 包？

Qwen / DashScope 通常提供 OpenAI-compatible 的调用方式。这样你可以用统一的 `client.chat.completions.create(...)` 方式学习 `messages`，以后换 OpenAI / DeepSeek 也更容易迁移。

---

## 8. Day 1 的最小 API 设计

你的后端先只需要一个接口：

```text
POST /api/chat
```

前端/测试工具传入：

```json
{
  "message": "介绍一下 Sophie Zhu 的技术栈"
}
```

后端返回：

```json
{
  "reply": "模型返回的文本"
}
```

先不要做复杂的 `messages[]` 入参。  
Day 1 可以让后端内部组装：

```text
system message:
你是 Sophie Zhu / 朱安琪个人网站里的 AI 交互分身。回答要专业、简洁、诚实。不了解的信息要说不知道，不要编造。

user message:
用户传入的 message
```

---

## 9. 你要亲手理解的核心代码结构

你写 `server/main.py` 时，可以按这个结构思考：

```text
1. 读取 .env
2. 创建 FastAPI app
3. 引入 schemas.py 中的入参类型 (ChatRequest)
4. 创建 OpenAI-compatible client
5. 定义 POST /api/chat
6. 从请求 body 里拿 message
7. 调用 Qwen
8. 把 Qwen 的回答包装成 { reply }
```

不要一开始追求优雅封装。  
Day 1 的代码越直白越好，因为目标是理解链路。

---

## 10. Day 1 验收方式

启动后端后，用 curl 测试：

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"介绍一下 Sophie Zhu 的技术栈"}'
```

如果成功，你应该看到类似：

```json
{
  "reply": "..."
}
```

验收通过后，今天就可以停。不要急着接前端。

---

## 11. 常见错误排查

### 401 / invalid api key

检查：

- `.env` 是否真的在项目根目录
- key 是否复制完整
- Python 是否成功读取到 `QWEN_API_KEY`
- base_url 是否使用 compatible mode 地址

### ModuleNotFoundError

检查：

- 是否安装了 `requirements.txt`
- 当前终端是否使用了正确 Python 环境

### curl 连接不上

检查：

- FastAPI 是否启动成功
- 端口是不是 `8000`
- 路径是不是 `/api/chat`

### 模型返回很慢

先不用优化。Day 1 只要能成功返回即可。

---

## 12. 今日学习记录

### 今日复盘

- **今天我理解了**：Monorepo 前后端分离架构；Python 后端作为 API Key 守门人的角色；`messages` 数组里 `system` / `user` 的分工；用 curl 先测后端再接前端的验收思路
- **今天我亲手实现了**：`main.py` + `schemas.py` 分层；OpenAI SDK 兼容模式调用 Qwen；虚拟环境 + uvicorn 启动 FastAPI

### 踩坑提炼（知识盲区，非笔误类）

#### Python 环境与启动

- **两种启动方式的区别**（见下方展开）
- **`.env` 路径与启动目录解耦**：在 `server/` 下跑 uvicorn 时，默认 `load_dotenv()` 找不到根目录的 `.env`；需要用 `Path(__file__).resolve().parent.parent / ".env"` 精确定位

```py
from dotenv import load_dotenv
import os
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
# load_dotenv之后才可以使用 os.getenv('xxx')
```

##### `uvicorn main:app` vs `python main.py` —— 到底差在哪？

可以把它们分成两层来理解：

|                    | `main.py` 的角色                             | 谁负责监听 HTTP 请求                        |
| ------------------ | -------------------------------------------- | ------------------------------------------- |
| `uvicorn main:app` | 只**定义**应用（路由、逻辑）                 | **uvicorn**（专业 Web 服务器）              |
| `python main.py`   | 只是把文件**从上到下执行一遍**并没有启动项目 | 除非你在文件末尾手动调用 `uvicorn.run(...)` |

**`uvicorn main:app --reload` 做了什么？**

#### FastAPI 核心概念（今天最不熟的部分）

- **`app` vs `APIRouter`**：`uvicorn main:app` 要求模块里暴露 `app = FastAPI()`；`APIRouter` 是路由容器，适合后期按模块拆分，Day 1 直接 `@app.post` 更简单
- **`include_router` 的时机**：若用 Router，路由必须定义在 `include_router()` **之前**，否则路由挂不上去，请求会 404
- **入参类型决定数据从哪来**（关键）：
  - `request: str` → FastAPI 当作 **query 参数**，期望 `?request=xxx`，发 JSON body 会 422
  - `request: ChatRequest`（Pydantic）→ 从 **JSON body** 解析，才能接收 `{"message": "..."}`

- **Python 类型注解**：注解用内置 `str`，不是 `string`（`string` 是标准库模块名）

#### 调试与排错方法

- **HTTP 状态码含义**：
  - `404` → 路由没注册上
  - `422` → 入参格式/类型不符合 FastAPI 预期
  - `500` → 代码执行中抛异常（看 uvicorn 终端的 traceback，不是 curl 终端）
- **`print` 出现在 uvicorn 终端**，不出现在 curl 终端；且异常之前的代码才会执行——如果 API 调用处就崩了，后面的 `print(response...)` 永远不会跑到
- **排错顺序**：先看 uvicorn 终端完整堆栈 → 确认路由（`/docs`）→ 确认入参（422 detail 里的 `loc` 字段）→ 确认发给模型的 `messages` 结构
