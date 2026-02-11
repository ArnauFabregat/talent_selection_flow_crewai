from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Any, Literal
import chromadb

from config.paths import CHROMA_DIR
from exceptions import ChromaDBMatcherError


class MatcherInput(BaseModel):
    query_text: str = Field(..., description="CV text or job description to match")
    search_type: Literal["jobs", "cvs"] = Field(..., description="Search for 'jobs' or 'cvs'")
    top_k: int = Field(default=5, description="Number of results to return")


class ChromaDBMatcherTool(BaseTool):
    name: str = "ChromaDB Matcher"
    description: str = "Matches CVs to jobs using semantic search"
    args_schema: type[BaseModel] = MatcherInput
    chroma_path: str = Field(
        default=CHROMA_DIR,
        description="Filesystem path to Chroma's persistent store"
    )
    _client: Any = None  # Private attribute

    def model_post_init(self, __context: Any) -> None:
        self._client = chromadb.PersistentClient(path=self.chroma_path)

    def _run(self, query_text: str, search_type: str, top_k: int = 5) -> str:

        # Select collection based on search type
        collection_name = "jobs" if search_type == "jobs" else "cvs"
        try:
            collection = self._client.get_collection(collection_name)
        except Exception as e:
            raise ChromaDBMatcherError(
                f"Could not load Chroma collection '{collection_name}': {e}"
            )

        results = collection.query(
            query_texts=[query_text],
            n_results=top_k
        )
        return str(results)
