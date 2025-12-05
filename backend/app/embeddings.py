from typing import List
from .rag import get_openai_client

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generates embeddings for a list of texts using OpenAI's text-embedding-3-small model.
    """
    client = get_openai_client()
    response = client.embeddings.create(model="text-embedding-3-small", input=texts)
    embeddings = [item.embedding for item in response.data]
    return embeddings