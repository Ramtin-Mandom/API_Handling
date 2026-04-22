from fastapi import FastAPI
from .models import OpenAIFinalResult, OpenAIInput
from .services import (
    openai_request_process,
    openai_request,
    evaluate_openai_response,
    final_clean_up,
)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello, {name}"}

@app.post("/openai-request", response_model=OpenAIFinalResult)
async def openai_request_endpoint(data: OpenAIInput) -> OpenAIFinalResult:
    cleaned_request = openai_request_process(data)
    openAI_raw_response = openai_request(cleaned_request)
    evaluated_response = evaluate_openai_response(openAI_raw_response)
    final_result = final_clean_up(evaluated_response, openAI_raw_response)

    return final_result
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