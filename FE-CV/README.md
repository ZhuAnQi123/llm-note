# 前端面试大纲 2026
> 💡 核心准备策略（Key Takeaway）
*   **不要只背 API，要懂底层原理：** 面试官更看重你“在不依赖第三方库时如何解决问题”，比如浏览器的事件循环机制、渲染管道以及框架的 Fiber 协调。
*   **突出工程化与架构思维：** 资深前端与初中级前端的分水岭，在于你对组件库包管理（NPM 发布）、构建工具（Vite/Turbopack）以及多渲染模式（SSR/Static Export）的理解。
*   **提前准备“技术难点说故事”：** 准备 2-3 个你解决过的复杂挑战（如性能调优、复杂的 CMS 静态集成），用 **STAR 法则**（情境、任务、行动、结果）向面试官精彩呈现。

---


## 一、 核心基础知识 (The Core Fundamentals)
*   **JavaScript 深度进阶：**
    *   作用域链、闭包机制、变量提升与垃圾回收。
    *   **Event Loop（事件循环机制）**：宏任务（MacroTask）与微任务（MicroTask）的浏览器/Node.js 执行顺序。
    *   异步编程深度：Promise 规范、`async/await` 语法糖及其底层的 Generator 机制。
    *   原型与原型链：继承机制、`new` 的实现、`this` 绑定（call/apply/bind 区别）。
*   **TypeScript 实战应用：**
    *   高级类型系统：Generics（泛型）、Union/Intersection Types。
    *   **Utility Types 的灵活运用**（如 `Omit`、`Pick`、`Record`、`ReturnType` 等）。
    *   TS 编译配置优化（`tsconfig.json`）与在现代框架中的工程实践。
*   **浏览器与网络安全：**
    *   **关键渲染路径 (CRP)**：HTML/CSS 解析、DOM/CSSOM 树构建、Layout、Paint 到 Composite 的完整流程。
    *   重绘 (Repaint) 与回流 (Reflow) 的触发机制与性能优化。
    *   浏览器安全：跨站脚本攻击 (XSS)、跨站请求伪造 (CSRF)、同源策略 (CORS) 及其防御手段 (CSP)。

## 二、 网络与性能优化 (Network & Performance)
*   **计算机网络协议：**
    *   HTTP/1.1、HTTP/2、HTTP/3 的演进及多路复用、头部压缩等核心技术差异。
    *   **HTTPS 握手过程与加密原理**（对称加密、非对称加密、CA 证书）。
    *   浏览器缓存机制：强缓存 (Cache-Control) 与协商缓存 (Etag/Last-Modified) 的协作。
*   **性能调优与 Core Web Vitals：**
    *   核心用户体验指标优化：LCP (最大内容绘制)、INP (交互延迟时间)、CLS (累积布局偏移)。
    *   首屏加载优化：代码分割 (Code Splitting)、懒加载 (Lazy Loading)、Tree Shaking。
    *   资源优化：现代图片格式（WebP/AVIF）、字体子集化、静态资源 CDN 加速。

## 三、 现代前端框架与架构 (Modern Frameworks & Architecture)
*   **React 核心原理：**
    *   Virtual DOM 与 Fiber 架构：协调算法 (Reconciliation) 的双缓存机制。
    *   Hooks 的实现原理、并发渲染 (Concurrent Mode) 以及闭包陷阱的规避。
    *   状态管理方案对比：Zustand / Redux / Context API 及其适用场景。
*   **Next.js & 渲染架构深度（现代大厂热点）：**
    *   **多渲染模式**：SSR (服务端渲染)、SSG (静态站点生成)、ISR (增量静态再生) 的应用场景与混用。
    *   **Static Export (静态导出)** 机制，以及如何高效结合 Headless CMS（如 Strapi）进行企业级建站。
    *   React Server Components (RSC) 与 Client Components 的运行边界与数据流。
*   **UI 组件库与设计系统：**
    *   Headless 组件库设计思想（如 Radix UI、Ark UI）与高复用性实现。
    *   设计系统 (Design System) 构建、UI Motion 动画指标设定与性能保障。
    *   **NPM 组件发布流程**、语义化版本 (SemVer) 控制、多模块格式输出（ESM/CJS）。

## 四、 前端工程化与工具链 (Frontend Tooling & DevOps)
*   **构建工具演进：**
    *   Webpack、Vite、Turbopack 构建原理及热更新 (HMR) 的工作机制。
    *   打包体积优化实战：Bundle 深度拆分、按需加载。
*   **多包管理与编辑器生态：**
    *   pnpm 幽灵依赖解决方案与 **Monorepo (多包仓库) 架构管理**。
    *   开发协议工具：了解 **MCP (Model Context Protocol)** 在现代编辑器生态（如 Cursor 等 AI 工具）中的连接应用。
*   **CI/CD 与部署环境：**
    *   主流静态托管部署（Vercel、Docker 容器化）。
    *   自动化 lint (ESLint, Ruff)、格式化、单元测试在自动化流水线中的集成。

## 五、 算法、手写题与系统设计 (Algorithms & Design)
*   **数据结构与算法：**
    *   高频 LeetCode 题目归类：双指针、链表操作、二叉树遍历、DFS/BFS、滑动窗口。
*   **高频手写题：**
    *   防抖 (Debounce) 与节流 (Throttle) 的立即执行版本。
    *   深拷贝 (Deep Clone) 的循环引用处理。
    *   手写 Promise (Promise.all/race/allSettled)。
    *   手写自定义 React Hooks（如 `useLocalStorage`、`useDebounce`）。
*   **前端系统设计 (System Design)：**
    *   如何从零设计一个大型复杂组件或模块（例如：Autocomplete 联想输入框、无限滚动 Infinite Scroll、权限管理系统）。
    *   考察重点：API 边界设计、全局状态流向、网络竞态处理、渲染性能兜底。

## 六、 前沿科技：AI 与前端的融合 (Next-Gen Frontend & AI)
*   **AI API 接入实战：** 前端集成 Gemini 等大模型 API 时的流式传输 (Streaming) 展现、错误兜底设计。
*   **Prompt 工程与智能化应用：** 结合 Prompt Registry A/B 测试、前端可观测性日志记录和埋点。
*   **AI 辅助工作流：** 熟练运用现代 AI 开发工具（Cursor、AI 编程助理）完成代码快速重构与 Loop/Harness 级别的测试验证。

---

## 🛡️ 常见面试误区（Proactive Tips）
1.  **“背书”感太重：** 在被问到类似“Redux 与 Zustand 区别”时，不要只念概念，应从“我们团队在什么业务场景下，因为遇到了什么心智模型负担，从而决定做这套技术选型”去回答。
2.  **写代码时“闷头敲”：** 在白板写算法或实现系统设计时，最忌讳不吭声。务必在动笔前**先与面试官确认入参、边界条件**，并一边敲代码一边说出你的思路（Mock Interview 非常有助于突破这一关）。
