from token import OP
from fastapi import FastAPI
from models import InputText, OutputText
from models import OpenAIInput, OpenAIAnalysisResponse
from services import analyze_text, openai_request_clean_up, openai_request, analyze_openai_response

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello, {name}"}

@app.post("/analyze-text", response_model=OutputText)
async def analyze_text_endpoint(data: InputText):
    return analyze_text(data)
@app.post("/openai-request", response_model=OpenAIAnalysisResponse)
async def openai_request_endpoint(data: OpenAIInput) -> OpenAIAnalysisResponse:
    cleaned_request = openai_request_clean_up(data)
    openai_raw_response = openai_request(cleaned_request)
    analyzed_response = analyze_openai_response(openai_raw_response)

    return analyzed_response
# class EchoResponse(BaseModel):
#     received_text: str
#     length: int  
# class MessageRequest(BaseModel):
#     text: str  
# @app.get("/")
# async def root():
#     return {"message": "API is running"}

# @app.get("/hello/{name}")
# async def say_hello(name: str):
#     return {"message": f"Hello, {name}"}

# @app.post("/echo", response_model=EchoResponse)
# async def echo_message(data: MessageRequest):
#     return {
#         "received_text": data.text,
#         "length": len(data.text)
#     }