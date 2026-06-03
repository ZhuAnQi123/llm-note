# 第1天— 概念与账号准备
cost：（3.0–3.5 小时）    
- 学：
    
    * [-] 阅读 OpenAI [Quick Start](https://developers.openai.com/api/docs/quickstart)
    * [] 阅读 OpenAI [Prompt Guide](https://developers.openai.com/api/docs/guides/prompt-guidance)（重点：temperature、max_tokens、top_p、few-shot、system vs user）、  
    - [ ] [Hugging Face Inference](https://huggingface.co/docs/inference-providers/index) 基础章节（文本生成/embedding 概念）。
 - [x]: 做：注册 OpenAI（或其他模型 API）并拿到 API Key；注册 Hugging Face 账号。
- 输出：一个笔记（.md）列出 8 个要记住的 LLM 概念与你理解的短释。

## LMM(Large Language Model)
Large Language Model Engineer.  
专注于大语言模型（如 GPT、LLaMA、Claude 等）的开发、微调、部署和优化.  
工作内容包括：模型训练、提示词工程、RAG 开发、模型压缩等

## Quick Start
example
```py
import OpenAI from "openai";
const client = new OpenAI();

const response = await client.responses.create({
    model: "gpt-5",
    // tools 联网搜索
    tools: [
        { type: "web_search" },
    ],
    //输入类型，可以是文字/图片输入
     content: [
                {
                    type: "input_text",
                    text: "What is in this image?",
                },
                {
                    type: "input_image",
                    image_url: "https://ope.png",
                },
            ],
    input: "What was a positive news story from today?",
});

console.log(response.output_text);
```

## Prompt Guide（GPT-5.4）

### 完整知识框架图

```
┌─────────────────────────────────────────────────────────────┐
│                    GPT-5.4 Prompt 工程                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Prompt Contract（提示词契约）                             │
│     ├── 输出格式与简洁性控制                                   │
│     ├── 行为与决策规则                                         │
│     ├── 任务完整性与持久性                                     │
│     ├── 工具使用规则                                           │
│     ├── 研究/引用/事实性                                       │
│     ├── 编码/终端/前端专用                                     │
│     └── 个性与风格控制                                         │
│                                                               │
│  2. Runtime Contract（运行时契约）                            │
│     ├── Phase 参数（区分工作中消息与最终答案）                  │
│     └── Compaction（长会话压缩机制）                          │
│                                                               │
│  3. 个性与写作控制                                            │
│     ├── 持久个性（Personality）                               │
│     ├── 单次控制（Writing Controls）                          │
│     └── 专业备忘录模式（Memo Mode）                           │
│                                                               │
│  4. 推理力度调优                                              │
│     ├── none / low / medium / high / xhigh 选择指南           │
│     ├── 先用 Prompt 优化，再调 reasoning_effort               │
│     └── <dig_deeper_nudge> 提升主动性                         │
│                                                               │
│  5. 迁移策略                                                  │
│     └── 一次只改一个变量 + 按来源选择起点                      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```






### 优势
在保持tools调用精度的前提下，进行批量或并行调用。
### 短板介绍
即便是像 GPT-5.4 这样强大的模型，在以下几种典型复杂场景下，仍然需要通过精心设计的“提示词”（Prompt）

* 在低上下文时需要明确指定需要的工具，已经相应的用途。  
    比如：‘“如果需要知道时间，请使用 get_current_time 工具；如果涉及未来日期计算，请使用 date_calculator 工具。不要猜测。”’
* 在处理有前后顺序的任务时模型可能会忽略潜质步骤直接完成最后一步
    比如先拉取数据、再清洗、最后可视化。模型可能会直接尝试最后一步。   
    方法：使用编号排序，或者“必须完成步骤A才能进行步骤B”的清晰描述

* 不要所有问题都深度思考
    建议：在提示中写明：“如果问题是事实性查询，快速回答；如果涉及多步逻辑或数学，进入详细思考模式。”

* 研究型任务比如让模型做研究（如写行业报告）时，它可能信息源不固定、格式混乱，甚至编造来源。
    方法：强制其收集有来源的信息。比如“请至少引用3个来自指定来源（如 .edu 或 .gov 域名）的内容，并以 APA 格式列出。每一步发现均需注明出处。”

* 高风险操作（如删除数据库、发送邮件、执行交易）前的挽留操作
    方法：要求模型在执行前增加“确认”步骤

* 模糊代码环境使用边界
    建议：说明所有python代码都需要包含错误处理


### [Prompt Contract](./prompt-contracts.md)

### [Runtime Contract](./runtime-contract.md) 运行时与 API 集成要点



