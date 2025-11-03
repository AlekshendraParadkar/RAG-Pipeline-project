import os
from urllib import response
from dotenv import load_dotenv
from groq import Groq
from retrieve import search_qdrant
load_dotenv()  

def generate_answer(question):
    # Automatically retrieve relevant context from vector store
    retrieved_chunks = search_qdrant(question, top_K=3)
    # print("Retrieved chunks:")
    if not retrieved_chunks:
        print("No relevant context found for the question.")
    context = "\n\n".join(retrieved_chunks)

    prompt = (
        "Given the following context from a government report, answer the question. "
        "If the answer can't be found in the context, say so.\n\n"
        f"CONTEXT:\n{context}\n\nQUESTION: {question}\n\nANSWER:"
    )

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",  # Free open model by Groq
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=2560,
        temperature=0.2,
    )

    return response.choices[0].message.content



