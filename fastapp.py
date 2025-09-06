# Project Imports
from main import rag_query
from main import refine
from helpers.chat_memory import ChatMemory

# Python Imports
import json
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI()

# Whatever you want, this is optional
PASSCODE = "zanye"

# Mount the static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create Chat History
memory_context = ChatMemory()

# Serve index.html at root
@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")

# --- API MODELS ---
class ChatRequest(BaseModel):
    query: str

# --- API ROUTES ---
@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    # (Optional) add passcode check
    # if passcode != PASSCODE: return {"error": "Invalid passcode"}

    # Retrieve chat history for AI
    chat_history = [
        {"role": m["role"], "content": m["content"]}
        for m in memory_context.get_history()
    ]

    # Add user query to memory
    memory_context.add_message(role="user", content=req.query)

    # Get AI response
    response = rag_query(req.query, memory_context=chat_history)

    # Add AI response to memory
    memory_context.add_message(role="Komuna", content=response)
    return {"response": response}

@app.post("/api/clear")
async def clear_chat():
    memory_context.clear()
    return {"response": "Chat cleared."}

@app.post("/api/refine")
async def refine_chat():
    # Retrieve chat history for AI
    chat_history = [
        {"role": m["role"], "content": m["content"]}
        for m in memory_context.get_history()
    ]

    # Get refined response
    new_response = refine(chat_history)

    # Add response to memory
    memory_context.add_message(role="Komuna", content=new_response)
    return {"response": new_response}

@app.get("/api/export")
async def export_chat():
    # Dump memory to JSON string
    exported = memory_context.export_json_web()
    return json.loads(exported)

@app.post("/api/import")
async def import_chat(request: Request):
    # Convert file to json
    data = await request.json()

    # Import json to memory
    memory_context.import_json(data)
    return {
        "status": "Imported",
        "conversation": memory_context.get_history()
    }
