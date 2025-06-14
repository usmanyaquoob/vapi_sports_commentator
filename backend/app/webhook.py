import asyncio
import httpx
from fastapi import FastAPI, Header, Request
from pydantic import BaseModel
from backend.app.services.data_service import DataService
from backend.app.services.user_context_service import UserContextService
from backend.app.config import settings
import json

app = FastAPI()
_active_tickers = {}  # Track active tickers by call_id
current_sport_type = "football"  # Default sport type

class UserPreferences(BaseModel):
    preferred_sport: str
    favorite_team: str
    favorite_player: str
    commentary_style: str

class SavePreferencesRequest(BaseModel):
    phone_number: str
    preferences: UserPreferences

def _verify(payload: dict, sig: str | None):
    print(f"Skipping signature verification for testing. Payload: {payload}")

async def send_speak_command(control_url: str, call_id: str, message: str, is_event=False):
    headers = {"Authorization": f"Bearer {settings.VAPI_API_KEY}", "Content-Type": "application/json"}
    content = json.dumps(message) if is_event else message
    payload = {
        "type": "add-message",
        "message": {
            "role": "system",
            "content": content
        }
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(control_url, json=payload, headers=headers)
            print(f"Control URL (add-message) response: {response.status_code} - {response.text}")
            return response
        except Exception as e:
            print(f"Control URL (add-message) error: {str(e)}")
            raise

@app.get("/vapi/current-score")
async def current_score():
    global current_sport_type
    file_name = f"current_state_{current_sport_type}.json"
    file_path = f"backend/app/data/{file_name}"
    try:
        with open(file_path, 'r') as file:
            state = json.load(file)
        return {"score": state["score"]}
    except Exception as e:
        return {"error": f"Failed to fetch score: {str(e)}"}

@app.post("/save-preferences")
async def save_preferences(request: SavePreferencesRequest):
    user_context_service = UserContextService()
    user_context_service.set_user_context(request.phone_number, request.preferences.dict())
    return {"status": "success"}

@app.post("/vapi/webhook")
async def vapi_webhook(request: Request, x_vapi_signature: str | None = Header(None)):
    payload = await request.json()
    _verify(payload, x_vapi_signature)
    print(f"Received payload: {payload}")

    # Extract event type, call ID, control URL, and phone number
    message = payload.get("message", {})
    event_type = message.get("type")
    call_id = message.get("call", {}).get("id")
    control_url = message.get("call", {}).get("monitor", {}).get("controlUrl")
    status = message.get("status")
    phone_number = message.get("call", {}).get("customer", {}).get("number", "unknown")
    print(f"Event Type: {event_type}, Call ID: {call_id}, Control URL: {control_url}, Status: {status}, Phone: {phone_number}")

    # Initialize services
    user_context_service = UserContextService()

    # Handle call start or in-progress
    if event_type == "status-update" and status == "in-progress":
        print("Starting match updates")
        # Load user context
        user_context = user_context_service.get_user_context(phone_number)
        # Update global sport type
        global current_sport_type
        current_sport_type = user_context.get("preferred_sport", "football")
        # Send user preferences to the assistant
        context_message = (
            f"The user prefers {user_context['preferred_sport']} commentary, "
            f"their favorite team is {user_context['favorite_team']}, "
            f"favorite player is {user_context['favorite_player']}, "
            f"and they like {user_context['commentary_style']} commentary."
        )
        await send_speak_command(control_url, call_id, context_message)

        # Load match updates based on user's preferred sport
        sport_type = user_context.get("preferred_sport", "football")
        data_service = DataService(sport_type=sport_type)
        events = [event.dict() for event in data_service.load_match_updates()]

        # Store events, index, and control URL for this call
        _active_tickers[call_id] = {"events": events, "index": 0, "control_url": control_url}

        # Start ticker to send updates every 30 seconds
        async def ticker():
            while call_id in _active_tickers:
                ticker_data = _active_tickers[call_id]
                if ticker_data["index"] < len(ticker_data["events"]):
                    event = ticker_data["events"][ticker_data["index"]]
                    print(f"Attempting to send update: {event}")
                    await send_speak_command(control_url, call_id, event, is_event=True)
                    ticker_data["index"] += 1  # Move to the next event
                else:
                    print("All match updates have been sent.")
                    break
                await asyncio.sleep(30)  # Wait 30 seconds before the next update
        asyncio.create_task(ticker())

    # Stop ticker on call end
    if event_type == "status-update" and status == "ended":
        print(f"Stopping ticker for call {call_id}")
        _active_tickers.pop(call_id, None)

    return {"status": "success"}