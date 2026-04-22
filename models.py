from cgitb import text
from httpx import request
from typing import Union, List
from pydantic import BaseModel, StrictStr,StrictInt


class OpenAIInput(BaseModel):
    text: StrictStr
class OpenAIRequest(BaseModel):
    requests: Union[StrictStr, List[StrictStr]]
class OpenAIResponse(BaseModel):
    responses: Union[StrictStr, List[StrictStr]]
class OpenAIEvaluatedResponse(BaseModel):
    analysis_result: StrictInt
class OpenAIFinalResult(BaseModel):
    final_text: StrictStr