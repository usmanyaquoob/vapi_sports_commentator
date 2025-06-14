import json
from backend.app.models.match_event import MatchEvent
from backend.app.config import settings

class DataService:
    def __init__(self, sport_type):
        if sport_type == "football":
            self.data_path = 'backend/app/data/football_updates.json'
        elif sport_type == "cricket":
            self.data_path = 'backend/app/data/cricket_updates.json'
        else:
            raise ValueError(f"Unsupported sport_type: {sport_type}")

    def load_match_updates(self):
        with open(self.data_path, 'r') as file:
            data = json.load(file)
        return [MatchEvent(**event) for event in data['events']]

    def get_events_by_type(self, event_type):
        events = self.load_match_updates()
        return [event for event in events if event.type == event_type]

    def get_events_by_team(self, team):
        events = self.load_match_updates()
        return [event for event in events if event.team == team]