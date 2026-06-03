import os
import hashlib
from dotenv import load_dotenv
import numpy as np

load_dotenv()

api_key = os.getenv("CHROMA_API_KEY")
api_url = os.getenv("CHROMA_API_URL") or os.getenv("CHROMA_SERVER")

if not api_key:
    print("ERROR: CHROMA_API_KEY not found in environment. Ensure .env was created by the CLI and contains CHROMA_API_KEY.")
    raise SystemExit(1)

from chromadb import CloudClient

client = CloudClient(api_key=api_key, api_url=api_url)

def deterministic_embed(text, dim=8):
    h = hashlib.sha256(text.encode()).hexdigest()
    vals = []
    for i in range(dim):
        chunk = h[i * 8:(i + 1) * 8]
        vals.append(int(chunk, 16) / 0xFFFFFFFF)
    return vals

COL_NAME = "chroma-getting-started"

try:
    collection = client.create_collection(name=COL_NAME)
except Exception:
    collection = client.get_collection(name=COL_NAME)

documents = [
    "Alice likes machine learning.",
    "Bob enjoys hiking and photography.",
    "Carol is a software engineer who loves Python."
]
ids = ["doc1", "doc2", "doc3"]
metadatas = [{"source": "notes"} for _ in documents]
embeddings = [deterministic_embed(d) for d in documents]

print("Ingesting documents:")
for i, d in enumerate(documents):
    print(f"- id={ids[i]} doc=\"{d}\"")

collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)

query_text = "Looking for someone who programs in Python"
query_emb = deterministic_embed(query_text)

print("\nQuery:")
print(query_text)

res = collection.query(query_embeddings=[query_emb], n_results=3, include=["documents", "metadatas", "distances", "ids"]) 

print("\nResults:")
print(res)

print("\nDone. (Data left in collection.)")
