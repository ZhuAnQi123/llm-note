# Python Asyncio 全面指南

## 一、什么是 Asyncio？

Asyncio 是 Python 的异步 I/O 框架，用于编写**并发**代码。它通过**单线程 + 事件循环**的方式实现并发，特别适合处理大量的 I/O 密集型任务（网络请求、文件读写、数据库查询等）。

### 核心概念对比

```python
# 同步执行（传统方式）
def sync_task():
    time.sleep(2)  # 阻塞等待
    return "完成"
# 总时间 = 所有任务时间之和

# 异步执行（Asyncio）
async def async_task():
    await asyncio.sleep(2)  # 非阻塞等待
    return "完成"
# 总时间 ≈ 最慢任务的时间
```

## 二、核心概念详解

### 1. **协程 (Coroutine)**

协程是 Asyncio 的基本单位，用 `async def` 定义。

```python
# 定义协程
async def my_coroutine():
    print("开始执行")
    await asyncio.sleep(1)  # 让出控制权
    print("恢复执行")
    return "结果"

# 协程不会自动执行，需要事件循环驱动
```

### 2. **Awaitable 对象**

可以被 `await` 的对象，包括：
- 协程 (coroutine)
- Task 对象
- Future 对象

```python
async def example():
    # await 协程
    result = await my_coroutine()
    
    # await Task
    task = asyncio.create_task(my_coroutine())
    result = await task
    
    # await Future
    future = asyncio.Future()
    # ... 设置 future 结果
    result = await future
```

### 3. **事件循环 (Event Loop)**

事件循环是 Asyncio 的核心调度器，负责管理和执行协程。

```python
# 获取事件循环的多种方式
import asyncio

# 方式1: 自动管理（推荐）
async def main():
    await asyncio.sleep(1)

asyncio.run(main())  # Python 3.7+

# 方式2: 手动管理（更底层的控制）
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    loop.run_until_complete(main())
finally:
    loop.close()
```

### 4. **Task 任务**

Task 是协程的包装器，用于并发执行。

```python
async def worker(name, delay):
    await asyncio.sleep(delay)
    return f"{name} 完成"

async def task_examples():
    # 创建 Task（立即开始执行）
    task1 = asyncio.create_task(worker("任务1", 2))
    task2 = asyncio.create_task(worker("任务2", 1))
    
    # 等待单个任务
    result = await task1
    
    # 等待多个任务
    results = await asyncio.gather(task1, task2)
    
    # 等待第一个完成
    done, pending = await asyncio.wait(
        [task1, task2], 
        return_when=asyncio.FIRST_COMPLETED
    )
```

## 三、常用 API 详解

### 1. **`asyncio.gather()`** - 并发执行多个任务

```python
async def gather_example():
    tasks = [
        asyncio.create_task(worker("A", 2)),
        asyncio.create_task(worker("B", 1)),
        asyncio.create_task(worker("C", 3))
    ]
    
    # 所有任务完成后返回结果列表（保持顺序）
    results = await asyncio.gather(*tasks)
    print(results)  # ['A 完成', 'B 完成', 'C 完成']
    
    # 处理异常（return_exceptions=True 不抛出异常）
    results = await asyncio.gather(*tasks, return_exceptions=True)
```

### 2. **`asyncio.wait()`** - 更灵活的控制

```python
async def wait_example():
    tasks = [
        asyncio.create_task(worker("A", 2)),
        asyncio.create_task(worker("B", 1)),
        asyncio.create_task(worker("C", 3))
    ]
    
    # 等待所有完成
    done, pending = await asyncio.wait(tasks)
    
    # 等待第一个完成
    done, pending = await asyncio.wait(
        tasks, 
        return_when=asyncio.FIRST_COMPLETED
    )
    
    # 等待第一个异常
    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_EXCEPTION
    )
    
    # 设置超时
    done, pending = await asyncio.wait(tasks, timeout=5)
    
    # 取消未完成的任务
    for task in pending:
        task.cancel()
```

### 3. **`asyncio.create_task()`** vs `asyncio.ensure_future()`

```python
async def create_task_example():
    # 方式1: create_task (Python 3.7+，推荐)
    task = asyncio.create_task(worker("A", 1))
    
    # 方式2: ensure_future (更通用，可以包装多种类型)
    task = asyncio.ensure_future(worker("A", 1))
    
    # 方式3: loop.create_task (旧方式)
    loop = asyncio.get_running_loop()
    task = loop.create_task(worker("A", 1))
```

