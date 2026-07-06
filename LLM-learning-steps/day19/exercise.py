#異步查詢與多任務處理
#模擬同時調用兩個 AI 專家（或兩個不同接口）並匯總結果。

import time
import asynico
impoirt json

async def mock_ai_call(expert_name,delay):
    """
    Simulate an AI model call with a delay
    """
    print(f"{expert_name} is thinking for {delay} seconds...")
    await asynico.sleep(delay)

    result = {
        "expert": expert_name,
        "content": f"Analysis result from {expert_name}",
        "confidence": 0.95
    }

    return json.dumps(result)

async def call_with_timeout(expert_name,delay,timeout=2.5):
    try:
        result = await asyncio.wait_for(
            mock_ai_call(expert_name,delay),
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        error_result = {
            "expert": expert_name,
            "content": f"❌ Timeout: {expert_name} 响应超时（>{timeout}秒）",
            "confidence": 0.0,
            "error": "timeout"
        }
        return json.dumps(error_result)

async def run_parallel_analysis():
    start_time=time.time()

    #1. Start multiple tasks concurrently (Gather)
    print('--- 🧠 Starting Multi-Expert Analysis ---')
    results = await asyncio.gather(
        call_with_timeout('Data Scientist', 2, timeout=2.5),    # 2秒 < 2.5秒，成功
        call_with_timeout('Security Specialist', 3, timeout=2.5), # 3秒 > 2.5秒，超时
        call_with_timeout('Legal Advisor', 1.5, timeout=2.5)   # 1.5秒 < 2.5秒，成功
    )

    #2. Parse and summarize results
    for r in results:
        data=json.loads(r)
        print(f'Expert: {data['expert']} | Result: {data['content']}\n')

    end_time=time.time()
    print(f'\n✅ Total time taken: {end_time - start_time:.2f} seconds.')
    print('(Notice: Total time is roughly the maximum of individual delays, not the sum!)')

if __name__ == '__main__':
    asyncio.run(run_parallel_analysis())