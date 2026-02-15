from pydantic import BaseModel

from src.talent_selection_flow.crews.classification_crew.enums import DocumentType


class TalentState(BaseModel):
    raw_input: str = ""
    input_type: DocumentType = DocumentType.OTHER
    output: str = ""