### 4. **超时控制**

```python
async def timeout_example():
    # 方式1: wait_for
    try:
        result = await asyncio.wait_for(worker("慢任务", 5), timeout=2)
    except asyncio.TimeoutError:
        print("任务超时！")
    
    # 方式2: wait + timeout
    task = asyncio.create_task(worker("慢任务", 5))
    done, pending = await asyncio.wait([task], timeout=2)
    if pending:
        pending.pop().cancel()
    
    # 方式3: timeout (Python 3.11+)
    try:
        async with asyncio.timeout(2):
            result = await worker("慢任务", 5)
    except TimeoutError:
        print("超时！")
```

### 5. **同步原语**

```python
# Lock - 互斥锁
async def lock_example():
    lock = asyncio.Lock()
    
    async with lock:
        # 临界区代码
        await shared_resource_modify()
    
    # 等价于：
    await lock.acquire()
    try:
        await shared_resource_modify()
    finally:
        lock.release()

# Semaphore - 信号量（限制并发数）
async def semaphore_example():
    semaphore = asyncio.Semaphore(3)  # 最多3个并发
    
    async def limited_task(task_id):
        async with semaphore:
            await asyncio.sleep(1)
            print(f"任务 {task_id} 完成")
    
    tasks = [limited_task(i) for i in range(10)]
    await asyncio.gather(*tasks)

# Queue - 生产者-消费者模式
async def queue_example():
    queue = asyncio.Queue(maxsize=10)
    
    # 生产者
    async def producer():
        for i in range(20):
            await queue.put(i)
            print(f"生产: {i}")
        await queue.put(None)  # 结束信号
    
    # 消费者
    async def consumer():
        while True:
            item = await queue.get()
            if item is None:
                break
            print(f"消费: {item}")
            queue.task_done()
    
    await asyncio.gather(producer(), consumer())

# Event - 事件通知
async def event_example():
    event = asyncio.Event()
    
    async def waiter():
        print("等待事件...")
        await event.wait()
        print("事件触发！")
    
    async def setter():
        await asyncio.sleep(2)
        event.set()
        print("已设置事件")
    
    await asyncio.gather(waiter(), setter())
```

## 四、实际应用场景

### 场景1: 批量网络请求

```python
import aiohttp

async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.text()

async def batch_fetch(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

# 使用
urls = ['https://api.example.com/1', 'https://api.example.com/2']
results = asyncio.run(batch_fetch(urls))
```

### 场景2: 带重试的并发处理

```python
from tenacity import retry, stop_after_attempt, wait_exponential

class AsyncProcessor:
    def __init__(self, max_concurrent=5):
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1))
    async def process_item(self, item):
        async with self.semaphore:
            # 模拟处理
            await asyncio.sleep(0.1)
            return f"处理完成: {item}"
    
    async def process_batch(self, items):
        tasks = [self.process_item(item) for item in items]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 分离成功和失败的结果
        successes = [r for r in results if not isinstance(r, Exception)]
        failures = [r for r in results if isinstance(r, Exception)]
        
        return successes, failures

# 使用
processor = AsyncProcessor(max_concurrent=10)
items = list(range(100))
successes, failures = asyncio.run(processor.process_batch(items))
```

### 场景3: 流式处理大数据

```python
async def stream_processor(data_source, chunk_size=1000):
    """流式处理大数据，避免内存爆炸"""
    results = []
    
    # 使用队列作为缓冲区
    queue = asyncio.Queue(maxsize=10)
    
    # 生产者：从数据源读取
    async def producer():
        for i in range(0, len(data_source), chunk_size):
            chunk = data_source[i:i+chunk_size]
            await queue.put(chunk)
        await queue.put(None)  # 结束信号
    
    # 消费者：处理数据块
    async def consumer(consumer_id):
        while True:
            chunk = await queue.get()
            if chunk is None:
                queue.task_done()
                break
            
            # 处理数据块
            processed = await process_chunk(chunk)
            results.append(processed)
            queue.task_done()
    
    # 启动多个消费者
    consumers = [consumer(i) for i in range(5)]
    await asyncio.gather(producer(), *consumers)
    
    return results
```

### 场景4: 超时和取消操作

```python
async def robust_operation():
    """带有超时和优雅取消的操作"""
    task = None
    
    try:
        # 设置超时
        task = asyncio.create_task(long_running_operation())
        result = await asyncio.wait_for(task, timeout=30)
        return result
        
    except asyncio.TimeoutError:
        print("操作超时，正在取消...")
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                print("任务已取消")
        raise
        
    except asyncio.CancelledError:
        print("操作被取消")
        # 清理资源
        if task and not task.done():
            task.cancel()
        raise
```

