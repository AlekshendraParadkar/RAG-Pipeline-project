from qdrant_client import QdrantClient
import numpy as np
import os

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLETION_NAME = "document_chunks"

def upload_to_qdrant(embeddings, texts):
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    client.recreate_collection(
        collection_name=COLLETION_NAME,
        vectors_config={"size": embeddings.shape[1], "distance": "Cosine"} )
    client.upsert(
        collection_name=COLLETION_NAME,
        points=[{
            "id": idx,
            "vector": embedding,
            "payload": {"text": text}
        } for idx, (embedding, text) in enumerate(zip(embeddings, texts))]
    )

if __name__ == "__main__":
    embeddings = np.load("embeddings.npy")
    with open("chunks.txt", "r", encoding="utf-8") as f:
        texts = f.read().split("\n\n---\n\n")
    upload_to_qdrant(embeddings, texts)
