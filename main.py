import csv
import json
from typing import Optional, Literal, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Client(BaseModel):
    id: Optional[int] = None
    first_name: str
    last_name: str
    account: int

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class PromptRequest(BaseModel):
    user_question: str

def read_clients():
    try:
        with open('clients.csv', 'r') as f:
            reader = csv.DictReader(f)
            clients = []
            for row in reader:
                row['id'] = int(row['id'])
                row['account'] = int(row['account'])
                clients.append(row)
            return clients
    except FileNotFoundError:
        return []

def write_clients(clients):
    with open('clients.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'first_name', 'last_name', 'account'])
        writer.writeheader()
        for client in clients:
            writer.writerow(client)

def read_conversations():
    try:
        with open("conversation.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def write_conversations(conversations):
    with open("conversation.json", "w", encoding="utf-8") as f:
        json.dump(conversations, f, ensure_ascii=False, indent=2)            

@app.get("/clients")
def get_clients():
    return read_clients()

@app.get("/clients/{client_id}")
def get_client(client_id: int):
    clients = read_clients()
    client = next((c for c in clients if c['id'] == client_id), None)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@app.post("/clients")
def create_client(client: Client):
    clients = read_clients()
    if client.id is None:
        client.id = max([c['id'] for c in clients], default=0) + 1
    else:
        if any(c['id'] == client.id for c in clients):
            raise HTTPException(status_code=400, detail="Client with this ID already exists")
    clients.append(client.dict())
    write_clients(clients)
    return client

@app.put("/clients/{client_id}")
def update_client(client_id: int, updated_client: Client):
    clients = read_clients()
    for i, client in enumerate(clients):
        if client['id'] == client_id:
            updated_client.id = client_id  # keep the id
            clients[i] = updated_client.dict()
            write_clients(clients)
            return updated_client
    raise HTTPException(status_code=404, detail="Client not found")

@app.delete("/clients/{client_id}")
def delete_client(client_id: int):
    clients = read_clients()
    for i, client in enumerate(clients):
        if client['id'] == client_id:
            del clients[i]
            write_clients(clients)
            return {"message": "Client deleted"}
    raise HTTPException(status_code=404, detail="Client not found")


@app.post("/accept_prompt")
def accept_prompt(payload: PromptRequest):
    conversations = read_conversations()

    conversation_id = str(max((int(k) for k in conversations.keys()), default=0) + 1)
    conversations[conversation_id] = []

    conversations[conversation_id].append({
        "role": "user",
        "content": payload.user_question,
    })

    default_reply = "réponse par défaut, pas encore de LLM connecté"
    conversations[conversation_id].append({
        "role": "assistant",
        "content": default_reply,
    })

    write_conversations(conversations)

    return {"response": default_reply}


@app.get("/prompts/{id}")
def get_historical(id: int):
    conversations = read_conversations()
    historical = []
    for key in sorted(conversations.keys(), key=lambda x: int(x)):
        conversation_id = int(key)
        if conversation_id > id:
            break
        messages = conversations.get(key, [])
        if not messages:
            continue
        historical.append({
            "conversation_id": conversation_id,
            "messages": messages,
        })

    return {"prompts": historical}