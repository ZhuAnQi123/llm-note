import os 
import json
import time
from dashscope import Generation
from http import HTTPStatus
dashscope.api_key = 'sk-59c5b66dbe244feaaa26dabb23c5616b'

def call_qwen_with_retry(prompt, max_retries=3):
    """
    带有指数退避重试机制的 AI 调用函数
    """
    messages = [{'role': 'user', 'content': prompt}]
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 正在尝试调用 API (第 {attempt + 1} 次)...")
            response = Generation.call(
                model="qwen-turbo",
                messages=messages,
                result_format='message'
            )
            
            if response.status_code == HTTPStatus.OK:
                return response.output.choices[0]['message']['content']
            elif response.status_code == 429: # Too Many Requests
                print("⚠️  触发频率限制，等待重试...")
                # **指数退避（Exponential Backoff）**算法。
                # 网络请求重试——让程序在每次重试时等待的时间**指数级增长**。
                time.sleep(2 ** attempt)
            else:
                print(f"❌ API 错误: {response.code} - {response.message}")
                time.sleep(1)
        except Exception as e:
            print(f"🚨 网络异常: {e}")
            time.sleep(1)
            
    return None

def robust_json_parser(ai_text):
    """
    尝试从 AI 返回的杂乱文本中提取 JSON
    """
    try:
        # 场景 1：完美的 JSON
        return json.loads(ai_text)
    except:
        # 场景 2：带了 ```json 代码块
        if "```json" in ai_text:
            clean_text = ai_text.split("```json")[1].split("```")[0].strip()
            try:
                return json.loads(clean_text)
            except: pass
        
        # 场景 3：完全无法解析
        return {"error": "JSON format is invalid", "raw_text": ai_text}

# --- Main ---
if __name__ == "__main__":
    # 模拟一个复杂的、可能导致 AI 出错的 Prompt
    messy_prompt = "给我一个包含 {'name': '张三'} 的 JSON，并在前后加一些废话说明。"
    
    raw_result = call_qwen_with_retry(messy_prompt)
    
    if raw_result:
        print("\n📥 AI 原始输出: ", raw_result)
        final_data = robust_json_parser(raw_result)
        print("\n✅ 最终解析出的数据: ", final_data)
    else:
        print("❌ 经过多次尝试仍无法获取结果。")