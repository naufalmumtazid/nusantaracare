from fastapi import FastAPI
from app.schemas import QueryRequest, QueryResponse
from app.services.agent import generate_answer
from app.services.rag import rag_system

app = FastAPI(title="NusantaraCare RAG API")

@app.post("/api/v1/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    user_question = request.question

    retrieved_data = rag_system.query_rag(user_question)
    chunks = retrieved_data.get("documents", [[]])[0]

    response = generate_answer(
        question=user_question, retrieved_chunks=chunks
    )

    return response

