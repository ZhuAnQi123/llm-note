"""
带记忆的Chatbot - 同时支持短期记忆和长期记忆
需要安装：pip install langgraph langchain-openlangchain langchain_core
需要设置OPENAI_API_KEY环境变量
"""

import os
from typing import Annotated, List, Dict
import operator
from datetime import datetime

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# ========== 1. 配置 ==========
# 设置您的OpenAI API Key
os.environ["OPENAI_API_KEY"] = "your-openai-api-key-here"  # 替换为您的key

# 初始化LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7
)

# ========== 2. 定义状态 ==========
class State:
    """Agent的状态 - 会在每次会话中自动保存（短期记忆）"""
    messages: Annotated[List[Dict], operator.add]  # 对话历史
    summary: str  # 对话摘要（当历史过长时使用）
    user_id: str  # 用户ID（用于长期记忆）

# ========== 3. 定义节点函数 ==========

def extract_user_preferences(state: State, runtime):
    """节点1：从对话中提取用户偏好（写入长期记忆）"""
    messages = state.get("messages", [])
    user_id = state.get("user_id", "default_user")
    
    if not messages:
        return {}
    
    # 获取最后一条用户消息
    last_user_msg = None
    for msg in reversed(messages):
        if msg.get("type") == "human" or msg.get("role") == "user":
            last_user_msg = msg.get("content", "")
            break
    
    if not last_user_msg:
        return {}
    
    # 使用LLM判断是否需要记录偏好
    extract_prompt = f"""
    分析用户消息，判断是否包含可长期记忆的个人信息或偏好。
    如果有，提取出来；如果没有，返回空对象。
    
    用户消息："{last_user_msg}"
    
    可提取的信息类型：
    - 姓名、年龄、职业
    - 兴趣爱好（喜欢什么）
    - 饮食偏好（喜欢/不喜欢吃什么）
    - 生活习惯
    - 其他个人信息
    
    返回格式（JSON）：
    {{"has_memory": true/false, "key": "偏好类型", "value": "具体内容"}}
    
    只返回JSON，不要有其他内容。
    """
    
    try:
        response = llm.invoke(extract_prompt)
        import json
        # 清理可能的markdown标记
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        result = json.loads(content.strip())
        
        if result.get("has_memory"):
            # 保存到长期记忆
            namespace = ("user_profiles", user_id)
            # 读取现有记忆
            existing = runtime.store.get(namespace, "preferences")
            preferences = existing.value if existing else {}
            
            # 更新偏好
            key = result.get("key")
            value = result.get("value")
            if key and value:
                preferences[key] = {
                    "value": value,
                    "timestamp": datetime.now().isoformat()
                }
                runtime.store.put(namespace, "preferences", preferences)
                print(f"💾 已保存长期记忆：{key} = {value}")
    except Exception as e:
        print(f"提取偏好时出错：{e}")
    
    return {}

def load_long_term_memory(state: State, runtime):
    """节点2：加载长期记忆，注入到系统提示中"""
    user_id = state.get("user_id", "default_user")
    
    # 从长期记忆读取用户画像
    namespace = ("user_profiles", user_id)
    profile_data = runtime.store.get(namespace, "preferences")
    
    memory_context = ""
    if profile_data and profile_data.value:
        preferences = profile_data.value
        memory_context = "\n我知道的关于你的信息：\n"
        for key, info in preferences.items():
            memory_context += f"- {key}: {info['value']}\n"
    
    # 将长期记忆作为系统消息注入
    system_msg = SystemMessage(
        content=f"你是一个友好的AI助手。{memory_context}\n请基于这些信息提供个性化回复。"
    )
    
    # 注意：这里返回的是要添加到state中的消息
    return {"messages": [system_msg]}

def chatbot_response(state: State):
    """节点3：生成AI回复"""
    messages = state.get("messages", [])
    
    if not messages:
        return {"messages": [AIMessage(content="你好！我是AI助手，有什么可以帮你的吗？")]}
    
    # 调用LLM生成回复
    response = llm.invoke(messages)
    return {"messages": [AIMessage(content=response.content)]}

def check_and_summarize(state: State):
    """节点4：检查对话长度，必要时生成摘要"""
    messages = state.get("messages", [])
    current_summary = state.get("summary", "")
    
    # 当消息超过10条时触发总结（保留最近5条）
    if len(messages) > 10:
        # 构建需要总结的对话内容
        to_summarize = messages[:-5]  # 除最近5条外的所有消息
        
        conversation_text = ""
        for msg in to_summarize:
            role = "用户" if msg.get("type") == "human" or msg.get("role") == "user" else "AI"
            content = msg.get("content", "")
            conversation_text += f"{role}: {content}\n"
        
        summary_prompt = f"""
        请总结以下对话的关键信息，保留重要事实和上下文：
        
        {conversation_text}
        
        已有摘要：{current_summary if current_summary else "无"}
        
        请输出更新后的完整摘要（200字以内）：
        """
        
        try:
            response = llm.invoke(summary_prompt)
            new_summary = response.content
            print(f"📝 已生成对话摘要，消息数从{len(messages)}压缩到5条")
            return {
                "summary": new_summary,
                "messages": messages[-5:]  # 只保留最近5条
            }
        except Exception as e:
            print(f"生成摘要失败：{e}")
    
    return {}

# ========== 4. 构建图 ==========

