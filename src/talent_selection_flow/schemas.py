from pydantic import BaseModel
from typing import Any, Dict

from src.talent_selection_flow.crews.classification_crew.enums import DocumentType


class TalentState(BaseModel):
    raw_input: str = ""
    input_type: DocumentType = DocumentType.OTHER
    metadata: Dict[str, Any] = {}
    related_docs: Dict[str, Any] = {}
    process_crew: Any = None
