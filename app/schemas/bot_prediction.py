from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BotPrediction(BaseModel):
    id: str
    name: str
    username: str
    created_at: datetime
    followers_count: int
    followings_count: int
    verified: bool
    avatar: str
    banner: Optional[str]
