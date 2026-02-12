# query_jobs(), init client, etc.
from pathlib import Path
from dotenv import load_dotenv
import os
from tqdm import tqdm
import pandas as pd

import chromadb
from chromadb.utils.embedding_functions import JinaEmbeddingFunction
from typing import Any

# Load environment variables from .env file
load_dotenv()


def get_client(persist_dir: str) -> Any:
    """
    Initialize and return a ChromaDB client with the specified persistence directory.
    """
    Path(persist_dir).mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=persist_dir)


def get_collection(client: Any, collection_name: str, if_embedding: bool) -> Any:
    """
    Get or create a jobs collection in the given ChromaDB client.

    - "hnsw:space" → tells Chroma to use Hierarchical Navigable Small World
                     as distance metric.
    - "cosine" → instructs HNSW to use cosine distance.
    """
    if if_embedding:
        embedding_fn = JinaEmbeddingFunction(
            api_key=os.getenv("EMBEDDING_API_KEY"),  # https://jina.ai/
            model_name=os.getenv("EMBEDDING_MODEL"),
        )

    else:
        embedding_fn = None

    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"},
    )
    return collection


def add_to_collection(
        metadata_extractor: Any,
        corpus: pd.DataFrame,
        collection: Any,
) -> None:
    """
    Add documents with metadata to the specified ChromaDB collection.
    """
    for _, row in tqdm(corpus.iterrows(), total=len(corpus)):

        inputs = {"content": row["content"]}
        metadata = metadata_extractor.crew().kickoff(inputs=inputs)

        collection.add(
            ids=[row["doc_id"]],
            documents=[row["content"]],
            metadatas=[metadata.json]
        )
