import os
from dashscope import TextEmbedding
from http import HTTPStatus
import numpy as np

# 1. 封装获取向量的函数，
# 这个方法这里返回的是python列表
def get_embedding(text):
    """
    调用 Qwen API 获取文本向量
    """
    response = TextEmbedding.call(
        model=TextEmbedding.Models.text_embedding_v2,
        input=text
    )
    if response.status_code == HTTPStatus.OK:
        # 返回第一个文本的向量
        return response.output['embeddings'][0]['embedding']
    else:
        raise Exception(f"API Error: {response.message}")

# 2. 计算余弦相似度 (复用 Day 17 知识)
# 要把python列表转化成nparray方便计算
def cosine_similarity(v1, v2):
    v1, v2 = np.array(v1), np.array(v2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# --- Main ---
if __name__ == "__main__":
    # 请确保已设置环境变量 DASHSCOPE_API_KEY
    try:
        text1 = "人工智能正在改变世界。"
        text2 = "AI 技术对人类社会产生了巨大影响。"
        text3 = "今天晚饭我想吃红烧肉。"

        print("⏳ 正在获取向量...")
        vec1 = get_embedding(text1)
        vec2 = get_embedding(text2)
        vec3 = get_embedding(text3)

        sim12 = cosine_similarity(vec1, vec2)
        sim13 = cosine_similarity(vec1, vec3)

        print(f"\n📄 句子 1: {text1}")
        print(f"📄 句子 2: {text2}")
        print(f"📄 句子 3: {text3}")
        print("-" * 30)
        print(f"✨ 句子 1 与 2 的相似度: {sim12:.4f} (语义接近)")
        print(f"✨ 句子 1 与 3 的相似度: {sim13:.4f} (语义无关)")

    except Exception as e:
        print(f"❌ 运行失败: {e}")