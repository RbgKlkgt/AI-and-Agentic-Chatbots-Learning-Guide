import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CONVERSATION_FILE = Path(__file__).parent / "conversation.json"


class ChatRequest(BaseModel):
    prompt: str
    conversation_id: str | None = None


def _read_conversations() -> dict:
    with open(CONVERSATION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_conversations(data: dict) -> None:
    with open(CONVERSATION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_user_message(conversation_id: str, prompt: str) -> None:
    data = _read_conversations()
    if conversation_id not in data:
        data[conversation_id] = {}
    exchanges = data[conversation_id]
    exchange_id = str(len(exchanges) + 1)
    exchanges[exchange_id] = [{"role": "user", "content": prompt}]
    _write_conversations(data)


def save_assistant_message(conversation_id: str, response: str) -> None:
    data = _read_conversations()
    exchanges = data[conversation_id]
    last_exchange_id = str(len(exchanges))
    exchanges[last_exchange_id].append({"role": "assistant", "content": response})
    _write_conversations(data)


def build_history(data: dict) -> list[dict]:
    history = []
    for conv_id in sorted(data.keys(), key=int):
        for exchange_id in sorted(data[conv_id].keys(), key=int):
            history.extend(data[conv_id][exchange_id])
    return history


def get_agent_response(history: list[dict]) -> str:
    llm = ChatMistralAI(model="mistral-small-latest", api_key=os.getenv("MISTRAL_API_KEY"))
    messages = [
        HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"])
        for m in history
    ]
    result = llm.invoke(messages)
    return result.content


@app.post("/chat")
def chat(request: ChatRequest):
    data = _read_conversations()

    conversation_id = request.conversation_id or str(len(data) + 1)

    save_user_message(conversation_id, request.prompt)

    updated_data = _read_conversations()
    history = build_history(updated_data)

    response = get_agent_response(history)
    save_assistant_message(conversation_id, response)

    return {"response": response, "conversation_id": conversation_id}
