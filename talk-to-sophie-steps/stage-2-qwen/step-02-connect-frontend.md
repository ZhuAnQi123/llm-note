# Step 02：把后端接到前端（Day 2）

日期：2026-06-05  
阶段：阶段 2 - 接入真实大模型  
目标：让 React 前端通过 `fetch` 调用昨天写好的 Python 后端，实现真实对话（暂不使用流式输出）。

---

## 1. 今天的学习目标

【相关知识点】

- **跨域资源共享 (CORS)**：你的前端运行在 `localhost:5173` (Vite)，后端运行在 `localhost:8000` (FastAPI)。浏览器的安全机制默认禁止这种跨端口的请求。你需要在后端配置 CORS 中间件来允许前端访问。
- **React 异步请求与状态管理**：在前端，你需要使用 `fetch` 发送网络请求，并使用 `useState` 来管理“加载中 (Loading)”和“错误 (Error)”状态。
- **System Prompt (系统提示词)**：大模型默认是一个通用的助手。通过在后端注入 `role: "system"` 的消息，你可以给它设定人设（Persona）、语气和边界。

---

## 2. 今天的实操任务

今天你需要打通前后端，完成以下步骤：

1. **后端配置 CORS**：修改 `server/main.py`，允许前端跨域请求。
2. **后端注入 System Prompt**：在发给 Qwen 的 `messages` 数组最前面，加上系统提示词。
3. **前端对接 API**：修改 `src/components/HeroSection.tsx`，把原本的 `setTimeout` 和本地假数据替换成真实的 `fetch` 请求。
4. **前端状态处理**：在等待接口返回时，给用户一个 "Thinking..." 的提示，并处理可能发生的网络错误。

---

## 3. 核心代码结构提示

### 后端提示 (`server/main.py`)

**关于 CORS：**
在 FastAPI 中，你需要引入 `CORSMiddleware`。

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # 允许你的 Vite 前端访问
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**关于 System Prompt：**
在组装发给 Qwen 的 `messages` 时，固定写死第一条：

```python
messages = [
    {"role": "system", "content": "你是 Sophie Zhu (朱安琪) 的 AI 交互分身。你懂前端开发和 LLM 工程。回答要简短、专业。如果问到你不知道的个人经历，请直接说不知道，绝不编造。"},
    {"role": "user", "content": request.message}
]
```

### 前端提示 (`src/components/HeroSection.tsx`)

找到 `handleSend` 函数，把里面的 `setTimeout` 删掉，换成 `async/await` 结构的 `fetch` 请求：

```typescript
const handleSend = async (textToSend: string) => {
  // ... 前面的代码保持不变 (添加 user 消息)

  // 1. 先在界面上添加一个 loading 状态的 AI 气泡
  setMessages((prev) => [
    ...prev,
    { sender: "ai", text: "Thinking...", isStreaming: true },
  ]);

  try {
    // 2. 发起真实请求
    const response = await fetch("http://localhost:8000/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: query }),
    });

    if (!response.ok) throw new Error("Network response was not ok");

    const data = await response.json();

    // 3. 替换掉那个 loading 气泡，填入真实回复
    setMessages((prev) => {
      const updated = [...prev];
      updated[updated.length - 1] = {
        sender: "ai",
        text: data.reply,
        isStreaming: false,
      };
      return updated;
    });
  } catch (error) {
    // 4. 错误处理
    setMessages((prev) => {
      const updated = [...prev];
      updated[updated.length - 1] = {
        sender: "ai",
        text: "抱歉，我的大脑（后端服务）似乎断开了连接。请检查终端是否启动了 FastAPI。",
        isStreaming: false,
      };
      return updated;
    });
  }
};
```

_(注意：今天我们先把 `KB_RESPONSES` 这个假字典删掉或注释掉，彻底依赖真实模型)_

---

## 4. Day 2 验收方式

1. 保持终端 1 运行 `python server/main.py` (确保在正确的虚拟环境中)。
2. 保持终端 2 运行 `npm run dev`。
3. 打开浏览器 `http://localhost:5173`。
4. 在 Hero 区域的聊天框输入：“介绍一下 Sophie Zhu 的技术栈”。
5. **验收标准**：
   - 气泡先显示 "Thinking..."
   - 几秒钟后，气泡变成 Qwen 生成的真实回答。
   - 回答的语气符合你在后端设定的 System Prompt。
   - 浏览器 F12 (开发者工具) -> Network (网络) 面板里，能看到发往 `localhost:8000` 的请求，且**没有暴露任何 API Key**。

