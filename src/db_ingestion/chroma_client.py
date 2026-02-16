# query_jobs(), init client, etc.
from pathlib import Path
from dotenv import load_dotenv
import os
import time
from tqdm import tqdm
import pandas as pd

from src.utils.logger import logger
from src.config.paths import CHROMA_DIR

import chromadb
from chromadb.utils.embedding_functions import JinaEmbeddingFunction
from typing import Any, Dict, Optional

# Load environment variables from .env file
load_dotenv()


def get_client(persist_dir: str = CHROMA_DIR) -> Any:
    """
    Initialize and return a ChromaDB client with the specified persistence directory.
    """
    Path(persist_dir).mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=persist_dir)


def get_collection(client: Any, collection_name: str) -> Any:
    """
    Get or create a jobs collection in the given ChromaDB client.

    - "hnsw:space" → tells Chroma to use Hierarchical Navigable Small World
                     as distance metric.
    - "cosine" → instructs HNSW to use cosine distance.
    """
    embedding_fn = JinaEmbeddingFunction(
        api_key=os.getenv("EMBEDDING_API_KEY"),  # https://jina.ai/
        model_name=os.getenv("EMBEDDING_MODEL"),
    )

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
        max_rpm: Optional[int] = None,
        verbose: bool = False,
        **kwargs,
) -> None:
    """
    Add documents with extracted metadata to a ChromaDB collection,
    optionally respecting a max requests-per-minute limit.
    """
    # Precompute delay if a limit is provided
    min_delay: float = 60 / max_rpm if max_rpm else 0
    last_call: float = 0

    logger.info(f"Adding {len(corpus)} documents to `{collection.name}` collection.")
    for _, row in tqdm(corpus.iterrows(), total=len(corpus)):
        # Conditional rate limiting
        if max_rpm:
            now = time.time()
            elapsed = now - last_call

            if elapsed < min_delay:
                time.sleep(min_delay - elapsed)

            last_call = time.time()

        # Extract metadata
        inputs = {"content": row["content"], **kwargs}
        metadata_extractor._verbose = verbose
        crew = metadata_extractor.crew()

        try:
            metadata = crew.kickoff(inputs=inputs)
            logger.debug(f"Metadata: {metadata}")
        except Exception as e:
            logger.error(f"Failed extraction for `doc_id={row.get('doc_id')}` due to error: {e}")
            continue
        # Remove None values before sending to Chroma
        metadata_dict = {k: v for k, v in metadata.json_dict.items() if v is not None}
        null_keys = [k for k, v in metadata.json_dict.items() if v is None]

        if null_keys:
            logger.warning(f"Null metadata keys for `doc_id={row['doc_id']}`: {null_keys}")

        # Add to ChromaDB
        collection.add(
            ids=[str(row["doc_id"])],
            documents=[row["content"]],
            metadatas=[metadata_dict]
        )


def reshape_chroma_results(chroma_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Output format:
    {
    "JOB_ID": {
        "title": "Official job title",
        "similarity": 0.85, // Higher is better (range 0 to 1)
        "skills": "Key technical requirements",
        "industries": "Relevant market sectors",
        "experience_level": "Required seniority level",
        "summary": "Detailed responsibilities and job context",
        "country": "Job location country",
    }
    }
    """
    # Dictionary comprehension; we take the first index [0] 
    # because you likely queried with a single CV.
    ids = chroma_output['ids'][0]
    distances = chroma_output['distances'][0]
    metadatas = chroma_output['metadatas'][0]
    
    return {
        ids[i]: {
            "title": metadatas[i].get("title", ""),  # will be empty in de cvs collection
            "similarity": 1 - round(distances[i], 4),
            "skills": metadatas[i].get("skills", ""),
            "industries": metadatas[i].get("industries", ""),
            "experience_level": metadatas[i].get("experience_level", ""),
            "summary": metadatas[i].get("summary", ""),
            "country": metadatas[i].get("country", ""),
        }
        for i in range(len(ids))
    }


def query_to_collection(
    collection_name: str,
    query_text: str,
    country: str,
    persist_dir: str = CHROMA_DIR,
    top_k: int = 3,
) -> Dict[str, Any]:
    """
    Retrieves the most relevant documents from ChromaDB with a metadata fallback strategy.
    """
    # Initialize client and access collection
    client = get_client(persist_dir=persist_dir)
    collection = get_collection(client=client, collection_name=collection_name)

    logger.info(f"Initiating vector search in collection '{collection_name}' (Top K: {top_k})")

    # Primary Search: Strict filtering by country
    if country:
        results = collection.query(
            query_texts=[query_text],
            n_results=top_k,
            where={"country": country}
        )

    # Fallback Strategy: If no results found with country filter, widen the search
    if (country is None) or (results["ids"] == [[]]):
        logger.warning(
            f"No matches found for country '{country}'. "
            "Broadening search to all regions to ensure candidate visibility."
        )
        results = collection.query(
            query_texts=[query_text],
            n_results=top_k,
        )

    formatted_results = reshape_chroma_results(chroma_output=results)
    logger.debug(f"Final formatted results:\n{formatted_results}")

    return formatted_results
