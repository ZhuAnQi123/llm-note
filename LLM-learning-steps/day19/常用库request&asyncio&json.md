# Day 19：常用庫學習 - Requests, JSON 與異步編程 (asyncio)

## 🎯 學習目標
*   學會使用 `requests` 庫調用外部 API（不僅限於官方 SDK）。
*   精通 `json` 數據的解析與轉換（LLM 的核心數據格式）。
*   初步理解 `asyncio` 異步編程，解決調用 LLM 時的等待阻塞問題。

---

## 📚 學習資源
*   **Requests 官方文檔**: [Requests: HTTP for Humans](https://requests.readthedocs.io/en/latest/)
*   **Python JSON 模組**: [JSON Documentation](https://docs.python.org/3/library/json.html)
*   **Asyncio 入門教程 (必讀)**: [Asyncio Basics](https://realpython.com/async-io-python/)

---

## 🛠️ 新手必會知識點 (附範例)
`json.load`
`json.dumps`
### 1. JSON 解析 (Parse JSON)
LLM 輸出的結構化數據通常是字符串，你需要將其轉換為 Python 字典。
```python
import json

# String from LLM
llm_output = '{"name": "Python", "type": "AI Language", "rating": 5}'

# Convert String to Dictionary (json.loads)
data = json.loads(llm_output)
print(data["name"]) # Python

# Convert Dictionary to String (json.dumps)
new_json = json.dumps(data, indent=4) # indent=4 makes it readable
print(new_json)
```

### 2. 異步編程基礎 (Asyncio)
AI 調用通常需要 2-10 秒，異步 `asyncio.gather`可以让里面的task同时执行
```python
import asyncio

async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)

async def main():
    print(f"Started at {time.strftime('%X')}")
    # Run two tasks concurrently
    await asyncio.gather(
        say_after(1, "Task 1 finished"),
        say_after(2, "Task 2 finished")
    )
    print(f"Finished at {time.strftime('%X')}")
```

---

## 💻 完整可運行範例：異步查詢與多任務處理
模擬同時調用兩個 AI 專家（或兩個不同接口）並匯總結果。

```python
import asyncio
import time
import json

async def mock_ai_call(expert_name, delay):
    """
    Simulate an AI model call with a delay.
    """
    print(f"🚀 {expert_name} is thinking for {delay} seconds...")
    await asyncio.sleep(delay) # Simulate network IO
    
    # Return a JSON-style string
    result = {
        "expert": expert_name,
        "content": f"Analysis result from {expert_name}",
        "confidence": 0.95
    }
    return json.dumps(result)

async def run_parallel_analysis():
    start_time = time.time()
    
    # 1. Start multiple tasks concurrently (Gather)
    print("--- 🧠 Starting Multi-Expert Analysis ---")
    results = await asyncio.gather(
        mock_ai_call("Data Scientist", 2),
        mock_ai_call("Security Specialist", 3),
        mock_ai_call("Legal Advisor", 1.5)
    )
    
    # 2. Parse and summarize results
    print("\n--- 📊 Summary Report ---")
    for r in results:
        data = json.loads(r)
        print(f"Expert: {data['expert']} | Result: {data['content']}")
        
    end_time = time.time()
    print(f"\n✅ Total time taken: {end_time - start_time:.2f} seconds.")
    print("(Notice: Total time is roughly the maximum of individual delays, not the sum!)")

if __name__ == "__main__":
    asyncio.run(run_parallel_analysis())
```

---

## 💡 老師的建議 (必看)
1. **JSON 報錯**：LLM 有時會輸出不標準的 JSON（例如多了個逗號或換行）。後續我們會學 `Pydantic` 來解決這個問題。
2. **不要在異步代碼中用 `time.sleep`**：這會阻塞整個事件循環。必須使用 `await asyncio.sleep`。
3. **異步的好處**：當你需要同時總結 10 篇文章時，異步會比循環快 10 倍！

---

## 📝 本日練習
1. 使用 `requests` 庫嘗試調用一個免費的 API（例如：百度、騰訊、或通義千問的 API 地址）。
2. 修改 `run_parallel_analysis` 代碼，讓它不僅打印結果，還要把所有結果合併到一個名為 `final_report.json` 的文件中保存。
3. 思考：如果某個 AI 調用超時了，異步代碼該如何處理？（提示：關鍵詞 `asyncio.wait_for`）。
