from pydantic import BaseModel, Field

class InputText(BaseModel):
    text: str
    c: str = Field(..., min_length=1, max_length=1)

class OutputText(BaseModel):
    input_text: str
    char_count: int
    c_count: int
    ratio: float