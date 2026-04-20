from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class EchoResponse(BaseModel):
    received_text: str
    length: int  
class MessageRequest(BaseModel):
    text: str  

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello, {name}"}

@app.post("/echo", response_model=EchoResponse)
async def echo_message(data: MessageRequest):
    return {
        "received_text": data.text,
        "length": len(data.text)
    }