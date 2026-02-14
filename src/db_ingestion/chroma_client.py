# query_jobs(), init client, etc.
from pathlib import Path
from dotenv import load_dotenv
import os
import time
from tqdm import tqdm
import pandas as pd

from src.utils.logger import logger
from src.constants import GUARDRAIL_MAX_RETRIES

import chromadb
from chromadb.utils.embedding_functions import JinaEmbeddingFunction
from typing import Any, Optional

# Load environment variables from .env file
load_dotenv()


def get_client(persist_dir: str) -> Any:
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
