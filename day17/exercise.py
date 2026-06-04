# 练习1 - 計算用戶問題向量與文檔向量的距離。增加一個 `doc_c_vec` 向量，隨意填寫數字，觀察它的相似度。
import numpy as np

def calculate_similarity(vec1, vec2):
    """
    calculate the cosine similarity between two vectors.
    """
    # 1. Calculate Dot Product (點積)
    dot_product = np.dot(vec1, vec2)

    # 2. Calculate Norm (模長)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    # 3. Calculate Cosine Similarity
    # Formula: (A . B) / (||A|| * ||B||)
    similarity = dot_product / (norm1 * norm2)
    return similarity

if __name__ == '__main__'
    # 假设user的搜索转化为嵌入式向量 query_vec
    query_vec= np.array([0.4,0.5,0.3,0.7])

    # 假设有参考文件a & 参考文件b
    doc_a_vec = np.array([0.12,0.52,0.5,0.2])
    doc_b_vec = np.array([0.72,0.2,0.25,0.5])

    sim_a=calculate_similarity(query_vec,doc_a_vec)
    sim_b=calculate_similarity(query_vec,doc_b_vec)

    print(f"Similarity with Document A (Related): {sim_a:.4f}")
    print(f"Similarity with Document B (Unrelated): {sim_b:.4f}")


# 练习2-  嘗試使用 `np.reshape` 將一個長度為 6 的一維陣列轉換成 (2, 3) 的矩陣。

array_a = np.array([1,345,7,3,82,2])

matrix_a=array_a.reshape(2,3)



