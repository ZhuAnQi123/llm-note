# Step 04：企业级规范重构与错误处理 (Day 4)

日期：2026-06-08  
阶段：阶段 2 - 接入真实大模型  
目标：告别“玩具代码”，按照企业级项目规范重构前后的 API 链路，并完善错误处理与可观测性。

---

## 1. 为什么需要这一步？

目前我们的代码虽然能跑通，但存在几个“不规范”的问题：
1. **硬编码与跨域**：前端直接 `fetch("http://localhost:8000/api/chat")`。在生产环境中，前后端通常同源或通过网关转发。本地开发依赖 CORS 容易出各种奇怪的网络中断问题（比如我们遇到的 `ERR_INTERNET_DISCONNECTED`）。
2. **逻辑耦合**：`HeroSection.tsx` 既负责 UI 渲染，又负责复杂的流式 API 请求解析。组件太臃肿，不符合“关注点分离（Separation of Concerns）”原则。
3. **缺乏健壮性**：如果大模型 API 抽风（超时、502），目前只是简单 catch，缺乏优雅的重试或规范的错误码透传。

---

## 2. 今天的实操任务

### 任务 1：配置 Vite Proxy（解决跨域与硬编码）
- 在 `vite.config.ts` 中配置反向代理，将 `/api` 打头的请求转发到 `http://127.0.0.1:8000`。
- 将前端代码中的 `http://localhost:8000/api/chat` 统一改为相对路径 `/api/chat`。

### 任务 2：前端代码分层（Service 层抽取）
- 在 `src/` 下新建 `services/chatService.ts`。
- 将 `fetch` 和 `TextDecoder` 解析流的底层逻辑抽离成一个独立的异步函数。
- UI 组件 `HeroSection.tsx` 只负责调用该函数，并传入回调（`onChunk`, `onDone`, `onError`）来更新 React 状态。

### 任务 3：后端异常捕获与日志规范
- 在 `server/main.py` 中增加 `try-except`，捕获 OpenAI SDK 的异常（如网络错误、Token 超限）。
- 使用 FastAPI 的 `HTTPException` 返回规范的 HTTP 状态码，而不是让服务器直接 500 崩溃。

---

## 3. 核心代码结构提示

### 1. Vite Proxy 配置 (`vite.config.ts`)
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        // 这样配置后，前端请求 /api/chat 会被 Vite 自动转发给后端
      }
    }
  }
})
```

### 2. 前端 Service 抽取 (`src/services/chatService.ts`)
```typescript
export async function streamChatAPI(
  message: string,
  persona: string,
  onChunk: (text: string) => void,
  onDone: () => void,
  onError: (err: Error) => void
) {
  try {
    // 相对路径，走 Vite Proxy
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, persona }),
    });

    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    if (!res.body) throw new Error("No response body");

    const reader = res.body.getReader();
    const decoder = new TextDecoder("utf-8");

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        onDone();
        break;
      }
      const chunkText = decoder.decode(value, { stream: true });
      onChunk(chunkText);
    }
  } catch (error) {
    onError(error as Error);
  }
}
```

### 3. 组件内调用 (`HeroSection.tsx`)
```typescript
import { streamChatAPI } from "../services/chatService";

// ... 在 handleSend 中：
let streamResponse = "";
await streamChatAPI(
  query,
  persona,
  (chunk) => {
    streamResponse += chunk;
    // TODO: 使用 setMessages 更新最后一条气泡的 text
  },
  () => {
    // TODO: 结束，将 isStreaming 设为 false
  },
  (err) => {
    // TODO: 错误处理，显示友好提示
  }
);
```

---

## 4. Day 4 验收方式

1. **Proxy 验证**：检查浏览器 Network 面板，请求 URL 变成了 `http://localhost:5173/api/chat`，且不再有跨域的 `OPTIONS` 预检请求。
2. **解耦验证**：`HeroSection.tsx` 的代码行数显著减少，不再包含 `TextDecoder` 等底层流处理代码。
3. **容错验证**：故意关掉后端服务，在前端发送消息，确认 UI 能优雅地显示“连接失败”的提示，而不是白屏或一直 loading。

---

## 5. 今日学习记录

```md
## 今日复盘

- 今天我理解了：
  - [FE] 为什么企业级项目要用 Proxy 解决跨域，以及如何将 API 逻辑与 UI 组件解耦（关注点分离）。
  - [BE] FastAPI 中如何优雅地捕获并抛出 HTTP 异常。

- 今天我卡住了：
- 明天我要继续：
```