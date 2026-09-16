from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from src.rag import ask_rag

app = FastAPI(
    title="RAG Chatbot API",
    description="FastAPI + LangGraph + Chroma + Gemini",
    version="1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    question: str
    answer: str


@app.get("/")
def home():
    return {
        "message": "RAG Chatbot API Running Successfully"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    answer = ask_rag(request.question)

    return ChatResponse(
        question=request.question,
        answer=answer
    )