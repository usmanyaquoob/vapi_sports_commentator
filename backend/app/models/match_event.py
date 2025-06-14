from pydantic import BaseModel
from typing import Optional

class MatchEvent(BaseModel):
    minute: int
    type: str
    player: Optional[str] = None
    team: Optional[str] = None
    description: str
    details: Optional[dict] = {}