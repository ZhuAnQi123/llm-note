import OpenAI from "openai";
import 'dotenv/config';
const openai = new OpenAI({
    apiKey: process.env.QIANWEN_API_KEY, 
    baseURL: "https://dashscope.aliyuncs.com/compatible-mode/v1" // 根据地域选择
});


async function main() {
    try {
        // 阿里云百炼的兼容模式不支持 openai.responses.create() 这个方法，
        // 它只支持标准的 openai.chat.completions.create() 方法。
        const response = await openai.chat.completions.create({
            model: "qwen-vl-plus-2025-05-07",
            messages: [
                {
                    role: "user",
                    content: "Write a one-sentence bedtime story about a unicorn."
                }
            ]
        });
        
        // response.output_text → response.choices[0].message.content
        console.log(response.choices[0].message.content);
        
    } catch (error) {
        console.error("调用失败:", error.message);
        if (error.response) {
            console.error("错误详情:", error.response.data);
        }
    }
}

main();