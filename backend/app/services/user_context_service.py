from backend.app.config import settings
import redis
import json

class UserContextService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )

    def get_user_context(self, phone_number):
        context = self.redis_client.get(phone_number)
        if context:
            return json.loads(context)
        return {
            "favorite_team": "Argentina",
            "favorite_player": "Lionel Messi",
            "commentary_style": "snarky"
        }

    def set_user_context(self, phone_number, context):
        self.redis_client.set(phone_number, json.dumps(context))