# 自动化评测 (Eval Runner) 开发计划

## 1. 核心知识点解答

### 1.1 Python 文件中怎么引入 YAML 来进行遍历对比？

在 Python 中，我们使用第三方库 `PyYAML`。它的核心功能是将 YAML 文件的结构转化为 Python 原生的数据结构（如字典和列表）。

**实现步骤**：

1. 导入库：`import yaml`
2. 读取并反序列化：使用 `with open(...)` 打开文件，并用 `yaml.safe_load(f)` 将其读取为 Python 字典。
3. 遍历提取：一旦变成字典，就可以通过 `.get("cases", [])` 拿到用例列表，然后通过简单的 `for` 循环遍历对比。

**简单示例**：

```python
import yaml

with open("eval/test_cases.yaml", "r", encoding="utf-8") as f:
    test_data = yaml.safe_load(f)

for case in test_data.get("cases", []):
    print(case["id"])          # 获取用例ID
    print(case["expected"])    # 获取预期规则字典，用于后续与大模型回复做对比
```

### 1.2 命令行参数怎么在 Python 文件中获取？

获取如 `python -m eval.runner --version 1.1 --compare` 中的参数，最规范的做法是使用标准库 `argparse`。

**参数分类处理**：

- **带值的参数（如 `--version 1.1`）**：定义时需要声明 `type=str`，它会自动捕获后面的值，用 `args.version` 获取。
- **开关型参数（如 `--compare`）**：这是个布尔型开关，带上它即为 True。定义时需声明 `action="store_true"`。

**简单示例**：

```python
import argparse

parser = argparse.ArgumentParser(description="Eval Runner")
parser.add_argument("--version", type=str, help="指定 Prompt 版本号")
parser.add_argument("--compare", action="store_true", help="是否进行版本对比")

args = parser.parse_args()

if args.compare:
    print("开启对比模式")
elif args.version:
    print(f"运行版本: {args.version}")
```

---

### 1.3. 评分应该遵循什么原则？

应该围绕测试用例中的 `expected` 字段展开，遵循以下四个维度的原则：

1. must_contain（召回正确性）  
   **原则**：AI 回答的文本内容必须 100% 包含此列表中定义的所有关键词。  
   **作用**：确保模型正面回答了问题，并且命中了关键业务信息（比如问到个人项目，必须出现 "Talk to sophie"）。
2. must_not_contain（反幻觉/安全防范）  
   **原则：**AI 回答的文本内容绝对不能包含此列表中的任何词汇。  
   **作用：**防止模型编造你没有的技能（比如你用 React，不能让它回答 Vue），以及验证在 refusal（拒绝）类的 case 中，模型是否被恶意引导。
3. should_cite（知识溯源准确性 Grounding）  
   **原则：**回答中附带的引用源（Sources）必须包含列表中指定的文件名。  
   **作用：**验证 RAG 系统的检索能力是否准确，模型是不是真的依据 01-profile.md 或 clp.md 作答，而不是靠通用预训练记忆在瞎猜。
4. max_length（输出约束/风格控制）  
   **原则：**AI 最终回复的文本长度不应超过这个阈值（len(response.text) <= max_length）。  
   **作用：**限制大模型不要过度啰嗦，保持 AI 分身回答的简洁性（符合 prompt 中 不超过 200 字 的人设）。评分实现的小建议： 你可以用一个计分板的方式。每个 case 如果全部满足以上条件就算 Pass，只要有一条不满足就算 Fail，并记录下是哪个约束条件导致了 Fail，最后交给 print_report 将详细结果打印出来。

## 2. 今天的实操任务

> 以下是为你独立编写评测脚本提供的可对照目标代码。你可以先自己尝试实现，卡壳时再参考这里的逻辑。

### 2.1 计分器参考代码 (`server/eval/scorers.py`)

此文件根据 `test_cases.yaml` 中的期望条件，对单次回复进行多维度判定。

