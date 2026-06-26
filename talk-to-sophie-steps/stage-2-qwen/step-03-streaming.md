# Step 03：实现流式输出（Streaming 版本 1）(Day 3)

日期：2026-06-07  
阶段：阶段 2 - 接入真实大模型  
目标：将原本一次性返回的 API 改造为流式输出（Streaming），让前端的打字机效果变成真实的“边生成边显示”。

---

## 1. 今天的学习目标

【相关知识点】

- 【前端】**getReader拿数据流**：`fetch` 请求不仅可以 `await res.json()` 一次性拿结果，还可以通过 `res.body.getReader()` 拿到一个数据流读取器。我们可以用 `while` 循环不断读取网络通道里传过来的数据块（Chunks）。
- 【后端】**FastAPI 的 StreamingResponse**：普通的 `return {"reply": "..."}` 是一次性响应。要实现流式，我们需要写一个**生成器函数 (Generator)**（使用 `yield` 关键字），并用 FastAPI 提供的 `StreamingResponse` 将其包裹返回。

---

## 2. 今天的实操任务

今天你需要将昨天跑通的单次问答链路，升级为流式链路：

1. **后端改造**：在 `server/main.py` 中，将 Qwen API 的调用参数改为 `stream=True`，并使用 `StreamingResponse` 返回数据流。
2. **前端改造**：在 `src/components/HeroSection.tsx` 中，不再使用 `res.json()`，而是读取 `res.body`，并逐字更新到 React 状态中。

---

## 3. 核心代码结构提示

### 后端提示 (`server/main.py`)

你需要引入 FastAPI 的流式响应类：

```python
from fastapi.responses import StreamingResponse
```

修改 `/api/chat` 路由内部的逻辑。当 `stream=True` 时，`client.chat.completions.create` 返回的不再是一个完整的对象，而是一个可以迭代的流（stream）。

```python
@app.post("/api/chat")
async def chat(request: ChatRequest):
    # ... 前面组装 messages 的代码保持不变 ...

    # 1. 创建一个生成器函数
    def generate():
        # 注意这里加了 stream=True
        stream_response = client.chat.completions.create(
            model=os.getenv("QWEN_MODEL"),
            messages=messages,
            stream=True
        )

        # 遍历流中的每一个 chunk
        for chunk in stream_response:
            # OpenAI 兼容格式下，增量文本在 chunk.choices[0].delta.content
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    # 2. 返回 StreamingResponse，而不是 JSON
    return StreamingResponse(generate(), media_type="text/event-stream")
```

_(注意：因为返回的不再是 JSON，你需要把 `@app.post` 装饰器里的 `response_model=ChatResponse` 删掉，否则 FastAPI 会尝试把流转成 JSON 报错)_

### 前端提示 (`src/components/HeroSection.tsx`)

找到 `handleSend` 函数中的 `try` 块，把 `const data = await res.json();` 及其后面的逻辑替换为流式读取逻辑：

```typescript
try {
  const res = await fetch("http://localhost:8000/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: query, persona: persona }),
  });

  if (!res.ok) throw new Error("Failed to fetch");
  if (!res.body) throw new Error("No response body");

  // 1. 获取流读取器和文本解码器
  const reader = res.body.getReader();
  const decoder = new TextDecoder("utf-8");

  // 2. 准备一个变量来累加完整的回复
  let aiReply = "";

  // 3. 循环读取流数据
  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      // 流结束，把 isStreaming 设为 false
      setMessages((prev) => {
        const updated = [...prev];
        const lastMsg = updated[updated.length - 1];
        if (lastMsg && lastMsg.sender === "ai") {
          lastMsg.isStreaming = false;
        }
        return updated;
      });
      break;
    }

    // 解码当前拿到的二进制数据块 (Uint8Array -> string)
    const chunkText = decoder.decode(value, { stream: true });
    aiReply += chunkText;

    // 4. 实时更新 React 状态中的最后一条消息
    setMessages((prev) => {
      const updated = [...prev];
      const lastMsg = updated[updated.length - 1];
      if (lastMsg && lastMsg.sender === "ai") {
        lastMsg.text = aiReply; // 更新为累加后的文本
      }
      return updated;
    });
  }
} catch (error) {
  // ... 错误处理逻辑保持不变 ...
}
```

**前置小修提示**：记得在 `handleSend` 最开始，先 `setMessages` 添加用户的消息，然后再添加一条 `{ sender: "ai", text: "", isStreaming: true }` 作为占位气泡，接着再发起 `fetch`。

---

## 4. Day 3 验收方式

1. 重启后端 `python server/main.py`（如果你没有用 `--reload` 的话）。
2. 在前端页面提问。
3. **验收标准**：
   - 气泡出现后，文字是**一段一段/逐字**冒出来的，而不是像昨天那样卡顿几秒后突然整段出现。
   - 打开浏览器 F12 -> Network 面板，点击 `/api/chat` 请求，查看 `Headers`，你应该能看到 `Transfer-Encoding: chunked`，这标志着流式传输成功建立。

---

## 5. 常见错误排查

### 报错 `pydantic.error_wrappers.ValidationError` 或类似 Schema 错误

**检查**：你是否忘记在 `server/main.py` 的 `@app.post("/api/chat")` 装饰器中去掉 `response_model=ChatResponse`？因为现在返回的是流，不再是那个 Pydantic 模型了。

### 前端文字是一次性蹦出来的，没有流式感

**检查**：

- 后端 `client.chat.completions.create` 里面有没有加 `stream=True`？
- 前端是否正确使用了 `reader.read()` 并在 `while` 循环里调用了 `setMessages`？

### 前端出现乱码

**检查**：`TextDecoder` 解码时是否传入了 `{ stream: true }` 选项。因为有时候一个中文字符（3个字节）会被网络切断成两半传输，`stream: true` 可以让解码器保留不完整的字节，等下一块数据来了再合并解码。

---

## 6. 今日学习记录

把你的过程写在这里：

```md
## 今日复盘

- 今天我理解了：
  - [BE]openai包裹在函数中，并且把传isStreaming为true，并且使用StreamingResponse包裹LLM函数
  - [FE]从res.body.getReader() 获取流数据；用TextDecoder的decoder.decode(text,{stream:true})来将流数据转化为文字

- 今天我卡住了：
  - **现象**：前端发请求后，Network 报错 `ERR_INTERNET_DISCONNECTED`，页面没有 AI 回复，但后端终端只显示 `OPTIONS 200 OK`。
  - **原因**：流式请求是**长连接**。在测试期间，如果我保存了后端的 `main.py`，`uvicorn --reload` 会自动重启后端进程，导致正在进行的 POST 流式连接被强行掐断。Chrome 浏览器会将这种突然断开的本地连接误报为“网络已断开”。
  - **解决**：测试长连接时保持后端稳定（不要频繁保存文件触发 reload）。另外，前端代码中缺少了“流式请求前先插入一条空的 AI 占位气泡”的逻辑，导致即使后端正常返回，前端也找不到气泡来更新文字。补上 `{ sender: "ai", text: "", isStreaming: true }` 占位后解决。
- 明天我要继续：
```
