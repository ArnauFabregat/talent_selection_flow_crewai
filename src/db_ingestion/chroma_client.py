"""
ChromaDB Operations Module.

This module provides utility functions to interact with ChromaDB, including
client initialization, collection management, document ingestion with
automated metadata extraction, and semantic search with fallback strategies.
"""

import json
import os
import time
from pathlib import Path
from typing import Any

import chromadb
import pandas as pd
from chromadb.utils.embedding_functions import JinaEmbeddingFunction
from dotenv import load_dotenv
from tqdm import tqdm

from src.config.paths import CHROMA_DIR
from src.utils.logger import logger

# Load environment variables from .env file
load_dotenv()


def get_client(persist_dir: str = str(CHROMA_DIR)) -> Any:
    """
    Initialize and return a ChromaDB persistent client.

    Args:
        persist_dir (str): The directory where ChromaDB data is stored.
            Defaults to the project's CHROMA_DIR.

    Returns:
        chromadb.PersistentClient: An instance of the ChromaDB persistent client.
    """
    Path(persist_dir).mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=persist_dir)


def get_collection(client: Any, collection_name: str) -> Any:
    """
    Get an existing collection or create a new one with specific distance metrics.

    Uses Jina AI embeddings and configures the HNSW space for cosine similarity.

    Args:
        client (Any): The initialized ChromaDB client.
        collection_name (str): The name of the collection to access or create.

    Returns:
        chromadb.Collection: The requested ChromaDB collection object.
    """
    embedding_fn = JinaEmbeddingFunction(
        api_key=os.getenv("EMBEDDING_API_KEY"),  # https://jina.ai/
        model_name=os.getenv("EMBEDDING_MODEL", ""),
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
    max_rpm: int | None = None,
    verbose: bool = False,
    **kwargs,
) -> None:
    """
    Extracts metadata from documents and adds them to the vector collection.

    This function iterates through a DataFrame, uses an AI crew to extract
    structured metadata from the text content, and performs rate-limited
    uploads to the database.

    Args:
        metadata_extractor (Any): The CrewAI-based agent or crew responsible
            for extracting JSON metadata.
        corpus (pd.DataFrame): A DataFrame containing at least 'doc_id'
            and 'content' columns.
        collection (Any): The ChromaDB collection object to receive the data.
        max_rpm (int, optional): Maximum Requests Per Minute for the AI extractor.
        verbose (bool): If True, enables detailed logging for the extraction process.
        **kwargs: Additional context passed to the metadata extractor.
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
            logger.debug(f"Metadata:\n{json.loads(metadata.raw)}")
        except Exception as e:
            logger.error(f"Failed extraction for `doc_id={row.get('doc_id')}` due to error: {e}")
            continue

        # Remove None values before sending to Chroma
        metadata_dict = {k: v for k, v in metadata.json_dict.items() if v is not None}
        null_keys = [k for k, v in metadata.json_dict.items() if v is None]

        if null_keys:
            logger.warning(f"Null metadata keys for `doc_id={row['doc_id']}`: {null_keys}")

        # Add to ChromaDB
        collection.add(ids=[str(row["doc_id"])], documents=[row["content"]], metadatas=[metadata_dict])


def reshape_chroma_results(chroma_output: dict[str, Any]) -> dict[str, Any]:
    """
    Transforms raw ChromaDB query results into a structured dictionary format.

    Converts cosine distance into a similarity score (1 - distance) and
    maps metadata fields to a consistent schema.

    Args:
        chroma_output (dict): The raw dictionary returned by `collection.query`.

    Returns:
        dict[str, dict]: A dictionary where keys are Job IDs and values are
            formatted metadata and similarity scores.
    """
    # Check if results are empty
    if not chroma_output["ids"] or not chroma_output["ids"][0]:
        return {}

    ids = chroma_output["ids"][0]
    distances = chroma_output["distances"][0]
    metadatas = chroma_output["metadatas"][0]

    return {
        ids[i]: {
            "title": metadatas[i].get("title", ""),
            "similarity": round(1 - distances[i], 4),
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
    persist_dir: str = str(CHROMA_DIR),
    top_k: int = 3,
) -> dict[str, Any]:
    """
    Performs a semantic search in a collection with an optional geographical filter.

    Strategy:
    1. Attempt search filtered by country.
    2. If no results found or no country provided, perform a global search.

    Args:
        collection_name (str): The name of the collection to query.
        query_text (str): The natural language query or document text.
        country (str): The country name for strict metadata filtering.
        persist_dir (str): Path to the ChromaDB storage.
        top_k (int): Number of most relevant documents to return.

    Returns:
        dict[str, Any]: The reshaped search results including metadata and similarity.
    """
    # Initialize client and access collection
    client = get_client(persist_dir=persist_dir)
    collection = get_collection(client=client, collection_name=collection_name)

    logger.info(f"Initiating vector search in collection '{collection_name}' (Top K: {top_k})")

    # Primary Search: Strict filtering by country
    if country:
        results = collection.query(query_texts=[query_text], n_results=top_k, where={"country": country})

    # Fallback Strategy: If no results found with country filter, widen the search
    if (not country) or (results["ids"] == [[]]):
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