---

## 5. 常见错误排查

### 前端报错 "Failed to fetch" 或 "CORS error"

**检查**：

- 后端的 `CORSMiddleware` 是否配置正确？`allow_origins` 里的端口号是不是和前端一致？（注意不要在 URL 结尾加 `/`）。
- 后端服务是否正在运行？

### 前端收到 500 Internal Server Error

**检查**：

- 看运行 Python 的终端报错信息。通常是因为前后端 JSON 字段名没对齐（比如前端发了 `message`，后端 schemas 期望的是 `text`）。

---

## 6. 今日学习记录

## 今日复盘

- **今天我理解了：**
  - **CORS 的两步请求**：浏览器跨域 POST 会先发 `OPTIONS` 预检，通过后才发真正的 `POST`。终端里看到 `OPTIONS 200` 只说明预检成功，不代表业务请求一定成功。
  - **前后端契约（Contract）**：`schemas.py` 里定义 `reply`，后端就必须返回 `reply`，前端读 `data.reply` 才能对上。字段名不一致时，即使 `POST 200` 界面也可能空白。
  - **System Prompt 与 Persona**：在后端根据 `persona`（`sophie` / `naval`）注入不同的 `system` 消息，比在前端写死假数据更接近真实 LLM 产品。
  - **开发环境的干扰**：`uvicorn --reload` 在保存 `main.py` 时会重启服务，进行中的 fetch 可能被中断，浏览器可能报 `ERR_INTERNET_DISCONNECTED` 或 `Failed to fetch`——这不一定是 CORS 或 Key 的问题。
  - **分层调试法**：先用 `curl` 测后端，再测前端。`curl` 通说明 Qwen + FastAPI 没问题，问题多半在前端状态或 dev 环境。

- **今天我亲手实现了：**
  - 在 `server/main.py` 配置 `CORSMiddleware`，允许 `http://localhost:5173` 访问。
  - 在 `schemas.py` 扩展 `Persona` 枚举与 `ChatRequest`，支持 `message + persona` 入参。
  - 后端按 persona 注入不同 System Prompt，调用 Qwen 并返回 `ChatResponse(reply=...)`。
  - 在 `HeroSection.tsx` 用 `async/await + fetch` 替换 mock 的 `setTimeout + KB_RESPONSES` 主路径。
  - 用 `curl -X POST http://127.0.0.1:8000/api/chat` 验证后端链路，确认能拿到真实 `reply`。

- **今天我卡住了：**
  - 浏览器 Network 报 `ERR_INTERNET_DISCONNECTED`，后端有时只有 `OPTIONS 200`、没有 `POST` 日志。
  - 前后端字段一度不一致：后端返回 `message`，前端读 `reply`（已修正为统一 `reply`）。
  - 前端 success 逻辑曾试图「更新最后一条 ai 气泡」，但前面只 push 了 user 消息，导致成功也不显示回复（后改为 success 时 append 新的 ai 气泡）。
  - Python 虚拟环境最初用了别的项目的 `.venv`，启动时报 `ModuleNotFoundError: openai`（后在该 venv 中 `pip install openai` 解决）。
  - Step 2 文档要求的 `Thinking...` loading 态和「失败时替换 loading 气泡」尚未完全按规范实现，catch 里仍是 append 新错误气泡。

- **排查结论（重要）：**
  - 后端 **已验证可用**（curl 返回 `{"reply":"..."}`）。
  - 问题主要落在：**前端消息状态更新逻辑** + **dev 热重载打断请求**，而不是 Qwen Key 或 CORS 配置本身。

- **明天我要继续（Step 03 前置小修）：**
  - [ ] 补全 `Thinking...` loading 气泡，成功/失败都**替换**该气泡，而不是 append。
  - [ ] 测试时等 uvicorn 稳定后再发请求，或暂时不用 `--reload` 做联调。
  - [ ] 删除调试用 `console.log`，统一中英文错误提示。
  - [ ] 进入 **Step 03：Streaming 流式输出**，把假打字机换成真实 chunk 流。
  - [ ] （可选）用 Vite proxy 代理 `/api` 到 `8000`，减少硬编码 `localhost:8000`。

- **给自己的一句话：**
  > Step 2 已经打通了「真实 LLM 对话」的骨架；卡住的不是能力不够，而是第一次经历「预检通过 ≠ 请求成功」和「后端通了 ≠ 前端显示对」——这正是 LLM 全栈开发里最值钱的调试经验。
