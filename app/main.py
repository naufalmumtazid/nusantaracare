from fastapi import FastAPI
from .schemas import QueryRequest, QueryResponse
from .services.agent import generate_answer
from .services.rag import rag_system

app = FastAPI(title="NusantaraCare RAG API")

@app.get("/")
async def home():
    return {"APP Name": "Nusantara Care"}

@app.post("/api/v1/ask", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    user_question = request.question

    retrieved_data = rag_system.query_rag(user_question)
    chunks = retrieved_data.get("documents", [[]])[0]

    response = generate_answer(
        question=user_question, retrieved_chunks=chunks
    )

    return response

