import os
from llama_index.llms.dashscope import DashScope
from llama_index.embeddings.dashscope import DashScopeEmbedding
from llama_index.core import VectorStoreIndex,SimpleDirectoryReaer,Settings

# 1.全剧配置（Settings） 
# 注意这里的model中llm的model会和embedding的分开，
# 用专用的embedding model来做embedding查询
Settings.llm=DashScope(model_name='qwen-turbo')
Settings.embed_model=DashScopeEmbedding(model_name="text-embedding-v2")
# 配置全局的NodeParser【可选的】
Settings.node_parser = SimpleNodeParser.from_defaults(
    chunk_size=512,        # 每个节点最大字符数
    chunk_overlap=20,      # 节点间重叠字符数
    include_metadata=True  # 是否包含元数据
)

def quick_start_rag():
    #2.加载当前文件夹下'data'目录
    if not os.path.exists("./data"):
        os.makedirs('./data')
        with open('./data/test.txt','w') as f:
            f.write('感时花溅泪，恨别鸟惊心')
    print('⏳...文档取读中')

    # step1 取读文档
    documents=SimpleDirectoryReader('./data').load_data()
    # ↑ 这一步内部调用了：下面方法，自动在后面自动完成了Document→Node的切分
        # 1. 默认的NodeParser
        # 2. 将每个Document切分成多个Node
        # 3. 为每个Node生成embedding
        # 4. 构建索引

    #step2 建立向量索引
    index= VectorStoreIndex.from_documents(documents)

    # step3常见引擎查询
    query_engine=index.as_query_engine()

    # 提问
    response  = query_engine.query("感时花溅泪的下一句诗文是什么？")
    print(response)

if __name__=="__main__":
    quick_start_rag()





