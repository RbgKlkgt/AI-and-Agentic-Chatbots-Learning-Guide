import csv
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Client(BaseModel):
    id: Optional[int] = None
    first_name: str
    last_name: str
    account: int

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