# Day 5：异步编程深度对比（TS `Promise` ➡️ Python `asyncio`）
## 🎯 今日目标**：掌握 Python 的异步协程与事件循环。
*   **💡 核心映射**：
    *   **运行机制**：TS/JS 的事件循环是运行时底层的隐式机制，而 Python 需要显式通过 `asyncio.run(main())` 启动。
    *   **并发控制**：`Promise.all([p1, p2])` ➡️ `asyncio.gather(task1, task2)`。
*   **⚠️ 避坑指南**：注意 GIL（全局解释器锁，规定同一时刻只能够一个线程能够执行python的字节码）的存在。Python 异步非常适合 I/O 密集型任务（如 API 请求、数据库读取），但不适合 CPU 密集型任务（需要使用 `multiprocessing`）。
*   **📚 学习资料**：
    *   [Real Python: Async IO in Python Complete Walkthrough](https://realpython.com/async-io-python/)
    *   [Python 官方 asyncio 库指南](https://docs.python.org/3/library/asyncio.html)


## 学习笔记📒

### 运行机制
 理解TS/JS默认会在循环里面的，默认就是异步的。   
 而python默认是同步的，想要一步的时间生效要通过 `asyncio.run()` 启动。     
 ** 🧠`asyncio` 又是跑在单线程里🧠 ** 
 当你调用 `asyncio.run()` 时，Python 只创建了一个主线程。在这个线程里，所有的协程（Coroutine）轮流使用 CPU。 


### 并发控制
 看一个`ts` & `python`处理文件的例子
 ```ts
import fs from 'node:fs/promises';

// 1. 定义一个异步函数 (返回 Promise)
async function readFiles() {
  console.log('开始读取...');

  // 2. 并发发起两个读取操作
  //    Promise.all 接收两个 Promise，它们同时进入“等待”状态
  const [contentA, contentB] = await Promise.all([
    fs.readFile('./a.txt', 'utf-8'),
    fs.readFile('./b.txt', 'utf-8')
  ]);

  console.log('A 内容:', contentA);
  console.log('B 内容:', contentB);
}

// 3. 关键点：直接调用即可！
//    因为 Node.js 进程启动时，底层的事件循环已经自动在后台空转等待了。
//    调用 readFiles() 只是往这个已经在跑的事件循环里“扔”了一个任务。
readFiles(); 

// 4. 主线程同步代码继续执行
console.log('主线程不会阻塞，这行会先打印');

// 执行顺序：
// 1. "开始读取..."
// 2. "主线程不会阻塞，这行会先打印"
// 3. (等待约几毫秒) "A 内容: ..." "B 内容: ..."
```

```py
import asyncio
import aiofiles  # 异步读取文件的第三方库

# 1. 定义一个异步函数 (返回协程对象)
async def read_files():
    print("开始读取...")
    
    # 2. 并发发起两个读取操作
    #    asyncio.gather 并发运行两个协程
    
    # ✅ 正确：同时打开两个文件，再同时读取
    async with aiofiles.open('a.txt', 'r', encoding='utf-8') as f1, \
                aiofiles.open('b.txt', 'r', encoding='utf-8') as f2:
        # 同时发起两个读取任务
        task1 = f1.read()   # 创建协程对象
        task2 = f2.read()   # 创建协程对象
        content_a, content_b = await asyncio.gather(task1, task2)  # 并发执行
    
    print("A 内容:", content_a)
    print("B 内容:", content_b)

# 3. 关键点：此时 read_files() 只是一个对象，什么都没发生！
#    如果直接调用 read_files()，只会得到一个 <coroutine object>，控制台无输出。
#    read_files()  # 直接调用无效！

# 4. 必须显式创建并启动事件循环
if __name__ == "__main__":
    # Python 接收到这行指令，才会去创建循环、运行协程、结束后销毁循环
    asyncio.run(read_files())

print("主线程代码...")  # 注意：这行会在 asyncio.run() 完全结束后才执行

# 执行顺序：
# 1. "开始读取..."
# 2. (等待约几毫秒) "A 内容: ..." "B 内容: ..."
# 3. "主线程代码..."
```


### CPU 密集型 VS I/O 密集型

| 维度 | I/O 密集型 | CPU 密集型 |
| :--- | :--- | :--- |
| **举例** | 比如做网络请求、数据库查询 | 比如循环计算 1+1 一亿次 |
| **解决方案** | asyncio| multiprocessing（多进程） |
| **原理** | 单线程事件循环，避开 GIL，用极低的内存开销处理上万连接| 	每个进程有独立的 GIL 和 Python 解释器，利用多核 CPU 真正并行计算 |

#### 代码示例
```py
# ❌使用异步做计算的错误写法❌
async def bad_example():
    for i in range(1000000):  # 纯 CPU 计算
        i ** 2
    # 没有 await，事件循环被卡死，其他所有协程无法运行
```
```py
# ✅正确写法（将 CPU 任务扔给进程池->multiprocessing）✅：
import asyncio
import multiprocessing

def cpu_bound_task(n):
    # 这是普通同步函数，会单独在一个子进程中运行
    return sum(i * i for i in range(n))

async def main():
    loop = asyncio.get_running_loop()
    # 把 CPU 任务交给进程池执行，用 await 等待结果

    # loop.run_in_executor()：这是事件循环提供的方法，作用是把同步阻塞任务丢到另一个线程/进程里去执行，不让它卡住事件循环。
    result = await loop.run_in_executor(
        # multiprocessing.Pool(4)：创建一个进程池，里面预置了 4 个子进程（类似于雇佣了 4 个临时工）。
        multiprocessing.Pool(4),  
        # 子进程计算：其中一个子进程执行 cpu_bound_task(10_000_000)，跑满一个 CPU 核心。
        cpu_bound_task,
        10_000_000
    )
    print(result)
```

#### `multiprocessing`

 一、基础概念（先记住 3 个核心）   

| 概念 | 说明 | 类比 |
| :--- | :--- | :--- |
| **Process**（进程） | 一个独立的 Python 解释器实例 | 一个独立的厨房 |
| **Pool**（进程池） | 预先创建好一批进程，重复使用 | 一个厨师团队，随叫随到 |
| **Queue**（队列） | 进程间安全地传递数据 | 厨房和前台之间的传菜窗口 |

---

##### 用法 1：创建单个进程（`Process` 类）

**适用场景**：只需要启动 1~2 个子进程，不需要大量重复任务。

```python
import multiprocessing
import os

def worker(name, num):
    """子进程要执行的函数"""
    print(f"子进程 {name} (PID: {os.getpid()}) 开始计算...")
    result = sum(i * i for i in range(num))
    print(f"子进程 {name} 计算结果: {result}")
    return result  # 注意：Process 不能直接获取返回值！

if __name__ == "__main__":
    # 1. 创建进程对象
    p1 = multiprocessing.Process(
        target=worker,          # 要执行的函数
        args=("进程A", 1000000)  # 传递给函数的参数（必须是元组）
    )
    p2 = multiprocessing.Process(
        target=worker,
        args=("进程B", 2000000)
    )
    
    # 2. 启动进程
    p1.start()
    p2.start()
    
    # 3. 等待进程结束（让整个p1 p2跑完之后再继续下面的代码执行）
    p1.join()
    p2.join()
    
    print("所有子进程执行完毕")
```

**语法要点**：
-   `Process(target=函数名, args=(参数1, 参数2))`：参数必须用元组，即使只有一个参数也要加逗号 `(param,)`。
-   `start()`：启动子进程，**非阻塞**（立刻返回）。
-   `join()`：阻塞主进程，等待子进程结束。
-   **缺点**：`Process` 无法直接获取子进程的返回值（需要用 `Queue` 或 `Pipe`）。

---

##### 用法 2：进程池（`Pool` 类）—— 最常用！

**适用场景**：需要执行大量相似任务（如批量处理图片、批量计算）。

2.1 基础用法：`map()` 批量分发

```python
import multiprocessing

def cpu_bound_task(n):
    """CPU 密集型任务"""
    return sum(i * i for i in range(n))

if __name__ == "__main__":
    # 1. 创建进程池（默认使用 CPU 核心数）
    with multiprocessing.Pool(processes=4) as pool:
        # 2. map：把列表中的每个元素分给进程池执行
        #    4 个进程会同时计算 1000万, 2000万, 3000万, 4000万
        results = pool.map(cpu_bound_task, [10_000_000, 20_000_000, 30_000_000, 40_000_000])
        
        # 3. 结果按输入顺序返回
        print(results)  # [结果1, 结果2, 结果3, 结果4]
```