def build_chatbot():
    """构建带记忆的Chatbot图"""
    builder = StateGraph(State)
    
    # 添加节点
    builder.add_node("extract_preferences", extract_user_preferences)
    builder.add_node("load_memory", load_long_term_memory)
    builder.add_node("chatbot", chatbot_response)
    builder.add_node("summarize", check_and_summarize)
    
    # 定义流程
    builder.add_edge(START, "extract_preferences")
    builder.add_edge("extract_preferences", "load_memory")
    builder.add_edge("load_memory", "chatbot")
    builder.add_edge("chatbot", "summarize")
    builder.add_edge("summarize", END)
    
    # 创建短期记忆（自动保存会话状态）
    checkpointer = MemorySaver()
    
    # 创建长期记忆（跨会话保存用户画像）
    store = InMemoryStore()
    
    # 编译
    app = builder.compile(
        checkpointer=checkpointer,
        store=store
    )
    
    return app

# ========== 5. 运行 ==========

def run_chatbot():
    """运行带记忆的Chatbot"""
    app = build_chatbot()
    
    print("=" * 50)
    print("🤖 带记忆的Chatbot已启动")
    print("=" * 50)
    print("功能说明：")
    print("1. 短期记忆：记住本轮对话的所有内容")
    print("2. 长期记忆：记住你的个人信息和偏好（跨会话）")
    print("3. 自动总结：对话过长时自动压缩")
    print("输入 'quit' 退出，输入 'new' 开始新会话\n")
    
    user_id = "test_user_001"  # 实际应用中可以从登录信息获取
    thread_id = "session_001"
    
    config = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": user_id
        }
    }
    
    # 演示长期记忆：加载之前保存的偏好（如果有）
    namespace = ("user_profiles", user_id)
    existing = app.store.get(namespace, "preferences")
    if existing and existing.value:
        print(f"📚 已加载用户画像：{existing.value}\n")
    
    while True:
        user_input = input("\n👤 你: ").strip()
        
        if user_input.lower() == 'quit':
            print("👋 再见！")
            break
        elif user_input.lower() == 'new':
            thread_id = f"session_{datetime.now().timestamp()}"
            config["configurable"]["thread_id"] = thread_id
            print(f"✨ 已开始新会话（thread_id: {thread_id}）")
            continue
        
        if not user_input:
            continue
        
        # 调用Agent
        try:
            result = app.invoke(
                {
                    "messages": [HumanMessage(content=user_input)],
                    "user_id": user_id
                },
                config=config
            )
            
            # 获取AI回复
            if result.get("messages"):
                last_msg = result["messages"][-1]
                if hasattr(last_msg, 'content'):
                    response = last_msg.content
                elif isinstance(last_msg, dict):
                    response = last_msg.get("content", "")
                else:
                    response = str(last_msg)
                print(f"🤖 AI: {response}")
            
            # 可选：显示当前对话状态信息
            state = app.get_state(config)
            if state.values.get("summary"):
                print(f"\n📌 [当前摘要: {state.values['summary'][:100]}...]")
                
        except Exception as e:
            print(f"❌ 出错了：{e}")

# ========== 6. 测试示例 ==========

def test_memory_demo():
    """演示记忆功能的测试函数"""
    print("\n" + "=" * 50)
    print("📋 运行记忆功能演示")
    print("=" * 50)
    
    app = build_chatbot()
    user_id = "demo_user"
    
    # 创建不同会话的配置
    session_1_config = {"configurable": {"thread_id": "session_1", "user_id": user_id}}
    session_2_config = {"configurable": {"thread_id": "session_2", "user_id": user_id}}
    
    # 会话1：告诉AI个人信息
    print("\n【会话1】用户告诉AI个人信息")
    test_conversations = [
        "你好，我叫张三",
        "我是软件工程师",
        "我喜欢吃川菜",
        "我住在北京"
    ]
    
    for msg in test_conversations:
        print(f"👤: {msg}")
        result = app.invoke(
            {"messages": [HumanMessage(content=msg)], "user_id": user_id},
            session_1_config
        )
        response = result["messages"][-1].content if result.get("messages") else "无回复"
        print(f"🤖: {response}\n")
    
    # 查看保存的长期记忆
    namespace = ("user_profiles", user_id)
    saved_memory = app.store.get(namespace, "preferences")
    print(f"\n💾 长期记忆中保存的内容：{saved_memory.value if saved_memory else '无'}")
    
    # 会话2：新会话，AI应该还记得用户信息
    print("\n【会话2】新会话，测试AI是否记得用户")
    result = app.invoke(
        {"messages": [HumanMessage(content="你还记得我叫什么吗？")], "user_id": user_id},
        session_2_config
    )
    response = result["messages"][-1].content
    print(f"👤: 你还记得我叫什么吗？")
    print(f"🤖: {response}")

# ========== 7. 主程序 ==========

if __name__ == "__main__":
    # 检查API Key
    if os.environ.get("OPENAI_API_KEY", "").startswith("your-"):
        print("⚠️  请先设置 OPENAI_API_KEY 环境变量")
        print("   export OPENAI_API_KEY='your-key-here'")
        print("\n或者运行测试模式（不依赖API）：")
        print("   1. 注释掉 run_chatbot()")
        print("   2. 取消注释下面的测试代码")
    else:
        # 选择运行模式
        print("选择运行模式：")
        print("1. 交互式对话")
        print("2. 演示测试")
        choice = input("请输入选择 (1/2): ").strip()
        
        if choice == "1":
            run_chatbot()
        elif choice == "2":
            test_memory_demo()
        else:
            print("无效选择")

# 如果没有API Key，可以用这个简单的模拟版本测试
"""
# 模拟版本（不需要API Key）
class MockLLM:
    def invoke(self, messages):
        class Response:
            content = "这是一个模拟回复。请设置OPENAI_API_KEY来获得真实回复。"
        return Response()

llm = MockLLM()
run_chatbot()
"""