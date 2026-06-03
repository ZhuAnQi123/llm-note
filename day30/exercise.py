import os
import chromadb
import uuid
from dashscope import Generation, TextEmbedding
from http import HTTPStatus

dashscope.api_key = 'sk-59c5b66dbe244feaaa26dabb23c5616b'

# --- 工具函数区 ---

# 获取embedding函数
def get_embedding(text):
    '''获取Qwen向量'''
    response = TextEmbedding.call(
        model=TextEmbedding.Models.text_embedding_v2,
        input=text
    )

    if response.status_code == HTTPStatus.OK:
        return response.output['embeddings'][0]['embedding']
    else:
        raise Exception(f"Embedding API Error:{response.message}")

# document切分函数
def split_text(text, chunk_size=300):
    """简单的按长度切分，不带 Overlap (复习用,在实际开发中必须使用带重叠的切分方法)"""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# 核心流程区

class KnowledgeBaseAssistant:
    def __init__(self, collection_name='local_kb'):
        # 1.初始化本地持久化数据库
        self.client = chromadb.PersistentClient(path='./my_kb_storage')
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def clear(self):
        """清空整个collection"""
        # 获取当前collection中的所有ids
        all_ids = self.collection.get()['ids']
        if all_ids:
            self.collection.delete(ids=all_ids)
            print(f"已清空collection，删除了{len(all_ids)}条记录")
        else:
            print("collection已经是空的")

    def is_duplicate(self, chunk):
        """检查文本块是否已存在于数据库中"""
        # 使用embedding相似度检查去重
        try:
            vec = get_embedding(chunk)
            results = self.collection.query(
                query_embeddings=[vec],
                n_results=1
            )
            # 如果存在结果且相似度足够高（这里使用简单判断，实际可以用余弦相似度）
            if results['documents'][0] and len(results['documents'][0]) > 0:
                # 检查是否完全相同
                if results['documents'][0][0] == chunk:
                    return True
            return False
        except Exception as e:
            print(f"去重检查出错: {e}")
            return False

    def ingest_data(self, raw_text):
        '''将原始文本存入向量库，插入前去重'''
        chunks = split_text(raw_text)
        added_count = 0
        skipped_count = 0

        for chunk in chunks:
            # 插入前去重
            if self.is_duplicate(chunk):
                print(f"跳过重复内容: {chunk[:50]}...")
                skipped_count += 1
                continue
            
            vec = get_embedding(chunk)
            self.collection.add(
                embeddings=[vec],
                documents=[chunk],
                ids=[str(uuid.uuid4())]
            )
            added_count += 1
        
        print(f"数据入库完成: 新增{added_count}条, 跳过{skipped_count}条重复")

    def ask(self, query):
        '''用户提问，返回RAG回答，带质量检查'''
        print(f"\n[查询]: {query}")
        
        # A.检索
        try:
            query_vec = get_embedding(query)
            results = self.collection.query(
                query_embeddings=[query_vec],
                n_results=3
            )
            
            # 质量检查1：检查检索结果是否为空
            if not results['documents'][0] or len(results['documents'][0]) == 0:
                print("[质量检查] 警告：数据库检索结果为空！")
                return "知识库中暂无相关内容，请先导入数据。"
            
            context = '\n'.join(results['documents'][0])
            print(f"[检索结果] 找到{len(results['documents'][0])}条相关内容")
            
        except Exception as e:
            print(f"[质量检查] 数据库检索失败: {e}")
            return f"检索过程出现错误: {e}"

        # B.构造prompt
        prompt = f"""你是一个专业的AI知识助手，
        请你根据下面的参考内容回答用户问题，如果参考内容中没有提到相关信息，请回答“目前在知识库中没有找到相关说明”
        【参考内容】：
        {context}
        【用户提问】：
        {query}
        """

        # C.调用qwen对话接口
        try:
            response = Generation.call(
                model='qwen-turbo',
                messages=[{'role': 'user', 'content': prompt}],
                result_format='message'
            )

            if response.status_code == HTTPStatus.OK:
                answer = response.output.choices[0]['message']['content']
                
                # 质量检查2：验证AI回答是否合理
                print(f"[AI回答]: {answer}")
                
                # 简单检查：如果AI回答提到"没有找到"，但检索结果不为空，可能存在检索问题
                if ("没有找到" in answer or "暂无" in answer or "未找到" in answer) and context.strip():
                    print("[质量检查] 警告：AI回答表示未找到信息，但实际检索到了相关内容，请检查检索相关性！")
                
                return answer
            else:
                error_msg = f"API调用失败: {response.message}"
                print(f"[质量检查] {error_msg}")
                return error_msg
                
        except Exception as e:
            print(f"[质量检查] AI模型调用失败: {e}")
            return f"AI模型调用出现错误: {e}"


if __name__ == "__main__":
    # 模拟一段cursor使用手册内容
    CURSOR_GUIDE = """
    Cursor 是一款强大的 AI 编辑器。它支持快捷键 Cmd+K 进行代码修改，Cmd+L 进行对话。
    Cursor 可以自动索引你的整个代码库，从而提供精准的代码建议。
    目前 Cursor 已经支持 GPT-4o, Claude 3.5 Sonnet 等多个顶级模型。
    你可以在设置中通过开启 'Composer' 模式来进行多文件协作开发。
    """

    kb = KnowledgeBaseAssistant()

    # 测试1：正常入库
    print("=== 测试1：首次入库 ===")
    kb.ingest_data(CURSOR_GUIDE)

    # 测试2：重复入库（会去重）
    print("\n=== 测试2：重复入库（验证去重） ===")
    kb.ingest_data(CURSOR_GUIDE)

    # 测试3：提问（知识库中存在）
    print("\n=== 测试3：提问知识库中的内容 ===")
    ans = kb.ask('Cursor支持哪些AI模型？')
    print(f"最终答案: {ans}")

    # 测试4：提问（知识库中不存在，验证质量检查）
    print("\n=== 测试4：提问知识库中不存在的内容 ===")
    ans = kb.ask('cursor的总部在哪里？')
    print(f"最终答案: {ans}")

    # 测试5：清空collection
    print("\n=== 测试5：清空collection ===")
    kb.clear()

    # 测试6：清空后再次提问（验证检索失败的情况）
    print("\n=== 测试6：清空后提问 ===")
    ans = kb.ask('Cursor支持哪些模型？')
    print(f"最终答案: {ans}")