# Step 05：前端引用来源展示 (Day 9)

日期：2026-06-13  
阶段：阶段 3 - 个人知识库 RAG  
目标：在 AI 回复气泡下方展示引用来源，让 `RAG ENABLED` 标签名副其实。

---

## 1. 今天的学习目标

【相关知识点】

- **Citation UI 的价值**：可追溯性是 RAG 产品与普通 Chatbot 的核心差异。面试官看到「回答 + 来源」会立刻理解你懂 RAG 工程。
- **UX 设计参考**：Perplexity 的 numbered citations、ChatGPT 的 footnote 风格。你的站点已有 Glassmorphism 风格，引用可以用小 pill / chip 展示。
- **数据流**：Step 04 通过 Header 传 sources → `chatService.ts` 解析 → 回调传给 `HeroSection` → 存入 message state。

---

## 2. 对应 requirement.md

> Hero 区域 UI 上已有 `RAG ENABLED` / `NAMESPACE: NAVAL_DB` 标签——今天让它们展示**真实的 namespace 和命中来源**。

---

## 3. 今天的实操任务

### 任务 1：扩展 message 类型

在 `HeroSection.tsx` 的 message 类型中增加 sources：

```typescript
type ChatMessage = {
  sender: "user" | "ai";
  text: string;
  isStreaming?: boolean;
  sources?: Array<{ source: string; title: string }>;
};
```

### 任务 2：更新 `chatService.ts`

在 fetch 成功后、开始读流之前，解析 Header：

```typescript
const sourcesHeader = res.headers.get("X-RAG-Sources");
const sources = sourcesHeader ? JSON.parse(sourcesHeader) : [];
// 通过 onSources(sources) 回调传给 UI
```

### 任务 3：UI 展示引用

在 AI 气泡下方（流式结束后）渲染来源 chips：

```text
┌─────────────────────────────────┐
│ AI 回复正文……                    │
└─────────────────────────────────┘
  📎 resume.md · 工作经历
  📎 projects.md · Light-Agent Flow
```

**设计提示：**
- 流式过程中不显示 sources（等 `isStreaming: false`）
- chip 样式与现有 Glassmorphism / pill toggle 一致
- persona 切换时，badge 文案可显示真实 chunk 数（可选，Step 06 完善）

### 任务 4：更新 Hero badge

把静态文案改为动态（可选）：

```text
Sophie:  RAG · sophie_kb · 3 sources
Naval:   RAG · naval_kb · 2 sources
```

---

## 4. 验收方式

1. 问 Sophie 一个简历里有的问题 → 回复下方出现 ≥ 1 个来源 chip
2. 问一个知识库没有的问题 → 无来源 chip，且 AI 说「资料中没有提到」
3. 切换 Naval → 来源 chip 显示 naval 目录下的文件名
4. 流式过程中不出现 chip，结束后才淡入（可用 Framer Motion）

---

## 5. 常见错误排查

### sources Header 为 null

**检查**：Step 04 后端是否设置了 `expose_headers`？Vite Proxy 是否转发自定义 Header？

### chip 显示了但内容不对

**检查**：`JSON.parse` 是否报错？Console 里打印 sources 数组确认结构。

---

## 6. 今日学习记录

```md
## 今日复盘

- 今天我理解了：
- 今天我亲手实现了：
- 今天我卡住了：
- 明天我要继续：Step 06 评估
```
