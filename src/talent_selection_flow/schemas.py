from pydantic import BaseModel
from typing import Optional

from src.talent_selection_flow.crews.classification_crew.enums import InputType


class TalentState(BaseModel):
    raw_input: str = None
    input_type: InputType = InputType.OTHER
    results: Optional[str] = None
