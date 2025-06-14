from fastapi import FastAPI
from backend.app.services.data_service import DataService
import json

app = FastAPI()
data_service = DataService()

@app.get("/match-updates")
async def match_updates():
    updates = [event.dict() for event in data_service.load_match_updates()]
    return {"updates": updates}

@app.get("/vapi/current-score")
async def current_score():
    with open('backend/app/data/current_state.json', 'r') as file:
        state = json.load(file)
    return {"score": state["score"]}