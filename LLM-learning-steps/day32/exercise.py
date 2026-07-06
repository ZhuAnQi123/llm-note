import os
from langchain_community.chat_models import ChatDashScope
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.memory import ConversationSummaryMemory
from langchain.chains import LLMChain
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from typing import List, Dict
from collections import defaultdict

# ========== 1. 自定义混合记忆类 ==========
class LimitedSummaryMemory:
    """
    混合记忆：保留最近10条原始消息 + 对更早消息进行摘要
    """
    def __init__(self, model, max_raw_messages: int = 10):
        self.model = model
        self.max_raw_messages = max_raw_messages  # 最多保留10条原始消息
        self.raw_messages: List[BaseMessage] = []  # 原始消息列表
        self.summary: str = ""  # 早期对话的摘要
        self.secret_triggered = False  # 是否触发秘密规则
        
    def add_message(self, message: BaseMessage):
        """添加消息并自动管理记忆"""
        self.raw_messages.append(message)
        
        # 检查是否触发秘密规则
        if not self.secret_triggered and isinstance(message, HumanMessage):
            if "秘密" in message.content:
                self.secret_triggered = True
                print("🔐 秘密模式已触发！")
        
        # 如果超过限制，将最早的消息压缩成摘要
        if len(self.raw_messages) > self.max_raw_messages:
            self._compress_oldest_messages()
    
    def _compress_oldest_messages(self):
        """将超过限制的最早消息压缩成摘要"""
        # 取出超过限制的消息（按照保留最近 N 条的原则）
        excess_count = len(self.raw_messages) - self.max_raw_messages
        messages_to_summarize = self.raw_messages[:excess_count]
        
        # 构建摘要 prompt
        if messages_to_summarize:
            # 将旧消息转换为文本
            old_conversation = "\n".join([
                f"{'用户' if isinstance(m, HumanMessage) else 'AI'}: {m.content}"
                for m in messages_to_summarize
            ])
            
            # 生成摘要
            summary_prompt = ChatPromptTemplate.from_messages([
                ("system", "请用2-3句话总结以下对话的核心内容，保留关键信息："),
                ("user", old_conversation)
            ])
            chain = summary_prompt | self.model
            new_summary = chain.invoke({}).content
            
            # 合并摘要
            if self.summary:
                self.summary = f"【早期对话摘要】{self.summary}\n【新增摘要】{new_summary}"
            else:
                self.summary = f"【对话摘要】{new_summary}"
            
            # 移除已压缩的消息
            self.raw_messages = self.raw_messages[excess_count:]
    
    def get_messages(self):
        """获取完整的消息列表（摘要 + 原始消息）"""
        messages = []
        
        # 如果有摘要，添加为系统消息
        if self.summary:
            messages.append(SystemMessage(
                content=f"【历史对话摘要】\n{self.summary}\n\n请基于以上摘要和接下来的对话继续回答。"
            ))
        
        # 添加原始消息
        messages.extend(self.raw_messages)
        return messages
    
    def clear(self):
        """清空记忆"""
        self.raw_messages = []
        self.summary = ""


# ========== 2. 准备模型 ==========
model = ChatDashScope(model_name="qwen-turbo")

# ========== 3. 准备带占位符的 Prompt ==========
prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个幽默风趣的 AI 助手。
    
【特殊规则】
⚠️ 如果用户提到过"秘密"，或者你已经触发了秘密模式，请在后续**所有回复**中都带上一个 🎭 表情符号。
    - 示例回复：这个问题很有趣呢 🎭
    - 即使问题与秘密无关，也要带上 🎭
    
