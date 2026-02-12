from pydantic import BaseModel
from typing import Literal


class ParsedInput(BaseModel):
    input_type: Literal["cv", "job", "unknown"]
    content: str
