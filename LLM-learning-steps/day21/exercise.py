# 🌰将一段非结构化的自我介绍文本变成整齐的 Python 对象。
import os
import json
from pydantic import BaseModel, Field
from typing import List, Optional
from http import HTTPStatus
# 导入dashscope
from dashscope import Generation
import dashscope

# 尝试导入 dashscope，如果失败给出提示
try:
    from dashscope import Generation
except ImportError:
    print("错误: 请先安装 dashscope: pip install dashscope")
    exit(1)

# 直接设置API Key
dashscope.api_key = 'sk-59c5b66dbe244feaaa26dabb23c5616b'

# 验证是否设置成功（可选）
print(f"API Key已设置: {dashscope.api_key[:10]}...")  # 只显示前10个字符

# 使用basemodel定义一个Resume类
class Resume(BaseModel):
    name: str = Field(..., description="姓名")
    gender: Optional[str] = Field(None, description="性别")  # 改为可选
    college: str = Field(..., description="学校")  # 修正拼写: collage -> college
    working_years: int = Field(5, description="工作年限")  # 保持字段名一致
    skills: List[str] = Field(..., description="技能列表")


# 方法extract_resume_info
def extract_resume_info(introduction: str):
    # 改进的prompt
    prompt = f"""
    请将以下自我介绍文本中的信息提取出来，并以JSON格式返回。
    
    要求的JSON格式：
    {{
        "name": "姓名",
        "gender": "性别（如果未提及则省略）",
        "college": "毕业学校",
        "working_years": 工作年限（数字）,
        "skills": ["技能1", "技能2", "..."]
    }}
    
    请只返回JSON，不要包含其他解释文字。
    
    文本内容：{introduction}
    """

    # 写message
    messages = [
        {'role': 'system', 'content': '你是一个简历信息提取助手，只能返回JSON格式的结果。'},
        {'role': 'user', 'content': prompt}
    ]

    try:
        # 使用正确的模型名称 - qwen-turbo 是最常用的
        response = Generation.call(
            model='qwen-turbo',  # 修正模型名称
            messages=messages,   # 注意是 messages 不是 message
            result_format='message',
            temperature=0.1  # 降低随机性，获得更稳定的输出
        )
    except Exception as e:
        return f"API调用失败: {str(e)}"

    if response.status_code == HTTPStatus.OK:
        content = response.output.choices[0].message.content
        print(f"原始返回: {content}")  # 调试用
        
        # 清理返回内容
        clean_content = content.replace('```json', '').replace('```', '').strip()
        
        # 使用pydantic的model_validate_json方法（parse_raw已弃用）
        try:
            resume = Resume.model_validate_json(clean_content)
            return resume
        except Exception as e:
            return f"解析JSON失败: {str(e)}\n原始内容: {clean_content}"
    else:
        return f"请求失败: {response.status_code} - {response.message}"
    

# --- Main ---
if __name__ == "__main__":
    raw_text = "我叫张三，在 IT 行业摸爬滚打 5 年了。精通 Python、Docker 和 Kubernetes。本科毕业于清华大学。"
    print("⏳ 正在分析文本...")
    print(f"文本内容: {raw_text}\n")
    
    result = extract_resume_info(raw_text)
    
    if isinstance(result, Resume):
        print("\n✅ 提取成功：")
        print(f"姓名: {result.name}")
        print(f"学校: {result.college}")  # 修正字段名
        print(f"工作年限: {result.working_years}年")  # 修正字段名
        print(f"技能: {', '.join(result.skills)}")
    else:
        print(f"\n❌ 提取失败: {result}")