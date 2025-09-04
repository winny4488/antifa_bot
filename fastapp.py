from fastapi import FastAPI
from pydantic import BaseModel
from main import rag_query

#/chat?passcode=zanye&query=hello

app = FastAPI()

@app.get("/chat")
def chat_endpoint(passcode, query):
    if passcode != "zanye":
        return

    # Replace with your AI pipeline (rag_query, etc.)
    response = rag_query(query, memory_context="")
    return {"response": response}
