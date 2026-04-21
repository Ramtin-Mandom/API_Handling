from httpx import request
from pydantic import BaseModel, Field, StrictStr

class InputText(BaseModel):
    text: StrictStr
    c: str = Field(..., min_length=1, max_length=1)

class OutputText(BaseModel):
    input_text: str
    char_count: int
    c_count: int
    ratio: float
class OpenAIInput(BaseModel):
    input: StrictStr
class OpenAIRequest(BaseModel):
    request: StrictStr
class OpenAIResponse(BaseModel):
    response: StrictStr
class OpenAIAnalysisResponse(BaseModel):
    analysis_result: StrictStr