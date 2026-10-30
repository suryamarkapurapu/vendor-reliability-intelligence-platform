
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix="/chat",
    tags=["Chatbot"],
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    message = request.message.strip()

    if not message:
        reply = "Please enter a message."
    elif message.lower() in {"hi", "hello", "hey"}:
        reply = "Hello! I'm your Vendor Reliability Platform chatbot. How can I help you?"
    elif "vendor" in message.lower():
        reply = "I can help you explore vendor management and vendor reliability."
    elif "procurement" in message.lower():
        reply = "I can help you explore procurement requests and purchase orders."
    else:
        reply = "I'm a beginner chatbot, so I can currently respond to greetings and basic vendor or procurement questions."

    return ChatResponse(reply=reply)
