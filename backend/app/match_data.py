import json
from backend.app.config import settings

# Load the JSON file
def load_match_data(file_path=None):
    if file_path is None:
        file_path = 'backend/app/data/football_updates.json' if settings.SPORT_TYPE == "football" else 'backend/app/data/cricket_updates.json'
    with open(file_path, 'r') as file:
        return json.load(file)

# Filter events by type (e.g., all goals)
def get_events_by_type(data, event_type):
    return [event for event in data['events'] if event['type'] == event_type]

# Filter events by team
def get_events_by_team(data, team):
    return [event for event in data['events'] if event['team'] == team]

# Generate commentary for an event
def generate_commentary(event):
    if settings.SPORT_TYPE == "football":
        if event['type'] == 'goal':
            return f"What a goal by {event['player']}! {event['description']}"
        elif event['type'] == 'yellow_card':
            return f"{event['player']} picks up a yellow for {event['details']['reason']}. Careful now!"
        elif event['type'] == 'foul':
            return f"{event['player']} commits a foul: {event['description']}"
        elif event['type'] == 'corner':
            return f"{event['player']} takes a corner: {event['description']}"
        elif event['type'] == 'substitution':
            return f"Substitution for {event['team']}: {event['player_out']} off, {event['player_in']} on."
        elif event['type'] == 'incident':
            return event['description']
        else:
            return f"{event['type'].capitalize()} at minute {event['minute']}: {event['description']}"
    elif settings.SPORT_TYPE == "cricket":
        if event['type'] == 'wicket':
            return f"Wicket! {event['player']} is out! {event['description']}"
        elif event['type'] == 'boundary':
            return f"Four! {event['player']} plays a fantastic shot: {event['description']}"
        elif event['type'] == 'six':
            return f"Six! {event['player']} goes big: {event['description']}"
        else:
            return f"{event['type'].capitalize()} in over {event['minute']}: {event['description']}"
    else:
        return f"Unsupported sport type: {settings.SPORT_TYPE}"

# Example usage
if __name__ == "__main__":
    # Load the data
    data = load_match_data()

    # Get match info
    match_info = data['match_info']
    print(f"Match: {match_info['home_team']} vs {match_info['away_team']} on {match_info['date']}")

    # Get all goals or wickets based on sport
    if settings.SPORT_TYPE == "football":
        goals = get_events_by_type(data, 'goal')
        print("\nGoals:")
        for goal in goals:
            print(generate_commentary(goal))
    elif settings.SPORT_TYPE == "cricket":
        wickets = get_events_by_type(data, 'wicket')
        print("\nWickets:")
        for wicket in wickets:
            print(generate_commentary(wicket))