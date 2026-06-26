# 阶段 5：专业化打磨 & 上线 — 开发规划

日期：阶段 4 完成后  
阶段：阶段 5  
目标：把作品集从「本地 demo」升级为「可公开访问的产品级网站」。

---

## 对应 requirement.md

| 需求点 | 阶段 5 落地 |
| ------ | ----------- |
| Insights 技术博客 | 至少 1 篇 Streaming UX + RAG 工程复盘 |
| Streaming UX 极致优化 | 性能审查 + 动效 polish |
| 开源 UI 组件 | Chat 组件抽离 + GitHub README |
| 上线后可被搜索 | SEO meta / sitemap |

---

## 验收标准

- [ ] 网站 HTTPS 可公开访问
- [ ] 首页 meta / OG 标签完整（分享链接有预览）
- [ ] Insights 区域有 ≥ 1 篇文章
- [ ] Lighthouse Performance ≥ 80，Accessibility 无明显问题
- [ ] Chat 组件有独立 README，网站挂「UI Components Open Sourced」

---

## Step 规划

| Step | 文件 | 主题 | 关键产出 |
| ---- | ---- | ---- | -------- |
| 01 | step-01-deploy.md | 部署 | 前端 Vercel + 后端 Railway/Render，环境变量配置 |
| 02 | step-02-seo.md | SEO | `index.html` meta、OG、sitemap.xml、robots.txt |
| 03 | step-03-insights-article.md | 首篇技术文章 | Insights 组件 + Markdown 渲染 + 代码高亮 |
| 04 | step-04-performance-a11y.md | 性能 & 可访问性 | Lighthouse 审查、图片优化、键盘导航 |
| 05 | step-05-open-source.md | 开源 Chat 组件 | 抽离 `ChatWindow` 组件，写 README，网站加标签 |

---

## 部署架构建议

```text
用户浏览器
  → Vercel（React 静态站点 + /api Proxy 或直连后端 URL）
  → Railway / Render（FastAPI + ChromaDB 持久化卷）
  → DashScope API（Qwen chat + embedding）
```

**注意：**
- `.env` 密钥只在后端，Vercel 只放 `VITE_*` 公开变量
- ChromaDB 数据需要持久化卷，否则 redeploy 丢库
- 生产环境关闭 `uvicorn --reload`

---

## Insights 文章选题建议

任选其一作为首篇：

1. **《从 Mock 到 RAG：个人网站 Hero 区的 LLM 工程实践》**
2. **《Streaming UX 前端实现：getReader、TextDecoder 与 React 状态》**
3. **《多 Persona 知识库路由：ChromaDB Namespace 设计》**

---

## 开始方式

阶段 4 Dashboard 验收通过后，创建 `step-01-deploy.md` 并开始部署。