```python
def score_response(case: dict, response_text: str, sources: list) -> dict:
    """
    目标返回：{
        "passed": True/False,
        "detail": {
            "must_contain": {"React": True/False, "TypeScript": True/False},
            "must_not_contain": {"Java": True/False},
            "should_cite": {"02-skills.md": True/False},
            "within_len_limit": True/False
        },
        "fail_reasons": []
    }
    """
    expected = case.get("expected", {})

    # 初始化返回结构
    result = {
        "passed": True,
        "detail": {
            "must_contain": {},
            "must_not_contain": {},
            "should_cite": {},
            "within_len_limit": True
        },
        "fail_reasons": []
    }

    if not expected:
        return result

    # 1. 判定 must_contain
    for word in expected.get("must_contain", []):
        passed = word in response_text
        result["detail"]["must_contain"][word] = passed
        if not passed:
            result["passed"] = False
            result["fail_reasons"].append(f"未包含必填词汇: '{word}'")

    # 2. 判定 must_not_contain
    for word in expected.get("must_not_contain", []):
        passed = word not in response_text
        result["detail"]["must_not_contain"][word] = passed
        if not passed:
            result["passed"] = False
            result["fail_reasons"].append(f"包含违禁词汇: '{word}'")

    # 3. 判定 should_cite (溯源检查)
    sources_str = str(sources) # 转为字符串便于做全文关键词搜索
    for cite in expected.get("should_cite", []):
        passed = cite in sources_str
        result["detail"]["should_cite"][cite] = passed
        if not passed:
            result["passed"] = False
            result["fail_reasons"].append(f"未引用正确知识库: '{cite}'")

    # 4. 判定 max_length
    max_len = expected.get("max_length")
    if max_len is not None:
        actual_len = len(response_text)
        passed = actual_len <= max_len
        result["detail"]["within_len_limit"] = passed
        if not passed:
            result["passed"] = False
            result["fail_reasons"].append(f"长度超出限制 (当前: {actual_len}, 最大允许: {max_len})")

    return result
```

### 2.2 运行器参考代码 (`server/eval/runner.py`)

此文件串联用例读取、调用接口和打印打分结果的完整生命周期。

```python
import yaml
import argparse
import asyncio
import httpx
from eval.scorers import score_response

async def run_single_case(case: dict, prompt_version: str) -> dict:
    """调用内部chat逻辑拿到完整回复+sources"""
    # 这里以 httpx 请求你的 FastAPI 为例，如果是本地直调函数则替换为本地函数调用
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                "http://127.0.0.1:8000/api/chat",
                json={"message": case["input"]},
                headers={"X-Prompt-Version": prompt_version}
            )
            data = resp.json()
            return {
                "text": data.get("text", ""),
                "sources": data.get("sources", [])
            }
    except Exception as e:
        return {"text": f"请求失败: {e}", "sources": []}

async def run_eval(prompt_version: str) -> dict:
    """1-4: 完整遍历打分流程"""
    with open("eval/test_cases.yaml", "r", encoding="utf-8") as f:
        test_data = yaml.safe_load(f)

    cases = test_data.get("cases", [])
    report = {"total": len(cases), "passed": 0, "failed_cases": []}

    for case in cases:
        print(f"🔄 正在运行测试用例: {case['id']}")
        res = await run_single_case(case, prompt_version)
        score = score_response(case, res["text"], res["sources"])

        if score["passed"]:
            report["passed"] += 1
            print("   ✅ Pass")
        else:
            print(f"   ❌ Fail: {', '.join(score['fail_reasons'])}")
            report["failed_cases"].append({
                "id": case["id"],
                "input": case["input"],
                "reasons": score["fail_reasons"],
                "actual_text": res["text"]
            })

    await print_report(report)
    return report

async def print_report(report: dict):
    """终端打印通过率+失败用例详情"""
    print("\n" + "="*40)
    print(f"🎯 评测报告 | 总数: {report['total']} | 通过: {report['passed']} | 失败: {len(report['failed_cases'])}")
    print("="*40)
    if report['failed_cases']:
        print("🚨 失败详情:")
        for fail in report['failed_cases']:
            print(f"  [{fail['id']}] {fail['input']}")
            print(f"  原因: {', '.join(fail['reasons'])}")
            print(f"  实际输出: {fail['actual_text'][:100]}...\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Eval Runner")
    parser.add_argument("--version", type=str, help="指定 Prompt 版本 (如 1.0 或 1.1)")
    parser.add_argument("--compare", action="store_true", help="对比两个版本")

    args = parser.parse_args()

    if args.compare:
        print("尚未实现对比功能。")
    elif args.version:
        asyncio.run(run_eval(args.version))
    else:
        parser.print_help()
```
