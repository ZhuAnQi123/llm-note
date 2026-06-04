# 將 API 調用封裝成一個函數或類。而不是把幾百行代碼塞在一個文件裡。
# 嘗試在 modes 字典中增加第 4 個模式，比如「情感分析」或「關鍵詞提取」，看看代碼邏輯是如何對應修改的。
import os
import json
import asyncio
from dashscope import Generation
from http import HTTPStatus
from functools import partial

# --- 1. Configuration & Utils ---
class AsyncAIProcessor:
    def __init__(self, api_key=None):
        # Prefer setting DASHSCOPE_API_KEY as an environment variable
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("❌ Error: DashScope API Key is missing!")

    async def call_qwen(self, system_prompt, user_content):
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_content}
        ]
        
        def sync_call():
            return Generation.call(
                model="qwen-turbo", # Turbo is fast and cheap for testing
                messages=messages,
                result_format='message',
                api_key=self.api_key,
            )
        
        # 塞型的同步代码就需要用loop.run_in_executor来执行
        loop= asyncio.get_running_loop()
        response = await loop.run_in_executor(None, sync_call)

        if response.status_code= HTTPStatus.OK:
            return response.output.choices[0]['message']['content']
        else:
            return f'Error: {response.code} - {response.message}'

    # 批量处理多个不同的文本，或者一个文本的多个不同分析。
    async def call_qwen_batch(self,prompts_and_contetns):
        '''批量并发调用'''
        tasks = [
            self.call_qwen(prompt,content)
            for prompt,content in prompts_and_contetns
        ]
        return await asyncio.gather(*tasks)
        


# 异步版本的 main
async def async_main():
    processor = AsyncAIProcessor()
    
    modes = {
        "1": {"name": "📜 摘要生成", "prompt": "你是一個專業的文章摘要專家。請總結用戶提供的內容，並條列重點。"},
        "2": {"name": "🌐 翻譯專家", "prompt": "你是一個資深的翻譯專家。請將用戶輸入的內容翻譯成地道的英文。"},
        "3": {"name": "✍️ 語法校對", "prompt": "你是一個嚴謹的寫作老師。請修正用戶輸入中的語法錯誤，並給予改進建議。"}
    }
    
    print("\n" + "="*40)
    print("🚀 歡迎使用 AI 多功能文本助手 (Day 20)")
    print("="*40)
    
    while True:
        print("\n請選擇模式：")
        for k, v in modes.items():
            print(f"  {k}. {v['name']}")
        print("  Q. 退出程序")
        
        choice = input("\n👉 你的選擇: ").strip().upper()
        
        if choice == 'Q':
            print("再見！👋")
            break
            
        if choice not in modes:
            print("⚠️ 選擇無效，請重新輸入！")
            continue
            
        selected_mode = modes[choice]
        user_text = input(f"\n[{selected_mode['name']}] 請輸入待處理的文本: \n> ")
        
        print("\n⏳ AI 正在處理中...")
        result = processor.call_qwen(selected_mode['prompt'], user_text)
        
        # 过程性函数main 就不需要return的～
        print("\n" + "-"*30)
        print(f"✨ 處理結果:\n{result}")
        print("-"*30)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
            