如果用户没有触发秘密模式，正常回复即可。
"""),
    MessagesPlaceholder(variable_name="history"),  # 历史记录注入点
    ("user", "{input}")
])

# ========== 4. 构建基础链 ==========
chain = prompt | model

# ========== 5. 自定义记忆管理器 ==========
class CustomHistoryManager:
    """管理多个会话的记忆"""
    def __init__(self, model, max_raw_messages: int = 10):
        self.model = model
        self.max_raw_messages = max_raw_messages
        self.store: Dict[str, LimitedSummaryMemory] = {}
    
    def get_session_history(self, session_id: str) -> LimitedSummaryMemory:
        if session_id not in self.store:
            self.store[session_id] = LimitedSummaryMemory(
                self.model, 
                self.max_raw_messages
            )
        return self.store[session_id]
    
    def get_messages_for_prompt(self, session_id: str):
        """获取用于 prompt 的消息格式"""
        memory = self.get_session_history(session_id)
        return memory.get_messages()


# ========== 6. 创建记忆管理器 ==========
memory_manager = CustomHistoryManager(model, max_raw_messages=10)  # 保留最近10条消息

def get_session_history(session_id: str):
    """适配 RunnableWithMessageHistory 的接口"""
    return memory_manager.get_session_history(session_id)


# ========== 7. 创建自定义的 RunnableWithMessageHistory ==========
class CustomRunnableWithMessageHistory(RunnableWithMessageHistory):
    """重写以支持自定义记忆格式"""
    def invoke(self, input_dict, config=None):
        session_id = config.get("configurable", {}).get("session_id")
        if not session_id:
            raise ValueError("必须提供 session_id")
        
        # 获取当前会话的记忆对象
        memory = memory_manager.get_session_history(session_id)
        
        # 获取历史消息（包含摘要和原始消息）
        history_messages = memory.get_messages()
        
        # 构建完整的消息列表
        from langchain_core.messages import HumanMessage
        
        # 使用 prompt 格式化
        messages = self.runnable.first.steps[0].invoke({
            "input": input_dict["input"],
            "history": history_messages  # 注入历史消息
        })
        
        # 调用模型
        response = self.runnable.invoke(messages)
        
        # 保存本轮对话到记忆
        memory.add_message(HumanMessage(content=input_dict["input"]))
        memory.add_message(AIMessage(content=response.content))
        
        return response


# ========== 8. 主程序 ==========
if __name__ == "__main__":
    config = {"configurable": {"session_id": "test_user_01"}}
    
    print("🤖 AI: 你好，我是小 Q，你想聊点什么？")
    print("💡 提示：输入'秘密'会触发特殊模式，输入'查看记忆'查看当前记忆状态\n")
    
    while True:
        user_text = input("👤 用户: ")
        if user_text.lower() in ["exit", "退出"]:
            break
        
        # 查看记忆状态（调试用）
        if user_text == "查看记忆":
            memory = memory_manager.get_session_history(config["configurable"]["session_id"])
            print(f"\n📊 记忆状态:")
            print(f"  - 原始消息数量: {len(memory.raw_messages)}/{memory.max_raw_messages}")
            print(f"  - 秘密模式: {'已触发 🎭' if memory.secret_triggered else '未触发'}")
            print(f"  - 摘要内容: {memory.summary if memory.summary else '无'}\n")
            continue
        
        # 获取历史消息（用于显示）
        history_msgs = memory_manager.get_messages_for_prompt(config["configurable"]["session_id"])
        
        # 手动构建并调用（简化版示例，实际生产可用 LCEL 链）
        messages = [
            ("system", prompt.messages[0].prompt.template),
            *[(msg.type, msg.content) for msg in history_msgs],
            ("user", user_text)
        ]
        
        # 调用模型
        from langchain_core.messages import HumanMessage as HMsg, AIMessage as AMsg
        full_messages = []
        for msg_type, content in messages:
            if msg_type == "system":
                full_messages.append(("system", content))
            elif msg_type == "human":
                full_messages.append(HMsg(content=content))
            elif msg_type == "ai":
                full_messages.append(AMsg(content=content))
        
        # 获取记忆对象
        memory = memory_manager.get_session_history(config["configurable"]["session_id"])
        
        # 调用模型（这里简化了，实际应该用 chain）
        from langchain_core.prompts import ChatPromptTemplate
        temp_prompt = ChatPromptTemplate.from_messages(full_messages)
        response = (temp_prompt | model).invoke({})
        
        # 应用秘密规则（在回复中添加 emoji）
        response_content = response.content
        if memory.secret_triggered and "🎭" not in response_content:
            response_content += " 🎭"
        
        # 保存对话
        memory.add_message(HMsg(content=user_text))
        memory.add_message(AMsg(content=response_content))
        
        print(f"🤖 AI: {response_content}\n")
        
        # 自动显示记忆状态（可选）
        if len(memory.raw_messages) >= memory.max_raw_messages:
            print(f"📌 提示：已达记忆上限 ({memory.max_raw_messages}条)，旧消息已自动生成摘要\n")


# ========== 更简洁的推荐写法（使用官方组件）==========
"""
如果你希望使用更标准的 LangChain 方式，这里是简化版本：
"""

from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationChain

# 使用官方提供的 ConversationSummaryBufferMemory来限制记忆条数
def simple_version_with_official_memory():
    """使用官方组件的简化版本"""
    
    memory = ConversationSummaryBufferMemory(
        llm=model,
        max_token_limit=2000,  # 根据 token 限制而非条数
        return_messages=True
    )
    
    # 自定义 prompt 添加秘密规则
    custom_prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个幽默风趣的 AI 助手。
        
【特殊规则】
⚠️ 如果用户提到过"秘密"，请在后续所有回复中都带上 🎭 表情符号。"""),
        MessagesPlaceholder(variable_name="history"),
        ("user", "{input}")
    ])
    
    # 创建对话链
    conversation = ConversationChain(
        llm=model,
        memory=memory,
        prompt=custom_prompt
    )
    
    # 运行对话
    config = {"configurable": {"session_id": "test_user_01"}}
    
    while True:
        user_input = input("👤 用户: ")
        if user_input == "exit":
            break
        
        response = conversation.predict(input=user_input)
        
        # 检查是否需要添加 emoji（通过检查 memory 中是否有"秘密"）
        # 这里简化处理，实际需要维护状态
        print(f"🤖 AI: {response}")