## 五、常见陷阱和最佳实践

### ❌ 常见错误

```python
# 错误1: 忘记 await
async def bad1():
    task = asyncio.create_task(worker())  # 创建任务
    # 忘记 await，任务可能不会执行完成
    return task  # 返回的是 Task 对象，不是结果

# 错误2: 在同步函数中调用异步代码
def bad2():
    asyncio.sleep(1)  # 错误！这会返回一个协程对象，不会执行

# 错误3: 混用 time.sleep 和 asyncio.sleep
async def bad3():
    time.sleep(1)  # 这会阻塞整个事件循环！
    await asyncio.sleep(1)  # 正确

# 错误4: 创建太多任务导致资源耗尽
async def bad4():
    tasks = []
    for i in range(10000):
        tasks.append(asyncio.create_task(heavy_task()))  # 可能耗尽内存
    await asyncio.gather(*tasks)  # 应该使用 Semaphore 限制并发
```

### ✅ 最佳实践

```python
# 实践1: 使用 asyncio.run() 作为主入口
async def main():
    # 你的异步代码
    pass

if __name__ == "__main__":
    asyncio.run(main())

# 实践2: 使用 Semaphore 限制并发
async def limited_concurrent(tasks, limit=10):
    semaphore = asyncio.Semaphore(limit)
    
    async def bounded_task(task):
        async with semaphore:
            return await task
    
    return await asyncio.gather(*[bounded_task(t) for t in tasks])

# 实践3: 优雅地处理取消和清理
async def with_cleanup():
    resource = None
    try:
        resource = await acquire_resource()
        await use_resource(resource)
    except asyncio.CancelledError:
        print("任务被取消，清理资源...")
        raise
    finally:
        if resource:
            await release_resource(resource)

# 实践4: 使用 asyncio.current_task() 调试
async def debug_task():
    task = asyncio.current_task()
    print(f"当前任务: {task.get_name()}")
    print(f"是否取消: {task.cancelled()}")
```

## 六、性能对比示例

```python
import time

# 模拟 I/O 密集型任务
async def io_task(name, delay):
    await asyncio.sleep(delay)
    return name

# 同步版本
def sync_version():
    start = time.time()
    for i in range(5):
        time.sleep(1)  # 模拟 I/O
    return time.time() - start

# 异步版本
async def async_version():
    start = time.time()
    tasks = [io_task(f"任务{i}", 1) for i in range(5)]
    await asyncio.gather(*tasks)
    return time.time() - start

# 对比
sync_time = sync_version()
async_time = asyncio.run(async_version())
print(f"同步耗时: {sync_time:.2f}秒")   # ~5秒
print(f"异步耗时: {async_time:.2f}秒")  # ~1秒
```

## 七、调试和监控

```python
import logging

# 启用调试模式
async def debug_mode():
    loop = asyncio.get_running_loop()
    loop.set_debug(True)
    
    # 设置慢回调阈值
    loop.slow_callback_duration = 0.1
    
    # 配置日志
    logging.basicConfig(level=logging.DEBUG)

# 监控任务状态
async def monitor_tasks():
    while True:
        tasks = asyncio.all_tasks()
        print(f"活跃任务数: {len(tasks)}")
        for task in tasks:
            print(f"  - {task.get_name()}: {task._state}")
        await asyncio.sleep(1)

# 超时监控
async def with_timeout_monitor(coro, timeout):
    try:
        return await asyncio.wait_for(coro, timeout)
    except asyncio.TimeoutError:
        print(f"操作超过 {timeout} 秒未完成")
        # 打印当前堆栈用于调试
        for task in asyncio.all_tasks():
            task.print_stack()
        raise
```

## 总结

**Asyncio 的核心优势：**
1. **高并发**：单线程处理数千个连接
2. **低开销**：比多线程更少的内存和上下文切换
3. **可预测**：没有竞态条件（单线程）

**适用场景：**
- Web 爬虫、API 调用
- Web 服务器（FastAPI、Sanic）
- 聊天服务器、实时应用
- 数据库批量操作
- 任何 I/O 密集型任务

**不适用场景：**
- CPU 密集型任务（应使用多进程）
- 简单的脚本（同步更简单）

掌握 Asyncio 需要理解"协作式多任务"的核心思想：任务主动让出控制权（通过 await），而不是被操作系统抢占。