from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import os

def search_qdrant(question, top_K=3):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    question_embedding = model.encode([question])
    client = QdrantClient(os.getenv("QDRANT_HOST", "localhost"), port=int(os.getenv("QDRANT_PORT", "6333")))
    results = client.search(
        collection_name="document_chunks",
        query_vector=question_embedding[0],
        limit=top_K)
    return [hit.payload["text"] for hit in results]

if __name__ == "__main__":
    print(search_qdrant("What was the major achievement in road construction in 2024?", top_K=3))